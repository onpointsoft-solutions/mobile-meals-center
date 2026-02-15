from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'order', 'user', 'amount', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('id', 'order__id', 'user__username', 'paystack_reference')
    readonly_fields = ('id', 'paystack_reference', 'paystack_transaction_id', 'created_at', 'updated_at', 'paid_at')
    
    def payment_id(self, obj):
        return obj.payment_id
    payment_id.short_description = 'Payment ID'
