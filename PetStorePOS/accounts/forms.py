from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile
import re
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from core.forms import DelayedReCaptchaField
from difflib import SequenceMatcher
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Requiere un email válido.')
    captcha = ReCaptchaField()

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "captcha")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class EditProfileForm(forms.ModelForm):
    first_name = forms.CharField(label="Nombre", max_length=30, required=False)
    last_name = forms.CharField(label="Apellidos", max_length=30, required=False)
    email = forms.EmailField(label="Correo electrónico", required=True)
    phone_number = forms.CharField(
        label="Teléfono",
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': '+34 666 123 456',
            'pattern': r'^\+?\d{9,15}$',
            'title': 'Sólo números, mínimo 9 máximo 15 dígitos, opcional + al inicio'
        })
    )
    postal_code = forms.CharField(
        label="Código Postal",
        max_length=8,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': '28013',
            'pattern': r'^\d{5}$',
            'title': 'Debe ser un código postal válido de 5 dígitos'
        })
    )

    class Meta:
        model = UserProfile
        fields = [
            'phone_number', 'address', 'city', 'postal_code',
            'receive_newsletter', 'receive_adoption_alerts', 'receive_product_recommendations'
        ]

    def clean_email(self):
        correo = self.cleaned_data['email']
        # Elimina la siguiente línea si quieres aceptar emails distintos a Gmail
        # if not re.match(r'^[A-Za-z0-9._%+-]+@gmail\.com$', correo):
        #     raise forms.ValidationError('El correo debe ser una cuenta de Gmail válida.')
        return correo

    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']
        phone_sin_espacios = re.sub(r'\s+', '', phone)
        if not re.match(r'^\+?\d{9,15}$', phone_sin_espacios):
            raise forms.ValidationError('Debe ingresar un teléfono válido con solo dígitos (y opcional +) de 9 a 15 caracteres.')
        return phone

    def clean_postal_code(self):
        code = self.cleaned_data['postal_code']
        if not re.match(r'^\d{5}$', code):
            raise forms.ValidationError('El código postal debe ser 5 números.')
        return code


class PasswordRecoveryVerificationForm(forms.Form):
    """Formulario para verificar la identidad del usuario mediante similitud"""
    email = forms.EmailField(
        label=_("Correo electrónico"),
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control bg-light border-0',
            'placeholder': _('Ingresa tu correo electrónico'),
            'autocomplete': 'email'
        })
    )
    remembered_info = forms.CharField(
        label=_("¿Qué recuerdas? (nombre de usuario, nombre o contraseña)"),
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control bg-light border-0',
            'placeholder': _('Ingresa algo que recuerdes de tu cuenta'),
            'autocomplete': 'off'
        }),
        help_text=_("Ingresa tu nombre de usuario, nombre completo o cualquier dato que recuerdes de tu cuenta.")
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        remembered_info = cleaned_data.get('remembered_info')
        
        if email and remembered_info:
            # Buscar usuario por email
            try:
                user = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                raise ValidationError(_("No se encontró ninguna cuenta con ese correo electrónico."))
            
            # Calcular similitud con diferentes campos del usuario
            username_similarity = SequenceMatcher(None, remembered_info.lower(), user.username.lower()).ratio()
            first_name_similarity = SequenceMatcher(None, remembered_info.lower(), (user.first_name or '').lower()).ratio()
            last_name_similarity = SequenceMatcher(None, remembered_info.lower(), (user.last_name or '').lower()).ratio()
            full_name_similarity = SequenceMatcher(
                None, 
                remembered_info.lower(), 
                f"{user.first_name} {user.last_name}".lower().strip()
            ).ratio()
            
            # Verificar si alguno tiene al menos 60% de similitud
            max_similarity = max(username_similarity, first_name_similarity, last_name_similarity, full_name_similarity)
            
            if max_similarity < 0.6:
                # Si no hay suficiente similitud, también verificar si el usuario tiene perfil
                try:
                    profile = user.userprofile
                    # Verificar otros campos del perfil si existen
                    phone_similarity = SequenceMatcher(None, remembered_info.lower(), (profile.phone_number or '').lower()).ratio()
                    max_similarity = max(max_similarity, phone_similarity)
                except UserProfile.DoesNotExist:
                    pass
                
                if max_similarity < 0.6:
                    raise ValidationError(_(
                        "La información proporcionada no coincide lo suficiente con los datos de tu cuenta. "
                        "Por favor, intenta con otra información que recuerdes."
                    ))
            
            # Guardar el usuario en cleaned_data para usarlo en la vista
            cleaned_data['verified_user'] = user
        
        return cleaned_data


class PasswordRecoveryChangeForm(forms.Form):
    """Formulario para cambiar la contraseña después de verificar la identidad"""
    new_password1 = forms.CharField(
        label=_("Nueva Contraseña"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control bg-light border-0',
            'placeholder': _('Ingresa tu nueva contraseña'),
            'autocomplete': 'new-password'
        }),
        min_length=6,
        required=True,
        help_text=_("La contraseña debe tener al menos 6 caracteres.")
    )
    new_password2 = forms.CharField(
        label=_("Confirmar Nueva Contraseña"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control bg-light border-0',
            'placeholder': _('Confirma tu nueva contraseña'),
            'autocomplete': 'new-password'
        }),
        min_length=6,
        required=True
    )
    recaptcha = DelayedReCaptchaField(
        widget=ReCaptchaV2Checkbox(),
        label="Verificación anti-bots",
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError(_("Las contraseñas no coinciden."))
            
            # Validaciones adicionales de seguridad
            if password1.isdigit():
                raise ValidationError(_("La contraseña no puede ser completamente numérica."))
        
        return cleaned_data
