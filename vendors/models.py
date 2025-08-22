from django.db import models
from users.models import User

# Create your models here.

class Vendor(models.Model):
    TYPE_CHOICES = [
        ('restaurant', 'Restaurant'),
        ('store', 'Store'),
        ('cafe', 'Cafe'),
    ]
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_vendors')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='vendor_logos/', null=True, blank=True)
    rating = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class Branch(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=200)
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    phone = models.CharField(max_length=20)
    opening_hours = models.JSONField(default=dict)  # {"monday": "09:00-22:00", ...}
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vendor.name} - {self.name}"