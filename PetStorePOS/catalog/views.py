from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Product, Category
from .forms import ProductForm


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
         return self.request.user.is_staff

class ProductListView(ListView):
    model = Product
    template_name = "catalog/list.html"
    context_object_name = "products"

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.GET.get('cat')
        if category:
            queryset = queryset.filter(category=category)
        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = [
            {'pk': choice[0], 'name': choice[1]} 
            for choice in Category.choices
        ]
        context['category_selected'] = self.request.GET.get('cat', '')
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
