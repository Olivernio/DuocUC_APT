from django import forms
from django.core.validators import RegexValidator

class PersonalInfoForm(forms.Form):
    nombre = forms.CharField(max_length=100, required=True, label="Nombre")
    apellidos = forms.CharField(max_length=150, required=True, label="Apellidos")
    correo = forms.EmailField(required=True, label="Correo electrónico")
    contraseña = forms.CharField(widget=forms.PasswordInput, min_length=8, required=True, label="Contraseña")

class ContactDataForm(forms.Form):
    telefono = forms.CharField(
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', message="Número inválido")],
        required=True,
        label="Teléfono"
    )
    direccion = forms.CharField(max_length=255, required=True, label="Dirección")
    ciudad = forms.CharField(max_length=100, required=True, label="Ciudad")
    codigo_postal = forms.CharField(max_length=20, required=True, label="Código Postal")
    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True, label="Fecha de nacimiento")

class PreferencesForm(forms.Form):
    preferencias_comunicacion = forms.MultipleChoiceField(
        choices=[('email', 'Email'), ('sms', 'SMS'), ('telefono', 'Teléfono')],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Preferencias de comunicación"
    )
    acepta_terminos = forms.BooleanField(
        required=True,
        label="Acepto términos y políticas"
    )
