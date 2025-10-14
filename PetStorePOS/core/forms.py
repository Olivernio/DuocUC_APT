from django import forms
from django.core.exceptions import ValidationError

# Paso 1
class PersonalInfoForm(forms.Form):
    nombre = forms.CharField(label="Nombre", max_length=100, required=True)
    apellidos = forms.CharField(label="Apellidos", max_length=100, required=True)

# Paso 2
class ContactDataForm(forms.Form):
    correo = forms.EmailField(label="Correo electrónico", required=True)

# Paso 3
class PreferencesForm(forms.Form):
    contraseña = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput,
        min_length=6,
        required=True
    )
    confirmar_contraseña = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput,
        min_length=6,
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("contraseña")
        confirm_password = cleaned_data.get("confirmar_contraseña")
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Las contraseñas no coinciden.")
        return cleaned_data