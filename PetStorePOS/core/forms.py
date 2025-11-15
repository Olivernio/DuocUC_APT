from django_recaptcha.fields import ReCaptchaField            # django‑recaptcha 3.x
from django_recaptcha.widgets import ReCaptchaV2Checkbox      # v2 Checkbox por defecto

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class PersonalInfoForm(forms.Form):
    nombre = forms.CharField(label=_("Nombre"), max_length=100, required=True)
    apellidos = forms.CharField(label=_("Apellidos"), max_length=100, required=True)


class ContactDataForm(forms.Form):
    correo = forms.EmailField(label=_("Correo electrónico"), required=True)


class PreferencesForm(forms.Form):
    contraseña = forms.CharField(
        label=_("Contraseña"),
        widget=forms.PasswordInput,
        min_length=6,
        required=True,
    )
    confirmar_contraseña = forms.CharField(
        label=_("Confirmar Contraseña"),
        widget=forms.PasswordInput,
        min_length=6,
        required=True,
    )
    # Google reCAPTCHA (v2 checkbox) - Accesible
    recaptcha = ReCaptchaField(
        widget=ReCaptchaV2Checkbox(),
        label=_("Verificación de seguridad"),
        help_text=_("Por favor, completa la verificación reCAPTCHA. Si tienes problemas de visión, puedes usar el desafío de audio disponible en el widget."),
        required=True,
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("contraseña")
        confirm_password = cleaned_data.get("confirmar_contraseña")
        if password and confirm_password and password != confirm_password:
            raise ValidationError(_("Las contraseñas no coinciden."))
        return cleaned_data
