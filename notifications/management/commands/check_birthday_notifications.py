from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from notifications.models import NotificationSubscription, GroupNotificationSubscription, Notification
from friends.models import GroupMembership


RANGES = [
    (6, 7, 'Через {days} дней день рождения у {name}!'),
    (4, 5, 'Через {days} {plural} день рождения у {name}!'),
    (2, 3, 'Через {days} {plural} день рождения у {name}!'),
    (1, 1, 'Завтра день рождения у {name}!'),
    (0, 0, 'Сегодня день рождения у {name}! Не забудьте поздравить!'),
]


def day_plural(n):
    if n % 10 == 1 and n % 100 != 11:
        return 'день'
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return 'дня'
    return 'дней'


def _get_message(days, name):
    for min_d, max_d, template in RANGES:
        if min_d <= days <= max_d:
            return template.format(days=days, plural=day_plural(days), name=name)
    return None


class Command(BaseCommand):
    help = 'Генерирует уведомления о ближайших днях рождения (друзья и группы)'

    def handle(self, *args, **options):
        today = timezone.now().date()
        current_year = today.year
        created_count = 0

        # Индивидуальные подписки
        for sub in NotificationSubscription.objects.select_related('subscriber', 'friend', 'friend__profile'):
            friend = sub.friend
            if not hasattr(friend, 'profile') or not friend.profile.birthday:
                continue
            bd = friend.profile.birthday
            this_year_bd = bd.replace(year=current_year)
            if this_year_bd < today:
                this_year_bd = bd.replace(year=current_year + 1)
            days_until = (this_year_bd - today).days
            name = friend.get_full_name() or friend.username
            msg = _get_message(days_until, name)
            if msg and not Notification.objects.filter(user=sub.subscriber, birthday_user=friend, message=msg, created_at__year=current_year).exists():
                Notification.objects.create(user=sub.subscriber, birthday_user=friend, message=msg)
                created_count += 1

        # Групповые подписки
        for sub in GroupNotificationSubscription.objects.select_related('subscriber', 'group'):
            members = User.objects.filter(groupmembership__group=sub.group).select_related('profile')
            for member in members:
                if member == sub.subscriber:
                    continue
                if not hasattr(member, 'profile') or not member.profile.birthday:
                    continue
                bd = member.profile.birthday
                this_year_bd = bd.replace(year=current_year)
                if this_year_bd < today:
                    this_year_bd = bd.replace(year=current_year + 1)
                days_until = (this_year_bd - today).days
                name = member.get_full_name() or member.username
                msg = _get_message(days_until, name)
                if msg and not Notification.objects.filter(user=sub.subscriber, birthday_user=member, message=msg, created_at__year=current_year).exists():
                    Notification.objects.create(user=sub.subscriber, birthday_user=member, message=msg)
                    created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Создано уведомлений: {created_count}'))
