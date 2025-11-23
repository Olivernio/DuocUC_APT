# Vistas de Catálogo - PetStorePOS

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.core.paginator import Paginator
import logging
from .models import Product, Category, ProductReview
from .forms import ProductForm, ReviewForm

logger = logging.getLogger(__name__)

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
         return self.request.user.is_staff

class ProductListView(ListView):
    model = Product
    template_name = "catalog/list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        search_query = self.request.GET.get('q', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(sku__icontains=search_query)
            )
        category = self.request.GET.get('cat', '').strip()
        if category:
            queryset = queryset.filter(category=category)
        queryset = queryset.order_by('name')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = [
            {'pk': choice[0], 'name': choice[1]} 
            for choice in Category.choices
        ]
        context['category_selected'] = self.request.GET.get('cat', '')
        context['search_query'] = self.request.GET.get('q', '')
        page_obj = context.get('page_obj')
        if page_obj and hasattr(page_obj, 'paginator'):
            context['paginator_info'] = {
                'current_page': page_obj.number,
                'total_pages': page_obj.paginator.num_pages,
                'total_items': page_obj.paginator.count,
                'items_per_page': self.paginate_by,
                'start_index': page_obj.start_index(),
                'end_index': page_obj.end_index(),
            }
        return context

class ProductCreateView(CreateView): 
    model = Product
    form_class = ProductForm              
    template_name = "catalog/form.html"
    success_url = reverse_lazy("catalog:product_list")
    
    def get_success_url(self):
        # Primero intenta obtener 'next' del POST (si viene del formulario)
        next_url = self.request.POST.get('next')
        # Si no está en POST, intenta del GET
        if not next_url:
            next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return super().get_success_url()

class ProductUpdateView(UpdateView): 
    model = Product
    form_class = ProductForm
    template_name = "catalog/form.html"
    success_url = reverse_lazy("catalog:product_list")
    
    def get_success_url(self):
        # Primero intenta obtener 'next' del POST (si viene del formulario)
        next_url = self.request.POST.get('next')
        # Si no está en POST, intenta del GET
        if not next_url:
            next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return super().get_success_url()

class ProductDeleteView(DeleteView): 
    model = Product
    template_name = "catalog/confirm_delete.html"
    success_url = reverse_lazy("catalog:product_list")
    
    def get_success_url(self):
        # Primero intenta obtener 'next' del POST (si viene del formulario)
        next_url = self.request.POST.get('next')
        # Si no está en POST, intenta del GET
        if not next_url:
            next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return super().get_success_url()

class ProductDetailView(DetailView):
    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        approved_reviews = product.reviews.filter(is_approved=True).select_related('user')
        context['reviews'] = approved_reviews
        avg_rating = approved_reviews.aggregate(Avg('rating'))['rating__avg']
        context['avg_rating'] = round(avg_rating, 1) if avg_rating else 0
        context['total_reviews'] = approved_reviews.count()
        if self.request.user.is_authenticated:
            user_review = product.reviews.filter(user=self.request.user).first()
            context['user_review'] = user_review
            context['can_review'] = not user_review and self._user_has_purchased(product)
        else:
            context['user_review'] = None
            context['can_review'] = False
        if self.request.user.is_authenticated and context['can_review']:
            context['review_form'] = ReviewForm(user=self.request.user, product=product)
        else:
            context['review_form'] = None
        return context
    
    def _user_has_purchased(self, product):
        from orders.models import OrderItem
        return OrderItem.objects.filter(
            order__user=self.request.user,
            product=product,
            order__status__in=['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED']
        ).exists()

@login_required
def create_review(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id)
        existing_review = ProductReview.objects.filter(product=product, user=request.user).first()
        if existing_review:
            messages.warning(request, "Ya has dejado una reseña para este producto.")
            return redirect('catalog:product_detail', pk=product.id)
        if request.method == 'POST':
            form = ReviewForm(request.POST, user=request.user, product=product)
            if form.is_valid():
                try:
                    review = form.save(commit=False)
                    review.product = product
                    review.user = request.user
                    review.is_approved = False
                    review.save()
                    try:
                        from accounts.utils import notify_review_created
                        notify_review_created(request.user, review)
                    except Exception as notify_error:
                        logger.warning(f"Error al crear notificación de reseña: {str(notify_error)}")
                    messages.success(request, "¡Gracias por tu reseña! Será revisada por un administrador antes de publicarse.")
                    return redirect('catalog:product_detail', pk=product.id)
                except Exception as save_error:
                    logger.error(f"Error al guardar reseña: {str(save_error)}", exc_info=True)
                    messages.error(request, f"Error al guardar la reseña: {str(save_error)}. Por favor intenta de nuevo.")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        else:
            form = ReviewForm(user=request.user, product=product)
        approved_reviews = product.reviews.filter(is_approved=True).select_related('user')
        avg_rating = approved_reviews.aggregate(Avg('rating'))['rating__avg']
        return render(request, 'catalog/product_detail.html', {
            'product': product,
            'review_form': form,
            'reviews': approved_reviews,
            'avg_rating': round(avg_rating, 1) if avg_rating else 0,
            'total_reviews': approved_reviews.count(),
            'user_review': ProductReview.objects.filter(product=product, user=request.user).first(),
        })
    except Exception as e:
        logger.error(f"Error en create_review: {str(e)}", exc_info=True)
        messages.error(request, f"Error al procesar la reseña: {str(e)}. Por favor intenta de nuevo.")
        return redirect('catalog:product_detail', pk=product_id)
