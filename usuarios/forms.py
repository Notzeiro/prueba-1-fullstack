from django import forms

from .models import Usuario


class RegistroForm(forms.Form):
    # Formulario simple de registro. No es un ModelForm porque el modelo
    # Usuario tiene campos adicionales (run, direccion, region, comuna)
    # que todavia no se piden en esta version del formulario de registro;
    # esos quedan pendientes para una version mas completa mas adelante.

    nombre = forms.CharField(max_length=100, label="Nombre completo")
    email = forms.EmailField(max_length=100, label="Correo")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar contraseña")
    telefono = forms.CharField(max_length=20, required=False, label="Telefono (opcional)")

    def clean_email(self):
        # clean_<campo> se ejecuta automaticamente para validar un campo
        # en particular. Aca se evita que dos personas se registren con
        # el mismo correo (evitar usuarios duplicados, punto 8 del checklist).
        email = self.cleaned_data["email"]
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe una cuenta registrada con este correo.")
        return email

    def clean(self):
        # clean() sin sufijo se ejecuta al final, cuando ya se validaron
        # todos los campos por separado. Sirve para validaciones que
        # dependen de mas de un campo a la vez, como comparar las dos
        # contraseñas ingresadas.
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Las contraseñas no coinciden.")

        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(label="Correo electrónico")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
