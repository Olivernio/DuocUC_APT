from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
from .models import Product, Category, ProductReview
from .forms import ProductForm, ProductSearchForm, ReviewForm


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
         return self.request.user.is_staff

class ProductListView(ListView):
    model = Product
    template_name = "catalog/list.html"
    context_object_name = "products"
    paginate_by = 12  # 12 productos por página

    def get_queryset(self):
        """
        Aplica filtros de búsqueda avanzada a los productos.
        """
        queryset = super().get_queryset().filter(is_active=True)
        
        # Si es staff, mostrar todos los productos (activos e inactivos)
        if self.request.user.is_staff:
            queryset = super().get_queryset()
        
        # 1. BÚSQUEDA POR TEXTO (nombre, descripción, SKU)
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |  # Busca en nombre (sin importar mayúsculas)
                Q(description__icontains=search_query) |  # Busca en descripción
                Q(sku__icontains=search_query)  # Busca en SKU
            )
        
        # 2. FILTRO POR CATEGORÍA (compatibilidad con 'cat' y 'category')
        category = self.request.GET.get('category') or self.request.GET.get('cat')
        if category:
            queryset = queryset.filter(category=category)
        
        # 3. FILTRO POR PRECIO MÍNIMO
        min_price = self.request.GET.get('min_price')
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass
        
        # 4. FILTRO POR PRECIO MÁXIMO
        max_price = self.request.GET.get('max_price')
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass
        
        # 5. FILTRO POR DISPONIBILIDAD (solo si no es staff)
        if not self.request.user.is_staff:
            if self.request.GET.get('in_stock') == 'on':
                queryset = queryset.filter(stock__gt=0)
        
        # 6. ORDENAMIENTO
        order_by = self.request.GET.get('order_by', 'name')
        if order_by:
            queryset = queryset.order_by(order_by)
        else:
            queryset = queryset.order_by('name')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Formulario de búsqueda avanzada
        form = ProductSearchForm(self.request.GET)
        context['form'] = form
        
        # Mantener compatibilidad con el código existente
        context['categories'] = [
            {'pk': choice[0], 'name': choice[1]} 
            for choice in Category.choices
        ]
        
        # Obtener valores de búsqueda para mostrar en el template
        context['search_query'] = self.request.GET.get('search', '').strip()
        context['category_selected'] = self.request.GET.get('category') or self.request.GET.get('cat', '')
        
        # Obtener favoritos del usuario (si está autenticado)
        if self.request.user.is_authenticated:
            try:
                from accounts.models import UserProfile
                user_profile, created = UserProfile.objects.get_or_create(user=self.request.user)
                favorite_ids = list(user_profile.favorite_products.values_list('id', flat=True))
                context['favorite_ids'] = favorite_ids
            except:
                context['favorite_ids'] = []
        else:
            context['favorite_ids'] = []
        
        return context


class ProductCreateView(CreateView): 
    model = Product
    form_class = ProductForm              
    template_name = "catalog/form.html"
    success_url = reverse_lazy("catalog:product_list")

class ProductUpdateView(UpdateView): 
    model = Product
    form_class = ProductForm
    template_name = "catalog/form.html"
    success_url = reverse_lazy("catalog:product_list")

class ProductDeleteView(DeleteView): 
    model = Product
    template_name = "catalog/confirm_delete.html"
    success_url = reverse_lazy("catalog:product_list")


class ProductDetailView(DetailView):
    """
    Vista para mostrar el detalle de un producto con sus reseñas.
    """
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        """
        Agrega información sobre reseñas al contexto.
        """
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Reseñas aprobadas (ordenadas por fecha, más recientes primero)
        context['reviews'] = product.reviews.filter(is_approved=True).order_by('-created_at')
        
        # Promedio de calificaciones y total de reseñas
        context['average_rating'] = product.get_average_rating()
        context['total_reviews'] = product.get_total_reviews()
        
        # Verificar si el usuario puede dejar una reseña
        context['can_review'] = False
        if self.request.user.is_authenticated:
            # Verificar si el usuario ha comprado el producto
            from orders.models import OrderItem
            has_purchased = OrderItem.objects.filter(
                order__user=self.request.user,
                product=product
            ).exists()
            
            # Verificar si ya dejó una reseña
            has_reviewed = product.reviews.filter(user=self.request.user).exists()
            
            # Solo puede reseñar si compró el producto y no ha reseñado antes
            context['can_review'] = has_purchased and not has_reviewed
        
        # Formulario de reseña (para mostrar en el template)
        context['review_form'] = ReviewForm()
        
        return context


@login_required
def create_review(request, product_id):
    """
    Vista para crear una reseña de un producto.
    Solo usuarios que hayan comprado el producto pueden reseñarlo.
    """
    product = get_object_or_404(Product, id=product_id)
    
    # Verificar que el usuario haya comprado el producto
    from orders.models import OrderItem
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        product=product
    ).exists()
    
    if not has_purchased:
        messages.error(request, _("Debes haber comprado este producto para poder reseñarlo."))
        return redirect('catalog:product_detail', pk=product.id)
    
    # Verificar si ya dejó una reseña
    if ProductReview.objects.filter(product=product, user=request.user).exists():
        messages.warning(request, _("Ya has dejado una reseña para este producto."))
        return redirect('catalog:product_detail', pk=product.id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.is_approved = False  # Requiere aprobación del administrador
            review.save()
            
            messages.success(request, _("Tu reseña ha sido enviada y será revisada por un administrador antes de publicarse."))
            return redirect('catalog:product_detail', pk=product.id)
    else:
        form = ReviewForm()
    
    # Si hay errores, mostrar el formulario nuevamente
    context = {
        'product': product,
        'review_form': form,
        'reviews': product.reviews.filter(is_approved=True).order_by('-created_at'),
        'average_rating': product.get_average_rating(),
        'total_reviews': product.get_total_reviews(),
        'can_review': True,  # Ya verificamos que puede reseñar
    }
    return render(request, 'catalog/product_detail.html', context)
