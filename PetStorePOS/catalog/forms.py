# catalog/forms.py
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Product, Category, ProductReview

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

#Formulario para búsqueda avanzada de productos.
class ProductSearchForm(forms.Form):
    # Campo de búsqueda de texto
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Buscar productos...')
        }),
        label=_('Buscar')
    )
    
    # Filtro por categoría
    category = forms.ChoiceField(
        required=False,
        choices=[('', _('Todas las categorías'))] + list(Category.choices),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Categoría')
    )
    
    # Filtro por precio mínimo
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('Mínimo'),
            'step': '0.01',
            'min': '0'
        }),
        label=_('Precio Mínimo')
    )
    
    # Filtro por precio máximo
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('Máximo'),
            'step': '0.01',
            'min': '0'
        }),
        label=_('Precio Máximo')
    )
    
    # Filtro por disponibilidad
    in_stock = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label=_('Solo productos disponibles')
    )
    
    # Ordenamiento
    order_by = forms.ChoiceField(
        required=False,
        choices=[
            ('name', _('Nombre (A-Z)')),
            ('-name', _('Nombre (Z-A)')),
            ('price', _('Precio (Menor a Mayor)')),
            ('-price', _('Precio (Mayor a Menor)')),
            ('created_at', _('Más recientes')),
            ('-created_at', _('Más antiguos')),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Ordenar por')
    )


#formulario para crear reseñas de productos
class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': 1,
                'max': 5,
                'class': 'form-control',
                'placeholder': _('Calificación de 1 a 5')
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Escribe tu opinión sobre el producto...')
            }),
        }
        labels = {
            'rating': _('Calificación'),
            'comment': _('Comentario'),
        }
        help_texts = {
            'rating': _('Selecciona una calificación de 1 a 5 estrellas'),
            'comment': _('Comparte tu experiencia con este producto'),
        }

    #Valida que la calificación esté entre 1 y 5.
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating and (rating < 1 or rating > 5):
            raise forms.ValidationError(_("La calificación debe estar entre 1 y 5."))
        return rating
