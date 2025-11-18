from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Order, OrderItem, Coupon, OrderCoupon


class OrderItemInline(admin.TabularInline):
    """Inline para mostrar items de orden en el admin"""
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'subtotal', 'created_at')
    fields = ('product', 'quantity', 'price', 'subtotal', 'created_at')
    can_delete = False

    def subtotal(self, obj):
        """Muestra el subtotal del item"""
        return f"${obj.subtotal:,.0f}"
    subtotal.short_description = _("Subtotal")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin para gestionar órdenes"""
    list_display = ('order_number', 'user', 'status', 'total', 'total_items', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__email')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'total_items')
    inlines = [OrderItemInline]
    
    fieldsets = (
        (_("Información Básica"), {
            'fields': ('order_number', 'user', 'status', 'total', 'total_items')
        }),
        (_("Dirección de Envío"), {
            'fields': ('shipping_address', 'shipping_city', 'shipping_postal_code')
        }),
        (_("Información Adicional"), {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )

    def total_items(self, obj):
        """Muestra el total de items en la orden"""
        return obj.total_items
    total_items.short_description = _("Total Items")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin para gestionar items de orden"""
    list_display = ('order', 'product', 'quantity', 'price', 'subtotal', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('order__order_number', 'product__name', 'product__sku')
    readonly_fields = ('subtotal', 'created_at')

    def subtotal(self, obj):
        """Muestra el subtotal del item"""
        return f"${obj.subtotal:,.0f}"
    subtotal.short_description = _("Subtotal")


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """Admin para gestionar cupones"""
    list_display = ('code', 'discount_type', 'discount_value', 'is_active', 'used_count', 'usage_limit', 'valid_from', 'valid_to')
    list_filter = ('is_active', 'discount_type', 'valid_from', 'valid_to')
    search_fields = ('code',)
    readonly_fields = ('used_count', 'created_at', 'updated_at')
    
    fieldsets = (
        (_("Información Básica"), {
            'fields': ('code', 'discount_type', 'discount_value', 'is_active')
        }),
        (_("Vigencia"), {
            'fields': ('valid_from', 'valid_to')
        }),
        (_("Límites de Uso"), {
            'fields': ('usage_limit', 'used_count')
        }),
        (_("Fechas"), {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(OrderCoupon)
class OrderCouponAdmin(admin.ModelAdmin):
    """Admin para ver cupones aplicados a órdenes"""
    list_display = ('order', 'coupon', 'discount_amount', 'applied_at')
    list_filter = ('applied_at',)
    search_fields = ('order__order_number', 'coupon__code')
    readonly_fields = ('applied_at',)
