from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_products, name='products'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('add/', views.add_product, name='add_product'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('add-to-wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('<int:product_id>/edit_comment/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('<int:product_id>/delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('delete_rating/<int:product_id>/', views.delete_rating, name='delete_rating'),
]