from django.urls import path
from . import views

app_name = 'riders'

urlpatterns = [
    # Rider authentication
    path('login/', views.rider_login, name='rider_login'),
    path('register/', views.rider_register, name='rider_register'),
    
    # Rider profile management
    path('profile/', views.get_rider_profile, name='get_rider_profile'),
    path('profile/create/', views.create_rider_profile, name='create_rider_profile'),
    path('toggle-online/', views.toggle_online_status, name='toggle_online_status'),
    
    # Order management
    path('available-orders/', views.get_available_orders, name='get_available_orders'),
    path('active-orders/', views.get_active_orders, name='get_active_orders'),
    path('accept-order/<int:order_id>/', views.accept_order, name='accept_order'),
    path('update-delivery/<uuid:assignment_id>/', views.update_delivery_status, name='update_delivery_status'),
    
    # Analytics
    path('earnings/', views.get_rider_earnings, name='get_rider_earnings'),
    path('delivery-history/', views.get_delivery_history, name='get_delivery_history'),
]
