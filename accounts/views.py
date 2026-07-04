from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib import messages
from .forms import RegistrationForm, ProfileForm, ProfileDetailForm
from friends.models import GroupMembership, Friendship
from gifts.models import WishlistItem
from notifications.models import NotificationSubscription


def home(request):
    if not request.user.is_authenticated:
        return render(request, 'accounts/home_landing.html')

    friends = Friendship.objects.filter(
        from_user=request.user, status=Friendship.STATUS_ACCEPTED
    ).select_related('to_user', 'to_user__profile')

    friend_profiles = [f.to_user for f in friends]

    from django.utils import timezone
    today = timezone.now().date()
    upcoming = []

    for u in friend_profiles:
        if hasattr(u, 'profile') and u.profile.birthday:
            bd = u.profile.birthday
            try:
                this_year_bd = bd.replace(year=today.year)
            except ValueError:
                this_year_bd = bd.replace(year=today.year, day=28)
            if this_year_bd < today:
                try:
                    this_year_bd = bd.replace(year=today.year + 1)
                except ValueError:
                    this_year_bd = bd.replace(year=today.year + 1, day=28)
            days_until = (this_year_bd - today).days
            if 0 <= days_until <= 30:
                upcoming.append((days_until, u))

    upcoming.sort(key=lambda x: x[0])

    return render(request, 'accounts/home.html', {
        'upcoming_birthdays': upcoming,
    })


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Добро пожаловать!')
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_edit(request):
    user_form = ProfileForm(instance=request.user)
    profile_form = ProfileDetailForm(instance=request.user.profile)

    if request.method == 'POST':
        user_form = ProfileForm(request.POST, instance=request.user)
        profile_form = ProfileDetailForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль обновлён.')
            return redirect('accounts:profile_view', request.user.id)

    return render(request, 'accounts/profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


@login_required
def profile_view_self(request):
    return redirect('accounts:profile_view', request.user.id)


def profile_view(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    groups = GroupMembership.objects.filter(user=profile_user).select_related('group')
    wishlist = WishlistItem.objects.filter(user=profile_user).select_related('purchased_by')

    is_owner = request.user.is_authenticated and request.user == profile_user

    friendship_status = None
    is_friend = False
    is_subscribed = False
    if request.user.is_authenticated and request.user != profile_user:
        friendship = Friendship.objects.filter(
            Q(from_user=request.user, to_user=profile_user) | Q(from_user=profile_user, to_user=request.user)
        ).first()
        if friendship:
            friendship_status = friendship.status
            is_friend = friendship.status == Friendship.STATUS_ACCEPTED

        is_subscribed = NotificationSubscription.objects.filter(
            subscriber=request.user, friend=profile_user
        ).exists()

    return render(request, 'accounts/profile_view.html', {
        'profile_user': profile_user,
        'groups': groups,
        'wishlist': wishlist,
        'is_owner': is_owner,
        'is_friend': is_friend,
        'friendship_status': friendship_status,
        'is_subscribed': is_subscribed,
    })


def custom_logout(request):
    logout(request)
    return redirect('home')
