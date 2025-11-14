from django.contrib import admin
from .models import UserProfile, Notification, NotificationType


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'city', 'receive_newsletter')
    list_filter = ('receive_newsletter', 'receive_adoption_alerts', 'receive_product_recommendations')
    search_fields = ('user__username', 'user__email', 'phone_number', 'city')
    filter_horizontal = ('favorite_products',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'title', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('user__username', 'user__email', 'title', 'message')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'type', 'title', 'message')
        }),
        ('Estado', {
            'fields': ('is_read', 'link', 'created_at')
        }),
    )
