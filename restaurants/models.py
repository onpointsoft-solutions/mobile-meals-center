from django.db import models
from django.conf import settings
from django.urls import reverse


class Restaurant(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    logo = models.ImageField(upload_to='restaurant_logos/', blank=True, null=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    pos_enabled = models.BooleanField(default=True, help_text="Enable POS system for this restaurant")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('restaurants:detail', kwargs={'pk': self.pk})


# Import payment models
from .models_payment import RestaurantPaymentProfile, RestaurantPayout, RestaurantEarning

# Import POS models
from .models_pos import POSSession, POSOrder, POSOrderItem, POSReceipt
