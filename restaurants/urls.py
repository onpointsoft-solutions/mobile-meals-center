from django.urls import path
from . import views
from . import views_payment

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
]
