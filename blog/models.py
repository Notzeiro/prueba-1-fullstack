from django.conf import settings
from django.db import models


class Blog(models.Model):
    # Titulo de la publicacion, se muestra en el listado y en el detalle.
    titulo = models.CharField(max_length=250)

    # Texto corto que se muestra en la tarjeta del listado de blog
    # (no es el contenido completo, es como un resumen).
    descripcion = models.CharField(max_length=250, help_text="Extracto corto para el listado")

    # Cuerpo completo del post. TextField no tiene limite de caracteres,
    # a diferencia de CharField, por eso se usa para textos largos.
    contenido = models.TextField(help_text="Contenido completo de la publicación")

    # ForeignKey = relacion "muchos a uno": muchos posts pueden tener el
    # mismo autor, pero cada post tiene un solo autor.
    # Se usa settings.AUTH_USER_MODEL en vez de importar el modelo
    # Usuario directamente para evitar una dependencia circular entre
    # las apps "usuarios" y "blog" (blog no necesita saber los detalles
    # internos de usuarios, solo que existe "algun" modelo de usuario).
    # on_delete=CASCADE: si se borra el usuario autor, se borran tambien
    # sus posts.
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')

    imagen_portada = models.ImageField(upload_to='img/')

    # Permite "despublicar" un post sin borrarlo de la base de datos
    # (equivalente al "activo" de Producto).
    activo = models.BooleanField(default=True)

    # auto_now_add=True: se completa solo una vez, al crear el registro,
    # y despues no vuelve a cambiar aunque se edite el post.
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # auto_now=True: se actualiza solo cada vez que el registro se guarda
    # de nuevo (por ejemplo, al editar el post desde el admin).
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Blog"
        verbose_name_plural = "Blogs"

    def __str__(self):
        return self.titulo


class ImagenBlog(models.Model):
    # Permite que un mismo post tenga varias imagenes de galeria, ademas
    # de la imagen de portada. related_name='imagenes' es lo que permite
    # escribir despues "un_blog.imagenes.all()" para traer todas las
    # imagenes asociadas a ese post.
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='imagenes')

    imagen = models.ImageField(upload_to='img/blog/galeria/')

    # Permite controlar en que orden se muestran las imagenes de la
    # galeria (0 primero, 1 despues, etc.), en vez de mostrarlas en el
    # orden en que se cargaron.
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        # Hace que, por defecto, cualquier consulta a ImagenBlog venga
        # ya ordenada por el campo "orden", sin tener que pedirlo cada vez.
        ordering = ['orden']
        verbose_name = "Imagen de blog"
        verbose_name_plural = "Imágenes de blog"

    def __str__(self):
        return f"Imagen de {self.blog.titulo}"
