from django.db import models
from django.contrib.auth.models import User


class NotificationSubscription(models.Model):
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notif_subscriptions', verbose_name='Подписчик')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notif_subscribers', verbose_name='Друг')
    days_before = models.IntegerField('Дней до ДР', default=7)

    class Meta:
        verbose_name = 'Подписка на уведомления'
        verbose_name_plural = 'Подписки на уведомления'
        unique_together = ['subscriber', 'friend']

    def __str__(self):
        return f'{self.subscriber} -> {self.friend}'


class GroupNotificationSubscription(models.Model):
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_notif_subs', verbose_name='Подписчик')
    group = models.ForeignKey('friends.Group', on_delete=models.CASCADE, related_name='notif_subscribers', verbose_name='Группа')
    days_before = models.IntegerField('Дней до ДР', default=7)

    class Meta:
        verbose_name = 'Подписка на уведомления по группе'
        verbose_name_plural = 'Подписки на уведомления по группам'
        unique_together = ['subscriber', 'group']

    def __str__(self):
        return f'{self.subscriber} -> {self.group}'


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='Получатель')
    message = models.TextField('Сообщение')
    birthday_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Именинник')
    is_read = models.BooleanField('Прочитано', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Для {self.user}: {self.message[:50]}'

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']
