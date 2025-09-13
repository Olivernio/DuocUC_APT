from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Product
from .forms import ProductForm

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class ProductListView(StaffRequiredMixin, ListView):
    model = Product
    template_name = "catalog/list.html"
    context_object_name = "products"

class ProductCreateView(StaffRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm              # 👈 IMPORTANTE
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
