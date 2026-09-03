from django import forms

from .models import Contacto


class ContactoForm(forms.ModelForm):
    # ModelForm genera automaticamente los campos del formulario a partir
    # de los campos del modelo Contacto, evitando escribirlos dos veces
    # (una en el modelo y otra en el formulario).
    class Meta:
        model = Contacto
        fields = ["nombre", "correo", "asunto", "mensaje"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "correo": forms.EmailInput(attrs={"class": "form-control"}),
            "asunto": forms.TextInput(attrs={"class": "form-control"}),
            "mensaje": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
        }
