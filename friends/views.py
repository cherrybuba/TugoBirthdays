from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from .models import Group, GroupMembership, Friendship
from notifications.models import Notification, NotificationSubscription, GroupNotificationSubscription


@login_required
def friend_list(request):
    friendships = Friendship.objects.filter(
        from_user=request.user, status=Friendship.STATUS_ACCEPTED
    ).select_related('to_user', 'to_user__profile')
    friends = [f.to_user for f in friendships]

    incoming = Friendship.objects.filter(
        to_user=request.user, status=Friendship.STATUS_PENDING
    ).select_related('from_user', 'from_user__profile')
    pending_requests = [f.from_user for f in incoming]

    subs = NotificationSubscription.objects.filter(
        subscriber=request.user
    ).select_related('friend', 'friend__profile')
    subscribed_friends = [s.friend for s in subs]

    return render(request, 'friends/friend_list.html', {
        'friends': friends,
        'pending_requests': pending_requests,
        'subscribed_friends': subscribed_friends,
    })


@login_required
def friend_search(request):
    query = request.GET.get('q', '')
    users = User.objects.exclude(id=request.user.id)
    if query:
        users = users.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(username__icontains=query)
        )
    users = users.select_related('profile')[:50]
    friend_ids = Friendship.objects.filter(
        from_user=request.user, status=Friendship.STATUS_ACCEPTED
    ).values_list('to_user_id', flat=True)
    pending_ids = Friendship.objects.filter(
        from_user=request.user, status=Friendship.STATUS_PENDING
    ).values_list('to_user_id', flat=True)
    return render(request, 'friends/friend_search.html', {
        'users': users,
        'query': query,
        'friend_ids': list(friend_ids),
        'pending_ids': list(pending_ids),
    })


@login_required
def friend_add(request, user_id):
    target = get_object_or_404(User, id=user_id)
    if target == request.user:
        messages.error(request, 'Нельзя добавить себя в друзья.')
        return redirect('friends:friend_list')
    exists = Friendship.objects.filter(
        Q(from_user=request.user, to_user=target) | Q(from_user=target, to_user=request.user)
    ).exists()
    if exists:
        messages.info(request, 'Заявка уже существует.')
        return redirect('friends:friend_list')
    Friendship.objects.create(from_user=request.user, to_user=target)
    sender_name = request.user.get_full_name() or request.user.username
    Notification.objects.create(
        user=target,
        message=f'{sender_name} хочет добавить вас в друзья',
    )
    messages.success(request, f'Заявка отправлена {target.get_full_name() or target.username}.')
    return redirect('friends:friend_list')


@login_required
def friend_accept(request, user_id):
    target = get_object_or_404(User, id=user_id)
    friendship = get_object_or_404(Friendship, from_user=target, to_user=request.user, status=Friendship.STATUS_PENDING)
    friendship.status = Friendship.STATUS_ACCEPTED
    friendship.save()
    Friendship.objects.get_or_create(from_user=request.user, to_user=target, defaults={'status': Friendship.STATUS_ACCEPTED})
    sender_name = request.user.get_full_name() or request.user.username
    Notification.objects.create(
        user=target,
        message=f'{sender_name} принял вашу заявку в друзья',
    )
    messages.success(request, f'{target.get_full_name() or target.username} добавлен в друзья.')
    return redirect('friends:friend_list')


@login_required
def friend_reject(request, user_id):
    target = get_object_or_404(User, id=user_id)
    Friendship.objects.filter(from_user=target, to_user=request.user, status=Friendship.STATUS_PENDING).delete()
    messages.info(request, f'Заявка от {target.get_full_name() or target.username} отклонена.')
    return redirect('friends:friend_list')


@login_required
def friend_remove(request, user_id):
    target = get_object_or_404(User, id=user_id)
    Friendship.objects.filter(from_user=request.user, to_user=target).delete()
    Friendship.objects.filter(from_user=target, to_user=request.user).delete()
    messages.success(request, f'{target.get_full_name() or target.username} удалён из друзей.')
    return redirect('friends:friend_list')


@login_required
def group_list(request):
    memberships = GroupMembership.objects.filter(
        user=request.user
    ).select_related('group')
    groups = [m.group for m in memberships]

    subs = GroupNotificationSubscription.objects.filter(
        subscriber=request.user
    ).select_related('group')
    subscribed_groups = [s.group for s in subs]

    return render(request, 'friends/group_list.html', {
        'groups': groups,
        'subscribed_groups': subscribed_groups,
    })


@login_required
def group_search(request):
    query = request.GET.get('q', '')
    groups = Group.objects.all()
    if query:
        groups = groups.filter(Q(name__icontains=query) | Q(description__icontains=query))
    groups = groups[:50]
    user_group_ids = GroupMembership.objects.filter(
        user=request.user
    ).values_list('group_id', flat=True)
    return render(request, 'friends/group_search.html', {
        'groups': groups,
        'query': query,
        'user_group_ids': list(user_group_ids),
    })


@login_required
def group_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        if name:
            group = Group.objects.create(name=name, description=description, created_by=request.user)
            GroupMembership.objects.create(group=group, user=request.user)
            messages.success(request, f'Группа "{name}" создана.')
            return redirect('friends:group_detail', group.id)
        messages.error(request, 'Название группы обязательно.')
    return render(request, 'friends/group_form.html')


@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    memberships = GroupMembership.objects.filter(group=group).select_related('user', 'user__profile')
    members = [m.user for m in memberships]
    is_member = GroupMembership.objects.filter(group=group, user=request.user).exists()
    is_subscribed = GroupNotificationSubscription.objects.filter(
        subscriber=request.user, group=group
    ).exists()
    return render(request, 'friends/group_detail.html', {
        'group': group,
        'members': members,
        'is_member': is_member,
        'is_subscribed': is_subscribed,
    })


@login_required
def group_join(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    GroupMembership.objects.get_or_create(group=group, user=request.user)
    messages.success(request, f'Вы вступили в группу "{group.name}".')
    return redirect('friends:group_detail', group.id)


@login_required
def group_leave(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    GroupMembership.objects.filter(group=group, user=request.user).delete()
    messages.success(request, f'Вы вышли из группы "{group.name}".')
    return redirect('friends:group_list')


@login_required
def group_delete(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if group.created_by != request.user:
        messages.error(request, 'Только создатель может удалить группу.')
        return redirect('friends:group_detail', group.id)
    name = group.name
    group.delete()
    messages.success(request, f'Группа "{name}" удалена.')
    return redirect('friends:group_list')
