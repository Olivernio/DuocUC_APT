from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile
import re

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Requiere un email válido.')

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

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
        # Elimina la siguiente línea que obliga solo a @gmail.com
        # if not re.match(r'^[A-Za-z0-9._%+-]+@gmail\.com$', correo):
        #     raise forms.ValidationError('El correo debe ser una cuenta de Gmail válida.')
        # Django ya valida el formato correctamente,
        # pero si quieres puedes agregar otros checks aquí.
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
