from django import forms
from .models import AdoptionRequest

class AdoptionRequestForm(forms.ModelForm):
    class Meta:
        model = AdoptionRequest
        fields = ["full_name", "email", "Telefono", "Mensaje"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "Telefono": forms.TextInput(attrs={"class": "form-control"}),
            "Mensaje": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }
