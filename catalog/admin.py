from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Category, Item, ItemImage, Offer


class ItemImageInline(admin.TabularInline):
    model = ItemImage
    extra = 1
    fields = ('image', 'is_primary', 'order')


class OfferInline(admin.TabularInline):
    model = Offer
    extra = 0
    fields = ('current_price', 'original_price', 'discount_percent', 'quantity_available', 'expires_at', 'status')
    readonly_fields = ('discount_percent',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'items_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    
    def items_count(self, obj):
        count = obj.item_set.count()
        if count > 0:
            return format_html(
                '<a href="/admin/catalog/item/?category__id__exact={}">{} items</a>',
                obj.id, count
            )
        return "0 items"
    items_count.short_description = "Items"


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'vendor', 'branch', 'category', 'unit', 'is_active', 'offers_count', 'created_at')
    list_filter = ('vendor__type', 'category', 'unit', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'vendor__name', 'branch__name')
    ordering = ('-created_at',)
    inlines = [ItemImageInline, OfferInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('vendor', 'branch', 'category', 'title', 'description')
        }),
        ('Details', {
            'fields': ('unit', 'tags')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def offers_count(self, obj):
        count = obj.offers.count()
        active_count = obj.offers.filter(status='available').count()
        if count > 0:
            return format_html(
                '<a href="/admin/catalog/offer/?item__id__exact={}">{} total ({} active)</a>',
                obj.id, count, active_count
            )
        return "0 offers"
    offers_count.short_description = "Offers"
    
    actions = ['activate_items', 'deactivate_items']
    
    def activate_items(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} items were successfully activated.')
    activate_items.short_description = "Activate selected items"
    
    def deactivate_items(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} items were successfully deactivated.')
    deactivate_items.short_description = "Deactivate selected items"


@admin.register(ItemImage)
class ItemImageAdmin(admin.ModelAdmin):
    list_display = ('item', 'image_preview', 'is_primary', 'order')
    list_filter = ('is_primary', 'item__vendor')
    search_fields = ('item__title', 'item__vendor__name')
    ordering = ('item', 'order')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('item', 'current_price', 'original_price', 'discount_percent', 'quantity_available', 'status', 'expires_at', 'is_expired_display')
    list_filter = ('status', 'item__vendor', 'item__category', 'expires_at')
    search_fields = ('item__title', 'item__vendor__name')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Item Information', {
            'fields': ('item',)
        }),
        ('Pricing', {
            'fields': ('current_price', 'original_price', 'vat_percent', 'discount_percent')
        }),
        ('Availability', {
            'fields': ('quantity_available', 'expires_at', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'discount_percent')
    
    def is_expired_display(self, obj):
        if obj.is_expired:
            return format_html('<span style="color: red;">Yes</span>')
        return format_html('<span style="color: green;">No</span>')
    is_expired_display.short_description = "Expired"
    
    def save_model(self, request, obj, form, change):
        # Calculate discount percentage
        if obj.original_price and obj.current_price:
            obj.discount_percent = round(((obj.original_price - obj.current_price) / obj.original_price) * 100, 2)
        super().save_model(request, obj, form, change)
    
    actions = ['mark_as_expired', 'mark_as_available', 'mark_as_sold_out']
    
    def mark_as_expired(self, request, queryset):
        updated = queryset.update(status='expired')
        self.message_user(request, f'{updated} offers were marked as expired.')
    mark_as_expired.short_description = "Mark selected offers as expired"
    
    def mark_as_available(self, request, queryset):
        updated = queryset.filter(expires_at__gt=timezone.now()).update(status='available')
        self.message_user(request, f'{updated} offers were marked as available.')
    mark_as_available.short_description = "Mark selected offers as available"
    
    def mark_as_sold_out(self, request, queryset):
        updated = queryset.update(status='sold_out')
        self.message_user(request, f'{updated} offers were marked as sold out.')
    mark_as_sold_out.short_description = "Mark selected offers as sold out"
