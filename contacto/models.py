from django.db import models


class Contacto(models.Model):
    # Este modelo no tiene relacion (ForeignKey) con ningun otro: un
    # mensaje de contacto se puede enviar sin estar registrado ni haber
    # iniciado sesion, asi que no depende del modelo Usuario.

    nombre = models.CharField(max_length=100)
    correo = models.EmailField(max_length=100)
    asunto = models.CharField(max_length=150)

    # max_length en un TextField no limita la base de datos (Postgres lo
    # ignora a nivel de columna), pero Django SI lo usa para validar el
    # formulario: si alguien escribe mas de 500 caracteres, el formulario
    # marca error antes de guardar.
    mensaje = models.TextField(max_length=500)

    fecha_envio = models.DateTimeField(auto_now_add=True)

    # Permite que el administrador marque un mensaje como "ya visto" sin
    # tener que borrarlo, para diferenciar pendientes de revisados.
    revisado = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Mensaje de contacto"
        verbose_name_plural = "Mensajes de contacto"
        # El "-" antes del nombre del campo invierte el orden: los
        # mensajes mas nuevos aparecen primero en vez de los mas viejos.
        ordering = ['-fecha_envio']

    def __str__(self):
        return f"{self.asunto} — {self.nombre}"
