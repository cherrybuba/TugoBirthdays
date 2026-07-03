from django.urls import path
from . import views

app_name = 'friends'

urlpatterns = [
    path('', views.friend_list, name='friend_list'),
    path('search/', views.friend_search, name='friend_search'),
    path('add/<int:user_id>/', views.friend_add, name='friend_add'),
    path('accept/<int:user_id>/', views.friend_accept, name='friend_accept'),
    path('reject/<int:user_id>/', views.friend_reject, name='friend_reject'),
    path('remove/<int:user_id>/', views.friend_remove, name='friend_remove'),
    path('groups/', views.group_list, name='group_list'),
    path('groups/search/', views.group_search, name='group_search'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/join/', views.group_join, name='group_join'),
    path('groups/<int:group_id>/leave/', views.group_leave, name='group_leave'),
    path('groups/<int:group_id>/delete/', views.group_delete, name='group_delete'),
]
