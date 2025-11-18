# catalog/forms.py
from django import forms
from .models import Product, ProductReview
from orders.models import Order, OrderItem

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["sku", "name", "category", "price", "stock", "description", "image", "is_active"]
        widgets = {
            "sku": forms.TextInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "stock": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ReviewForm(forms.ModelForm):
    """
    Formulario para crear/editar reseñas de productos.
    """
    class Meta:
        model = ProductReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
                'type': 'number'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Escribe tu opinión sobre este producto...'
            })
        }
        labels = {
            'rating': 'Calificación (1-5 estrellas)',
            'comment': 'Comentario'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        rating = cleaned_data.get('rating')
        
        if rating and (rating < 1 or rating > 5):
            raise forms.ValidationError("La calificación debe estar entre 1 y 5 estrellas.")
        
        # Validar que el usuario haya comprado el producto
        if self.user and self.product:
            has_purchased = OrderItem.objects.filter(
                order__user=self.user,
                product=self.product,
                order__status__in=['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED']
            ).exists()
            
            if not has_purchased:
                raise forms.ValidationError(
                    "Debes haber comprado este producto para poder dejar una reseña."
                )
        
        return cleaned_data
