from django.db import models

class AbstractUser(AbstractUser.self):
    run = self.Charfield(parámetros)
    rol = models.TipoDeCampo(parámetros)
    fecha_nacimiento
    direccion=
    region=
    comuna=
    class Meta:
        ordering = ['algún_campo']   # opcional: orden por defecto
        verbose_name = "..."          # opcional: nombre bonito en el admin

    def _str_(self):
        return self.campo1            # cómo se ve el objeto al imprimirlo

Cosas clave:

Cada clase = una tabla. Cada atributo = una columna.
_str_ es obligatorio de buena práctica: sin él, el admin de Django y los print() muestran algo como Producto object (1), ilegible.
Meta es opcional, para configurar comportamiento (orden, nombres).
Django agrega automáticamente un campo id autoincremental como llave primaria — no hace falta declararlo.
Tipos de campo que vas a necesitar



Tipo	Para qué sirve
CharField(max_length=N)	Texto corto (nombres, títulos) — max_length obligatorio
TextField()	Texto largo (descripciones, contenido de blog)
DecimalField(max_digits=N, decimal_places=2)	Precios (nunca uses FloatField para dinero)
PositiveIntegerField()	Stock, cantidades — no permite negativos
BooleanField(default=True/False)	El campo activo
DateTimeField(auto_now_add=True)	Fecha de creación (se pone sola al crear, no editable después)
DateTimeField(auto_now=True)	Fecha de modificación (se actualiza sola cada vez que guardas)
ImageField(upload_to='carpeta/')	Imágenes — usa MEDIA_ROOT que ya configuraron
ForeignKey(OtroModelo, on_delete=models.CASCADE)	Relación "muchos a uno" (ej: un álbum tiene un artista)
SlugField()	Opcional, útil para URLs bonitas (/productos/master-of-puppets/)

on_delete no es opcional en ForeignKey: define qué pasa si borras el registro relacionado. Lo más común es models.CASCADE