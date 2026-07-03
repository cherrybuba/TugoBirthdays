from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, StreamingHttpResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Notification, NotificationSubscription, GroupNotificationSubscription
from friends.models import Group, GroupMembership
import json
import time

RANGES = [(6, 7), (4, 5), (2, 3), (0, 1)]


def _check_and_notify(subscriber, friend):
    if not hasattr(friend, 'profile') or not friend.profile.birthday:
        return
    today = timezone.now().date()
    bd = friend.profile.birthday
    this_year = bd.replace(year=today.year)
    if this_year < today:
        this_year = bd.replace(year=today.year + 1)
    days = (this_year - today).days

    for min_d, max_d in RANGES:
        if min_d <= days <= max_d:
            name = friend.get_full_name() or friend.username
            if days == 1:
                msg = f'Завтра день рождения у {name}!'
            elif days == 0:
                msg = f'Сегодня день рождения у {name}! Не забудьте поздравить!'
            else:
                plural = 'день' if days % 10 == 1 and days % 100 != 11 else ('дня' if days % 10 in (2, 3, 4) and days % 100 not in (12, 13, 14) else 'дней')
                msg = f'Через {days} {plural} день рождения у {name}!'

            exists = Notification.objects.filter(
                user=subscriber, birthday_user=friend, message=msg, created_at__year=today.year
            ).exists()
            if not exists:
                Notification.objects.create(user=subscriber, birthday_user=friend, message=msg)
            break


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user)
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications,
    })


@login_required
@require_POST
def notification_read(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.is_read = True
    notif.save()
    return JsonResponse({'status': 'ok'})


@login_required
@require_POST
def notification_delete(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.delete()
    return JsonResponse({'status': 'ok'})


@login_required
@require_POST
def subscribe_user(request, user_id):
    friend = get_object_or_404(User, id=user_id)
    sub, created = NotificationSubscription.objects.get_or_create(
        subscriber=request.user, friend=friend
    )
    if not created:
        sub.delete()
        return JsonResponse({'subscribed': False})
    _check_and_notify(request.user, friend)
    return JsonResponse({'subscribed': True})


@login_required
@require_POST
def subscribe_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    sub, created = GroupNotificationSubscription.objects.get_or_create(
        subscriber=request.user, group=group
    )
    if not created:
        sub.delete()
        return JsonResponse({'subscribed': False})
    members = User.objects.filter(groupmembership__group=group)
    for member in members:
        if member != request.user:
            _check_and_notify(request.user, member)
    return JsonResponse({'subscribed': True})


@login_required
def notification_stream(request):
    last_id = int(request.GET.get('last_id', 0))

    def event_stream():
        current_id = last_id
        while True:
            new_notifs = Notification.objects.filter(
                user=request.user, id__gt=current_id
            )
            for n in new_notifs:
                data = json.dumps({
                    'id': n.id,
                    'message': n.message,
                    'is_read': n.is_read,
                    'created_at': n.created_at.strftime('%d.%m.%Y %H:%M'),
                })
                yield f'id: {n.id}\ndata: {data}\n\n'
                current_id = n.id
            time.sleep(2)

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response
