from django.urls import path
from . import views

app_name = 'superadmin'

urlpatterns = [
    # Authentication
    path('login/', views.SuperAdminLoginView.as_view(), name='login'),
    path('logout/', views.SuperAdminLogoutView.as_view(), name='logout'),
    
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
    
    # Complaint Management
    path('complaints/', views.ComplaintManagementView.as_view(), name='complaints'),
    path('complaints/<int:pk>/', views.ComplaintDetailView.as_view(), name='complaint_detail'),
    path('complaints/<int:pk>/update-status/', views.UpdateComplaintStatusView.as_view(), name='update_complaint_status'),
    
    # Category Management
    path('categories/', views.CategoryManagementView.as_view(), name='categories'),
    
    # System Settings
    path('settings/', views.SystemSettingsView.as_view(), name='settings'),
    
    # Activity Log
    path('activity-log/', views.ActivityLogView.as_view(), name='activity_log'),
    
    # POS Management
    path('pos/', views.POSManagementView.as_view(), name='pos_management'),
    path('pos/toggle/', views.POSToggleView.as_view(), name='pos_toggle'),
    path('pos/restaurants/', views.POSRestaurantsView.as_view(), name='pos_restaurants'),
    path('pos/sessions/', views.POSSessionsView.as_view(), name='pos_sessions'),
    
    # Financial Settings
    path('financial-settings/', views.FinancialSettingsView.as_view(), name='financial_settings'),
    
    # Rider Management
    path('riders/', views.RiderManagementView.as_view(), name='riders'),
    path('riders/<uuid:pk>/', views.RiderDetailView.as_view(), name='rider_detail'),
    path('riders/<uuid:pk>/approve/', views.ApproveRiderView.as_view(), name='approve_rider'),
    path('riders/<uuid:pk>/reject/', views.RejectRiderView.as_view(), name='reject_rider'),
    path('riders/<uuid:pk>/toggle-status/', views.ToggleRiderStatusView.as_view(), name='toggle_rider_status'),
    
    # Order Assignment
    path('order-assignment/', views.OrderAssignmentView.as_view(), name='order_assignment'),
    path('assign-order/', views.AssignOrderView.as_view(), name='assign_order'),
    path('cancel-assignment/<uuid:assignment_id>/', views.CancelAssignmentView.as_view(), name='cancel_assignment'),
    
    # SMS Management
    path('sms-dashboard/', views.SMSDashboardView.as_view(), name='sms_dashboard'),
]
