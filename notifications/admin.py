from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Notification, NotificationSubscription, GroupNotificationSubscription


class NotificationResource(resources.ModelResource):
    class Meta:
        model = Notification
        import_id_fields = ['id']
        fields = ('id', 'user', 'message', 'birthday_user', 'is_read', 'created_at')


class NotificationSubscriptionResource(resources.ModelResource):
    class Meta:
        model = NotificationSubscription
        import_id_fields = ['id']
        fields = ('id', 'subscriber', 'friend', 'days_before')


class GroupNotificationSubscriptionResource(resources.ModelResource):
    class Meta:
        model = GroupNotificationSubscription
        import_id_fields = ['id']
        fields = ('id', 'subscriber', 'group', 'days_before')


@admin.register(Notification)
class NotificationAdmin(ImportExportModelAdmin):
    resource_class = NotificationResource
    list_display = ['user', 'message', 'is_read', 'created_at']
    list_filter = ['is_read']


@admin.register(NotificationSubscription)
class NotificationSubscriptionAdmin(ImportExportModelAdmin):
    resource_class = NotificationSubscriptionResource
    list_display = ['subscriber', 'friend', 'days_before']


@admin.register(GroupNotificationSubscription)
class GroupNotificationSubscriptionAdmin(ImportExportModelAdmin):
    resource_class = GroupNotificationSubscriptionResource
    list_display = ['subscriber', 'group', 'days_before']
