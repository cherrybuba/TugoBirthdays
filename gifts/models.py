from django.db import models
from django.contrib.auth.models import User


class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist', verbose_name='Пользователь')
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    link = models.URLField('Ссылка', blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2, null=True, blank=True)
    is_purchased = models.BooleanField('Куплено', default=False)
    purchased_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='purchased_gifts', verbose_name='Купил'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Подарок из списка желаний'
        verbose_name_plural = 'Списки желаний'
        ordering = ['-created_at']


class GiftDiscussion(models.Model):
    target_user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='gift_discussion',
        verbose_name='Именинник'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Чат о подарке для {self.target_user}'

    class Meta:
        verbose_name = 'Обсуждение подарка'
        verbose_name_plural = 'Обсуждения подарков'


class GiftMessage(models.Model):
    discussion = models.ForeignKey(GiftDiscussion, on_delete=models.CASCADE, related_name='messages', verbose_name='Обсуждение')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    text = models.TextField('Текст')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author}: {self.text[:50]}'

    class Meta:
        verbose_name = 'Сообщение в чате подарка'
        verbose_name_plural = 'Сообщения в чатах подарков'
        ordering = ['created_at']
