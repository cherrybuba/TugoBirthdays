from django.urls import path
from . import views

app_name = 'gifts'

urlpatterns = [
    path('wishlist/add/', views.wishlist_add, name='wishlist_add'),
    path('wishlist/<int:item_id>/edit/', views.wishlist_edit, name='wishlist_edit'),
    path('wishlist/<int:item_id>/delete/', views.wishlist_delete, name='wishlist_delete'),
    path('wishlist/<int:item_id>/purchase/', views.wishlist_purchase, name='wishlist_purchase'),
    path('wishlist/<int:item_id>/unreserve/', views.wishlist_unreserve, name='wishlist_unreserve'),
    path('discussion/<int:user_id>/', views.discussion, name='discussion'),
    path('discussion/<int:user_id>/send/', views.discussion_send, name='discussion_send'),
    path('discussion/<int:user_id>/stream/', views.discussion_stream, name='discussion_stream'),
]
