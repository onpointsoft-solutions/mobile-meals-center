from django.urls import path
from . import views

app_name = 'superadmin'

urlpatterns = [
    # Dashboard
    path('', views.AdminDashboardView.as_view(), name='dashboard'),
    
    # Restaurant Management
    path('restaurants/', views.RestaurantManagementView.as_view(), name='restaurants'),
    path('restaurants/<int:pk>/', views.RestaurantDetailAdminView.as_view(), name='restaurant_detail'),
    path('restaurants/<int:pk>/toggle-status/', views.ToggleRestaurantStatusView.as_view(), name='toggle_restaurant_status'),
    
    # User Management
    path('users/', views.UserManagementView.as_view(), name='users'),
    path('users/<int:pk>/toggle-status/', views.ToggleUserStatusView.as_view(), name='toggle_user_status'),
    
    # Order Management
    path('orders/', views.OrderManagementView.as_view(), name='orders'),
    
    # Category Management
    path('categories/', views.CategoryManagementView.as_view(), name='categories'),
    
    # System Settings
    path('settings/', views.SystemSettingsView.as_view(), name='settings'),
    
    # Activity Log
    path('activity-log/', views.ActivityLogView.as_view(), name='activity_log'),
]
