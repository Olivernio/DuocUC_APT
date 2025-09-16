from django.contrib import admin
from .models import Product, StockMovement

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "category", "price", "stock", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("sku", "name", "description")

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("product", "delta", "note", "created_at")
    search_fields = ("product__sku", "product__name", "note")
