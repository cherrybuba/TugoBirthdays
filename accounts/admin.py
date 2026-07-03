from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Profile


class ProfileResource(resources.ModelResource):
    class Meta:
        model = Profile
        import_id_fields = ['id']
        fields = ('id', 'user', 'birthday')


@admin.register(Profile)
class ProfileAdmin(ImportExportModelAdmin):
    resource_class = ProfileResource
    list_display = ['user', 'birthday']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
