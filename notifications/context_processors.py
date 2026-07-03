from .models import Notification


def unread_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        last_notif = Notification.objects.filter(user=request.user).order_by('-id').first()
        last_id = last_notif.id if last_notif else 0
        return {'unread_count': count, 'last_notif_id': last_id}
    return {}
