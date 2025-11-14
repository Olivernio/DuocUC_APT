from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Order, OrderItem, OrderStatus

#Permite editar los items de una orden directamente desde la vista de la orden.
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)
    fields = ('product', 'quantity', 'price', 'subtotal')


#Configuración del admin para el modelo Order.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('order_number', 'user__username', 'user__email', 'shipping_address')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    
    fieldsets = (
        (_('Información Básica'), {
            'fields': ('order_number', 'user', 'status', 'total')
        }),
        (_('Información de Envío'), {
            'fields': ('shipping_address', 'shipping_city', 'shipping_postal_code', 'notes')
        }),
        (_('Fechas'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    #Si la orden ya existe, hacer el número de orden de solo lectura.
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Si estamos editando una orden existente
            return self.readonly_fields + ('order_number',)
        return self.readonly_fields


#Configuración del admin para el modelo OrderItem.
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'subtotal', 'created_at')
    list_filter = ('created_at', 'order__status')
    search_fields = ('order__order_number', 'product__name', 'product__sku')
    readonly_fields = ('subtotal', 'created_at')

