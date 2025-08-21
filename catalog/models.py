from django.db import models

# Create your models here.
from vendors.models import Vendor, Branch
from users.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.ImageField(upload_to='category_icons/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Item(models.Model):
    UNIT_CHOICES = [
        ('pcs', 'Pieces'),
        ('kg', 'Kilograms'),
        ('portion', 'Portion'),
        ('liter', 'Liter'),
    ]
    
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='items')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='items')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='pcs')
    tags = models.JSONField(default=list)  # ["halal", "vegetarian", ...]
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='item_images/')
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

class Offer(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('sold_out', 'Sold Out'),
        ('expired', 'Expired'),
    ]
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='offers')
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    vat_percent = models.FloatField(default=0.0)
    discount_percent = models.FloatField()
    quantity_available = models.PositiveIntegerField()
    expires_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.item.title} - {self.discount_percent}% off"

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at