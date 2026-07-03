from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile_view_self, name='profile_edit'),
    path('profile/edit/', views.profile_edit, name='profile_edit_form'),
    path('profile/<int:user_id>/', views.profile_view, name='profile_view'),
]
