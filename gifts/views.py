from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_POST
from .models import WishlistItem, GiftDiscussion, GiftMessage
from friends.models import Friendship
import json
import time


@login_required
def wishlist_add(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        link = request.POST.get('link', '').strip()
        price = request.POST.get('price') or None
        if title:
            WishlistItem.objects.create(
                user=request.user,
                title=title,
                description=description,
                link=link,
                price=price,
            )
            return redirect('accounts:profile_view', request.user.id)
    return render(request, 'gifts/wishlist_form.html')


@login_required
def wishlist_edit(request, item_id):
    item = get_object_or_404(WishlistItem, id=item_id, user=request.user)
    if request.method == 'POST':
        item.title = request.POST.get('title', item.title)
        item.description = request.POST.get('description', item.description)
        item.link = request.POST.get('link', item.link)
        price = request.POST.get('price')
        item.price = price if price else None
        item.save()
        return redirect('accounts:profile_view', request.user.id)
    return render(request, 'gifts/wishlist_form.html', {'item': item})


@login_required
def wishlist_delete(request, item_id):
    item = get_object_or_404(WishlistItem, id=item_id, user=request.user)
    item.delete()
    return redirect('accounts:profile_view', request.user.id)


@login_required
@require_POST
def wishlist_purchase(request, item_id):
    item = get_object_or_404(WishlistItem, id=item_id)
    is_friend = Friendship.objects.filter(
        from_user=request.user, to_user=item.user, status=Friendship.STATUS_ACCEPTED
    ).exists()
    if is_friend and not item.is_purchased:
        item.is_purchased = True
        item.purchased_by = request.user
        item.save()
        return JsonResponse({'status': 'reserved', 'by': request.user.get_full_name() or request.user.username})
    return JsonResponse({'status': 'error'}, status=400)


@login_required
@require_POST
def wishlist_unreserve(request, item_id):
    item = get_object_or_404(WishlistItem, id=item_id, purchased_by=request.user)
    item.is_purchased = False
    item.purchased_by = None
    item.save()
    return JsonResponse({'status': 'unreserved'})


def _get_or_create_discussion(target_user):
    discussion, _ = GiftDiscussion.objects.get_or_create(target_user=target_user)
    return discussion


@login_required
def discussion(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if request.user == target_user:
        return redirect('accounts:profile_view', user_id)
    is_friend = Friendship.objects.filter(
        from_user=request.user, to_user=target_user, status=Friendship.STATUS_ACCEPTED
    ).exists()
    if not is_friend:
        return redirect('accounts:profile_view', user_id)

    discussion_obj = _get_or_create_discussion(target_user)
    chat_messages = discussion_obj.messages.select_related('author').all()
    last_msg_id = chat_messages.last().id if chat_messages.exists() else 0

    return render(request, 'gifts/discussion.html', {
        'target_user': target_user,
        'chat_messages': chat_messages,
        'last_msg_id': last_msg_id,
    })


@login_required
@require_POST
def discussion_send(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if request.user == target_user:
        return JsonResponse({'error': 'Доступ запрещён'}, status=403)
    is_friend = Friendship.objects.filter(
        from_user=request.user, to_user=target_user, status=Friendship.STATUS_ACCEPTED
    ).exists()
    if not is_friend:
        return JsonResponse({'error': 'Доступ запрещён'}, status=403)

    text = request.POST.get('text', '').strip()
    if not text:
        return JsonResponse({'error': 'Пустое сообщение'}, status=400)

    discussion_obj = _get_or_create_discussion(target_user)
    msg = GiftMessage.objects.create(
        discussion=discussion_obj,
        author=request.user,
        text=text,
    )
    return JsonResponse({
        'id': msg.id,
        'author': msg.author.get_full_name() or msg.author.username,
        'text': msg.text,
        'created_at': msg.created_at.strftime('%d.%m.%Y %H:%M'),
    })


@login_required
def discussion_stream(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if request.user == target_user:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    is_friend = Friendship.objects.filter(
        from_user=request.user, to_user=target_user, status=Friendship.STATUS_ACCEPTED
    ).exists()
    if not is_friend:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    discussion_obj = _get_or_create_discussion(target_user)
    last_id = int(request.GET.get('last_id', 0))

    def event_stream():
        current_id = last_id
        while True:
            new_messages = discussion_obj.messages.filter(
                id__gt=current_id
            ).exclude(author=request.user).select_related('author')
            for msg in new_messages:
                data = json.dumps({
                    'id': msg.id,
                    'author': msg.author.get_full_name() or msg.author.username,
                    'text': msg.text,
                    'created_at': msg.created_at.strftime('%d.%m.%Y %H:%M'),
                })
                yield f'id: {msg.id}\ndata: {data}\n\n'
                current_id = msg.id
            time.sleep(1)

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response
