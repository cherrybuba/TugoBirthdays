from django.db import models
from django.contrib.auth.models import User


class Group(models.Model):
    name = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Создатель')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ['name']


class GroupMembership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, verbose_name='Группа')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Членство в группе'
        verbose_name_plural = 'Членства в группах'
        unique_together = ['group', 'user']

    def __str__(self):
        return f'{self.user} in {self.group}'


class Friendship(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Ожидает'),
        (STATUS_ACCEPTED, 'Принята'),
    ]

    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships_sent', verbose_name='От')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships_received', verbose_name='Кому')
    status = models.CharField('Статус', max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Дружба'
        verbose_name_plural = 'Дружбы'
        unique_together = ['from_user', 'to_user']

    def __str__(self):
        return f'{self.from_user} -> {self.to_user} ({self.status})'
