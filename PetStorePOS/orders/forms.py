from django import forms 
from django.utils.translation import gettext_lazy as _


class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(
        label=_("Dirección de Envío"),
        max_length=500,
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Ej: Av. Principal 123, Depto 45')

        }),
        help_text=_("Ingresa tu dirección completa")
    )

    
    # Ciudad
    shipping_city = forms.CharField(
        label=_("Ciudad"),
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Ej: Santiago')
        })
    )

    # código postal 
    shipping_city = forms.CharField(
        label=_("Ciudad"),
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Ej: Santiago')
        })
    )
    
    #Notas De Sugerencia Del CLiente
    notes = forms.CharField(
        label=_("Notas Adicionales"),
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': _('Instrucciones especiales de entrega (opcional)')
        })
    )