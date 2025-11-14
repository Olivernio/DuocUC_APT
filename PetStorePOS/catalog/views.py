from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Product, Category
from .forms import ProductForm, ProductSearchForm


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
