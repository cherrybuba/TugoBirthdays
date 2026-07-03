from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('read/<int:notif_id>/', views.notification_read, name='notification_read'),
    path('delete/<int:notif_id>/', views.notification_delete, name='notification_delete'),
    path('stream/', views.notification_stream, name='notification_stream'),
    path('subscribe/<int:user_id>/', views.subscribe_user, name='subscribe_user'),
    path('subscribe/group/<int:group_id>/', views.subscribe_group, name='subscribe_group'),
]
