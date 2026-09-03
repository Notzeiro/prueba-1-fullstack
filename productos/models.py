from django.db import models


class Artista(models.Model):
    nombre_artista = models.CharField(max_length=150)
    # blank=True: el campo puede quedar vacio en formularios/admin
    # (a diferencia de null=True, que es a nivel de base de datos).
    # Para CharField/TextField se usa blank=True solo, sin null=True,
    # porque Django ya guarda "vacio" como cadena vacia, no como NULL.
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

    # ForeignKey = relacion "muchos a uno": un artista puede tener varios
    # productos (discos), pero cada producto es de un solo artista.
    # on_delete=CASCADE: si se borra el artista, se borran tambien todos
    # sus productos (borrado en cascada).
    # related_name='productos' permite despues escribir
    # "un_artista.productos.all()" para traer todos sus discos.
    artista = models.ForeignKey(Artista, on_delete=models.CASCADE, related_name='productos')

    # null=True permite que un producto quede sin categoria asignada.
    # on_delete=SET_NULL: si se borra la categoria, el producto NO se
    # borra, solo queda con categoria=None (a diferencia de CASCADE).
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='productos')

    # TextField porque una descripcion de producto puede ser larga y no
    # tiene sentido ponerle un limite corto de caracteres como CharField.
    descripcion = models.TextField(blank=True)

    # DecimalField en vez de FloatField: para dinero siempre se usa
    # DecimalField, porque FloatField puede generar errores de redondeo
    # (por como se guardan los numeros decimales en binario).
    # max_digits=8, decimal_places=2 permite precios de hasta 999999.99.
    precio = models.DecimalField(max_digits=8, decimal_places=2)

    # PositiveIntegerField no permite numeros negativos: no tiene sentido
    # tener "-5" unidades de stock.
    stock = models.PositiveIntegerField()

    # ImageField guarda la imagen en la carpeta media/img/ (definida por
    # MEDIA_ROOT en settings.py) y en la base de datos solo se guarda la
    # ruta del archivo, no la imagen en si.
    imagen = models.ImageField(upload_to='img/')

    # Permite "desactivar" un producto (dejar de mostrarlo en la tienda)
    # sin borrarlo de la base de datos. Es la practica recomendada frente
    # a borrar productos que ya tuvieron ventas o historial.
    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vinilo"

    def __str__(self):
        return self.nombre
