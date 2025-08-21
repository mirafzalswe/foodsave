from django.contrib import admin
from django.utils.html import format_html
from .models import Vendor, Branch


class BranchInline(admin.TabularInline):
    model = Branch
    extra = 1
    fields = ('name', 'address', 'phone', 'is_active')
    show_change_link = True


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'owner', 'rating', 'is_active', 'branches_count', 'created_at')
    list_filter = ('type', 'is_active', 'rating', 'created_at')
    search_fields = ('name', 'owner__username', 'owner__email', 'description')
    ordering = ('-created_at',)
    inlines = [BranchInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('owner', 'name', 'type', 'description', 'logo')
        }),
        ('Status & Rating', {
            'fields': ('rating', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def branches_count(self, obj):
        count = obj.branches.count()
        if count > 0:
            return format_html(
                '<a href="/admin/vendors/branch/?vendor__id__exact={}">{} branches</a>',
                obj.id, count
            )
        return "0 branches"
    branches_count.short_description = "Branches"
    
    actions = ['activate_vendors', 'deactivate_vendors']
    
    def activate_vendors(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} vendors were successfully activated.')
    activate_vendors.short_description = "Activate selected vendors"
    
    def deactivate_vendors(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} vendors were successfully deactivated.')
    deactivate_vendors.short_description = "Deactivate selected vendors"


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'address', 'phone', 'is_active', 'items_count', 'created_at')
    list_filter = ('vendor__type', 'is_active', 'created_at')
    search_fields = ('name', 'vendor__name', 'address', 'phone')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('vendor', 'name', 'address', 'phone')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Operating Hours', {
            'fields': ('opening_hours',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)
    
    def items_count(self, obj):
        count = obj.items.count()
        if count > 0:
            return format_html(
                '<a href="/admin/catalog/item/?branch__id__exact={}">{} items</a>',
                obj.id, count
            )
        return "0 items"
    items_count.short_description = "Items"
    
    actions = ['activate_branches', 'deactivate_branches']
    
    def activate_branches(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} branches were successfully activated.')
    activate_branches.short_description = "Activate selected branches"
    
    def deactivate_branches(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} branches were successfully deactivated.')
    deactivate_branches.short_description = "Deactivate selected branches"
