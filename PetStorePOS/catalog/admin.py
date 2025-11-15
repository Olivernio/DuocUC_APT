from django.contrib import admin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import Product, StockMovement, ProductReview

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "category", "price", "stock", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("sku", "name", "description")

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("product", "delta", "note", "created_at")
    search_fields = ("product__sku", "product__name", "note")

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """
    Admin para moderar reseñas de productos.
    Permite aprobar o rechazar reseñas en lote.
    """
    list_display = ('product', 'user', 'rating', 'is_approved', 'created_at', 'comment_preview')
    list_filter = ('is_approved', 'rating', 'created_at', 'product__category')
    search_fields = ('product__name', 'user__username', 'user__email', 'comment')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Información de la Reseña'), {
            'fields': ('product', 'user', 'rating', 'comment', 'is_approved', 'created_at')
        }),
    )
    
    def comment_preview(self, obj):
        """Muestra un preview del comentario (primeros 50 caracteres)"""
        if obj.comment:
            return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
        return '-'
    comment_preview.short_description = _('Comentario')
    
    actions = ['approve_reviews', 'reject_reviews']
    
    def approve_reviews(self, request, queryset):
        """
        Acción para aprobar las reseñas seleccionadas.
        """
        count = queryset.update(is_approved=True)
        self.message_user(
            request,
            _('{} reseña(s) aprobada(s) exitosamente.').format(count),
            messages.SUCCESS
        )
    approve_reviews.short_description = _('Aprobar reseñas seleccionadas')
    
    def reject_reviews(self, request, queryset):
        """
        Acción para rechazar (desaprobar) las reseñas seleccionadas.
        """
        count = queryset.update(is_approved=False)
        self.message_user(
            request,
            _('{} reseña(s) rechazada(s).').format(count),
            messages.WARNING
        )
    reject_reviews.short_description = _('Rechazar reseñas seleccionadas')
    
    def get_queryset(self, request):
        """Optimizar consultas relacionadas"""
        return super().get_queryset(request).select_related('product', 'user')
