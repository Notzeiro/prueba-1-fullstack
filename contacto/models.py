from django.db import models


class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(max_length=100)
    asunto = models.CharField(max_length=150)
    mensaje = models.TextField(max_length=500)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    revisado = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Mensaje de contacto"
        verbose_name_plural = "Mensajes de contacto"
        ordering = ['-fecha_envio']

    def __str__(self):
        return f"{self.asunto} — {self.nombre}"
