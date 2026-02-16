from django.urls import path
from . import views
from . import views_payment
from . import views_pos

app_name = 'restaurants'

urlpatterns = [
    path('', views.RestaurantListView.as_view(), name='list'),
    path('<int:pk>/', views.RestaurantDetailView.as_view(), name='detail'),
    path('create/', views.RestaurantCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.RestaurantUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.RestaurantDeleteView.as_view(), name='delete'),
    path('dashboard/', views.RestaurantDashboardView.as_view(), name='dashboard'),
    
    # Payment related URLs
    path('payment-profile/', views_payment.RestaurantPaymentProfileView.as_view(), name='payment_profile'),
    path('payouts/', views_payment.RestaurantPayoutListView.as_view(), name='payout_list'),
    path('payouts/<uuid:pk>/', views_payment.PayoutDetailView.as_view(), name='payout_detail'),
    path('earnings/', views_payment.RestaurantEarningListView.as_view(), name='earning_list'),
    path('initiate-payout/', views_payment.InitiatePayoutView.as_view(), name='initiate_payout'),
    path('verify-paystack-recipient/', views_payment.VerifyPaystackRecipientView.as_view(), name='verify_paystack_recipient'),
    
    # POS related URLs
    path('pos/', views_pos.POSMainView.as_view(), name='pos_main'),
    path('pos/create-order/', views_pos.POSCreateOrderView.as_view(), name='pos_create_order'),
    path('pos/add-item/', views_pos.POSAddItemView.as_view(), name='pos_add_item'),
    path('pos/remove-item/', views_pos.POSRemoveItemView.as_view(), name='pos_remove_item'),
    path('pos/complete-order/', views_pos.POSCompleteOrderView.as_view(), name='pos_complete_order'),
    path('pos/reports/', views_pos.POSReportsView.as_view(), name='pos_reports'),
    path('pos/sessions/', views_pos.POSSessionsView.as_view(), name='pos_sessions'),
    path('pos/close-session/', views_pos.POSCloseSessionView.as_view(), name='pos_close_session'),
    path('pos/receipt/<uuid:pk>/', views_pos.POSReceiptView.as_view(), name='pos_receipt'),
    path('pos/email-receipt/<uuid:pk>/', views_pos.POSEmailReceiptView.as_view(), name='pos_email_receipt'),
]
