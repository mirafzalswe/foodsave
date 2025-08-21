from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username', 'user__email')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('user', 'title', 'message', 'notification_type')
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        ('Additional Data', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('user', 'notification_type')
        return self.readonly_fields
    
    actions = ['mark_as_read', 'mark_as_unread', 'delete_old_notifications']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} notifications were marked as read.')
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} notifications were marked as unread.')
    mark_as_unread.short_description = "Mark selected notifications as unread"
    
    def delete_old_notifications(self, request, queryset):
        # Delete notifications older than 30 days
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=30)
        deleted_count = queryset.filter(created_at__lt=cutoff_date).count()
        queryset.filter(created_at__lt=cutoff_date).delete()
        self.message_user(request, f'{deleted_count} old notifications were deleted.')
    delete_old_notifications.short_description = "Delete notifications older than 30 days"
