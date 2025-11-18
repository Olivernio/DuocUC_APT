from django import forms
from django.utils.translation import gettext_lazy as _


class CheckoutForm(forms.Form):
    """
    Formulario para el proceso de checkout.
    """
    shipping_address = forms.CharField(
        label=_("Dirección de Envío"),
        max_length=500,
        required=True,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': _('Ingresa tu dirección completa')
        })
    )
    shipping_city = forms.CharField(
        label=_("Ciudad"),
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Ej: Santiago, Valparaíso, etc.')
        })
    )
    shipping_postal_code = forms.CharField(
        label=_("Código Postal"),
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Opcional')
        })
    )
    notes = forms.CharField(
        label=_("Notas Adicionales"),
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': _('Instrucciones especiales de entrega (opcional)')
        })
    )

    def clean_shipping_address(self):
        address = self.cleaned_data.get('shipping_address')
        if address and len(address.strip()) < 10:
            raise forms.ValidationError(_("Por favor, ingresa una dirección más detallada (mínimo 10 caracteres)."))
        return address

    def clean_shipping_city(self):
        city = self.cleaned_data.get('shipping_city')
        if city and len(city.strip()) < 2:
            raise forms.ValidationError(_("Por favor, ingresa un nombre de ciudad válido."))
        return city


class OrderStatusUpdateForm(forms.Form):
    """
    Formulario para actualizar el estado de una orden (admin).
    """
    status = forms.ChoiceField(
        label=_("Nuevo Estado"),
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        from .models import OrderStatus
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = OrderStatus.choices


class CouponForm(forms.Form):
    """
    Formulario para aplicar un cupón en el checkout.
    """
    coupon_code = forms.CharField(
        label=_("Código de Cupón"),
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Ingresa el código del cupón'),
            'style': 'text-transform: uppercase;'
        })
    )

    def clean_coupon_code(self):
        code = self.cleaned_data.get('coupon_code', '').strip().upper()
        if not code:
            return None
        
        from .models import Coupon
        from django.db.utils import OperationalError
        
        try:
            coupon = Coupon.objects.get(code=code)
            if not coupon.is_valid():
                raise forms.ValidationError(_("Este cupón no es válido o ha expirado."))
            return coupon
        except Coupon.DoesNotExist:
            raise forms.ValidationError(_("El código de cupón ingresado no existe."))
        except OperationalError:
            # Si la tabla no existe, ignorar el cupón sin error
            return None
        except Exception:
            # Cualquier otro error, ignorar el cupón
            return None
