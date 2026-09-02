from django.db import models

class Artista(models.Model):
    nombre_artista = models.CharField(max_length=150)
    pais = models.CharField(max_length=100, blank=True)
    descripcion_artista = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Artistas"

    def __str__(self):
        return self.nombre_artista
    

class Categoria(models.Model):
    nombre = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=250)
    artista = models.ForeignKey(Artista, on_delete=models.CASCADE, related_name='productos')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='productos')
    descripcion = models.CharField(max_length=250)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField()
    imagen = models.ImageField(upload_to='img/')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = "Vinilo"


    def __str__(self):
        return self.nombre