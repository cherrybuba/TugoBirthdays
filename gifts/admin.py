from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import WishlistItem, GiftDiscussion, GiftMessage


class WishlistItemResource(resources.ModelResource):
    class Meta:
        model = WishlistItem
        import_id_fields = ['id']
        fields = ('id', 'user', 'title', 'description', 'link', 'price', 'is_purchased', 'purchased_by', 'created_at')


class GiftDiscussionResource(resources.ModelResource):
    class Meta:
        model = GiftDiscussion
        import_id_fields = ['id']
        fields = ('id', 'target_user', 'created_at')


class GiftMessageResource(resources.ModelResource):
    class Meta:
        model = GiftMessage
        import_id_fields = ['id']
        fields = ('id', 'discussion', 'author', 'text', 'created_at')


@admin.register(WishlistItem)
class WishlistItemAdmin(ImportExportModelAdmin):
    resource_class = WishlistItemResource
    list_display = ['title', 'user', 'price', 'is_purchased']
    list_filter = ['is_purchased']


@admin.register(GiftDiscussion)
class GiftDiscussionAdmin(ImportExportModelAdmin):
    resource_class = GiftDiscussionResource
    list_display = ['target_user', 'created_at']


@admin.register(GiftMessage)
class GiftMessageAdmin(ImportExportModelAdmin):
    resource_class = GiftMessageResource
    list_display = ['author', 'text', 'created_at']
