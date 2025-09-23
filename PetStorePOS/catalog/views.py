from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Product
from .forms import ProductForm

# class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
#     def test_func(self):
#         return self.request.user.is_staff

class ProductListView(ListView): #Eliminé el parámetro StaffRequiredMixin
    model = Product
    template_name = "catalog/list.html"
    context_object_name = "products"

class ProductCreateView(CreateView): #Eliminé el parámetro StaffRequiredMixin
    model = Product
    form_class = ProductForm              # 👈 IMPORTANTE
    template_name = "catalog/form.html"
    success_url = reverse_lazy("catalog:product_list")

class ProductUpdateView(UpdateView): #Eliminé el parámetro StaffRequiredMixin
    model = Product
    form_class = ProductForm
    template_name = "catalog/form.html"
    success_url = reverse_lazy("catalog:product_list")

class ProductDeleteView(DeleteView): #Eliminé el parámetro StaffRequiredMixin
    model = Product
    template_name = "catalog/confirm_delete.html"
    success_url = reverse_lazy("catalog:product_list")
