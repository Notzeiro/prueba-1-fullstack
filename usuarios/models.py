from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):

    class Rol(models.TextChoices):
        CLIENTE = "cliente", "Cliente"
        VENDEDOR = "vendedor", "Vendedor"
        ADMINISTRADOR = "administrador", "Administrador"

    run = models.CharField(max_length=9)
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.CLIENTE)
    fecha_nacimiento = models.DateField(null=True , blank=True)
    direccion = models.CharField(max_length=300)
    region = models.CharField(max_length=300)
    comuna = models.CharField(max_length=300)

    class Meta:
        verbose_name = "Usuario"

    def __str__(self):
        return self.username         # cómo se ve el objeto al imprimirlo
