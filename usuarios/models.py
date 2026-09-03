from django.db import models
from django.contrib.auth.models import AbstractUser


# Usuario extiende AbstractUser en vez de partir de cero. AbstractUser ya
# trae listos: username, email, first_name, last_name, password (hasheada
# automaticamente), is_active, is_staff, is_superuser, y todo el sistema
# de login/permisos de Django. Aca solo se agregan los campos que faltan
# para este proyecto.
class Usuario(AbstractUser):

    # TextChoices define un conjunto cerrado de opciones validas para el
    # campo "rol". Se puede usar despues en el codigo como
    # Usuario.Rol.ADMINISTRADOR en vez de escribir el texto "administrador"
    # a mano (evita errores de tipeo y hace el codigo mas legible).
    class Rol(models.TextChoices):
        CLIENTE = "cliente", "Cliente"
        VENDEDOR = "vendedor", "Vendedor"
        ADMINISTRADOR = "administrador", "Administrador"

    # RUN chileno, sin puntos ni guion (ej: 19011022K). La validacion del
    # formato (que el digito verificador sea correcto) se hace en el
    # formulario, no aca: el modelo solo define que tipo de dato se guarda.
    run = models.CharField(max_length=9)

    # choices=Rol.choices limita los valores posibles a los 3 definidos
    # arriba. default=Rol.CLIENTE es lo que se asigna si no se indica
    # nada al crear un usuario nuevo.
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.CLIENTE)

    # null=True, blank=True porque el PDF de requisitos indica que la
    # fecha de nacimiento es opcional (null=True permite NULL en la base
    # de datos, blank=True permite dejar el campo vacio en formularios).
    fecha_nacimiento = models.DateField(null=True, blank=True)

    direccion = models.CharField(max_length=300)
    region = models.CharField(max_length=300)
    comuna = models.CharField(max_length=300)

    class Meta:
        verbose_name = "Usuario"

    def __str__(self):
        # Define como se muestra un Usuario cuando se imprime o se ve en
        # el admin de Django (por ejemplo, en una lista desplegable).
        return self.username
