from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='list'),
    path('<uuid:pk>/', views.OrderDetailView.as_view(), name='detail'),
    path('create/', views.OrderCreateView.as_view(), name='create'),
    path('<uuid:pk>/update-status/', views.UpdateOrderStatusView.as_view(), name='update_status'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('add-to-cart/<int:meal_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('update-cart/<int:meal_id>/', views.UpdateCartView.as_view(), name='update_cart'),
    path('remove-from-cart/<int:meal_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
]
