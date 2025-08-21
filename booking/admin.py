from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('offer', 'quantity', 'price')
    readonly_fields = ('price',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'delivery_type', 'total_amount', 'payment_method', 'created_at')
    list_filter = ('status', 'delivery_type', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__email', 'delivery_address')
    ordering = ('-created_at',)
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'order_number', 'status')
        }),
        ('Delivery Details', {
            'fields': ('delivery_type', 'delivery_address', 'delivery_fee')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'total_amount')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'order_number')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('user',)
        return self.readonly_fields
    
    def save_model(self, request, obj, form, change):
        if not obj.order_number:
            # Generate order number if not exists
            import uuid
            obj.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save_model(request, obj, form, change)
    
    actions = ['mark_confirmed', 'mark_preparing', 'mark_ready', 'mark_delivered', 'mark_cancelled']
    
    def mark_confirmed(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(request, f'{updated} orders were marked as confirmed.')
    mark_confirmed.short_description = "Mark selected orders as confirmed"
    
    def mark_preparing(self, request, queryset):
        updated = queryset.filter(status='confirmed').update(status='preparing')
        self.message_user(request, f'{updated} orders were marked as preparing.')
    mark_preparing.short_description = "Mark selected orders as preparing"
    
    def mark_ready(self, request, queryset):
        updated = queryset.filter(status='preparing').update(status='ready')
        self.message_user(request, f'{updated} orders were marked as ready.')
    mark_ready.short_description = "Mark selected orders as ready"
    
    def mark_delivered(self, request, queryset):
        updated = queryset.filter(status__in=['ready', 'in_transit']).update(status='delivered')
        self.message_user(request, f'{updated} orders were marked as delivered.')
    mark_delivered.short_description = "Mark selected orders as delivered"
    
    def mark_cancelled(self, request, queryset):
        updated = queryset.exclude(status__in=['delivered', 'cancelled']).update(status='cancelled')
        self.message_user(request, f'{updated} orders were marked as cancelled.')
    mark_cancelled.short_description = "Mark selected orders as cancelled"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'offer_item', 'quantity', 'price', 'total_price')
    list_filter = ('order__status', 'offer__item__vendor', 'order__created_at')
    search_fields = ('order__order_number', 'offer__item__title', 'order__user__username')
    ordering = ('-order__created_at',)
    
    def offer_item(self, obj):
        return obj.offer.item.title
    offer_item.short_description = "Item"
    
    def total_price(self, obj):
        return format_html(
            '<strong>${:.2f}</strong>',
            obj.price * obj.quantity
        )
    total_price.short_description = "Total"
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return ('order', 'offer')
        return ()
