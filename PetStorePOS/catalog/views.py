# Importaciones originales de tus compañeros
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Product, Category, ProductReview
from .forms import ProductForm, ProductSearchForm, ProductReviewForm
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from accounts.models import UserProfile
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

# --- 1. NUESTRAS IMPORTACIONES (para la API) ---
import requests
import re
import time
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
# ¡Importamos la función de traducción que acabamos de arreglar!
from core.utils import traducir_texto 
# --- Fin de Importaciones ---


# --- 2. Vistas del Catálogo ---

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
         return self.request.user.is_staff

# --- 3. CLASE LISTVIEW FUSIONADA ---
# (Código de tus compañeros + nuestra lógica de API)
class ProductListView(ListView):
    model = Product
    template_name = "catalog/list.html"
    context_object_name = "products"
    paginate_by = 12  # (de tus compañeros)

    def get_queryset(self):
        """
        Aplica filtros de búsqueda avanzada a los productos.
        (Código de tus compañeros - intacto)
        """
        queryset = super().get_queryset().filter(is_active=True)
        
        if self.request.user.is_staff:
            queryset = super().get_queryset()
        
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query) | 
                Q(sku__icontains=search_query) 
            )
        
        category = self.request.GET.get('category') or self.request.GET.get('cat')
        if category:
            queryset = queryset.filter(category=category)
        
        min_price = self.request.GET.get('min_price')
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass
        
        max_price = self.request.GET.get('max_price')
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass
        
        if not self.request.user.is_staff:
            if self.request.GET.get('in_stock') == 'on':
                queryset = queryset.filter(stock__gt=0)
        
        order_by = self.request.GET.get('order_by', 'name')
        if order_by:
            queryset = queryset.order_by(order_by)
        else:
            queryset = queryset.order_by('name')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # --- Código de tus compañeros (intacto) ---
        form = ProductSearchForm(self.request.GET)
        context['form'] = form
        context['categories'] = [
            {'pk': choice[0], 'name': choice[1]} 
            for choice in Category.choices
        ]
        context['search_query'] = self.request.GET.get('search', '').strip()
        context['category_selected'] = self.request.GET.get('category') or self.request.GET.get('cat', '')
        
        if self.request.user.is_authenticated:
            try:
                user_profile, created = UserProfile.objects.get_or_create(user=self.request.user)
                favorite_ids = list(user_profile.favorite_products.values_list('id', flat=True))
                context['favorite_ids'] = favorite_ids
            except UserProfile.DoesNotExist:
                context['favorite_ids'] = []
        else:
            context['favorite_ids'] = []
        # --- Fin del código de tus compañeros ---
        
        
        # --- 4. NUESTRA LÓGICA DE TRADUCCIÓN (inyectada) ---
        products = context.get('products') 
        current_language = self.request.LANGUAGE_CODE
        
        if products and current_language != 'es':
            print(f"--- TRADUCIENDO CATALOGO (PÁGINA {context.get('page_obj').number}) A: {current_language} ---")
            
            for product in products:
                # 1. Traducir Nombres de Producto
                if product.name:
                    # add_p_tags=False (es el valor por defecto)
                    product.name = traducir_texto(product.name, current_language) 
                
                # 2. Traducir Descripciones
                if product.description:
                    # add_p_tags=False (para que no salgan <p>)
                    product.description = traducir_texto(product.description, current_language, add_p_tags=False)
        
        # --- FIN DE LA INYECCIÓN ---

        return context

# --- Vistas de Staff (de tus compañeros, intactas) ---
class ProductCreateView(StaffRequiredMixin, CreateView): 
    model = Product
    form_class = ProductForm              
    template_name = "catalog/form.html"
    success_url = reverse_lazy("catalog:product_list")

class ProductUpdateView(StaffRequiredMixin, UpdateView): 
    model = Product
    form_class = ProductForm
    template_name = "catalog/form.html"
    success_url = reverse_lazy("catalog:product_list")

class ProductDeleteView(StaffRequiredMixin, DeleteView): 
    model = Product
    template_name = "catalog/confirm_delete.html"
    success_url = reverse_lazy("catalog:product_list")

# --- 5. VISTA DE DETALLES (FUSIONADA) ---
class ProductDetailView(DetailView):
    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = context.get('product')
        current_language = self.request.LANGUAGE_CODE

        if product and current_language != 'es':
            # 1. Traducir Nombre
            if product.name:
                product.name = traducir_texto(product.name, current_language)
            # 2. Traducir Descripción (¡YA NO QUEREMOS LAS <p>!)
            if product.description:
                product.description = traducir_texto(product.description, current_language, add_p_tags=False)
        
        # Añadimos el formulario de reseñas (de tus compañeros)
        context['review_form'] = ProductReviewForm()
        context['reviews'] = product.reviews.all().order_by('-created_at')
        return context

# --- 6. VISTAS DE RESEÑAS Y FAVORITOS (de tus compañeros, intactas) ---
@login_required
def create_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, _('¡Gracias por tu reseña!'))
            return redirect('catalog:product_detail', pk=product_id)
    
    messages.error(request, _('Hubo un error con tu reseña.'))
    return redirect('catalog:product_detail', pk=product_id)

@login_required
def add_to_favorites(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        if product in user_profile.favorite_products.all():
            user_profile.favorite_products.remove(product)
            favorited = False
        else:
            user_profile.favorite_products.add(product)
            favorited = True
        return JsonResponse({'status': 'ok', 'favorited': favorited})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def remove_from_favorites(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.favorite_products.remove(product)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

class FavoritesListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'accounts/favorites.html'
    context_object_name = 'favorite_products'

    def get_queryset(self):
        user_profile = UserProfile.objects.get(user=self.request.user)
        return user_profile.favorite_products.all()