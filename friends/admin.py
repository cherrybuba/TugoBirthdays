from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Group, GroupMembership, Friendship


class GroupResource(resources.ModelResource):
    class Meta:
        model = Group
        import_id_fields = ['id']
        fields = ('id', 'name', 'description', 'created_by', 'created_at')


class GroupMembershipResource(resources.ModelResource):
    class Meta:
        model = GroupMembership
        import_id_fields = ['id']
        fields = ('id', 'group', 'user', 'joined_at')


class FriendshipResource(resources.ModelResource):
    class Meta:
        model = Friendship
        import_id_fields = ['id']
        fields = ('id', 'from_user', 'to_user', 'status', 'created_at')


@admin.register(Group)
class GroupAdmin(ImportExportModelAdmin):
    resource_class = GroupResource
    list_display = ['name', 'created_by', 'created_at']
    search_fields = ['name']


@admin.register(GroupMembership)
class GroupMembershipAdmin(ImportExportModelAdmin):
    resource_class = GroupMembershipResource
    list_display = ['group', 'user', 'joined_at']


@admin.register(Friendship)
class FriendshipAdmin(ImportExportModelAdmin):
    resource_class = FriendshipResource
    list_display = ['from_user', 'to_user', 'created_at']
