from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


# Usuario hereda de AbstractUser, así que su admin también debe heredar
# de UserAdmin en vez de registrarse "a secas". Si se registrara con
# admin.site.register(Usuario) sin más, el formulario del admin mostraría
# la contraseña como texto plano editable en vez de manejarla con el
# sistema de hasheo de Django.
class UsuarioAdmin(UserAdmin):
    # Columnas que se muestran en el listado de usuarios del admin.
    list_display = ("username", "email", "first_name", "last_name", "rol", "is_staff")

    # Permite filtrar el listado por estas columnas (aparece a la derecha).
    list_filter = ("rol", "is_staff", "is_active")

    # UserAdmin ya trae "fieldsets" definidos para username/password/permisos.
    # Acá se agrega una sección nueva al final con los campos propios
    # que se le sumaron a Usuario (los que no vienen en AbstractUser).
    fieldsets = UserAdmin.fieldsets + (
        (
            "Datos adicionales",
            {
                "fields": (
                    "run",
                    "rol",
                    "fecha_nacimiento",
                    "direccion",
                    "region",
                    "comuna",
                )
            },
        ),
    )


admin.site.register(Usuario, UsuarioAdmin)
