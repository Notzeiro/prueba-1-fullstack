from django.db import models

class Blog(models.Model):
    titulo = models.CharField(max_length=250)
    descripcion = models.CharField(max_length=250)
    imagen_portada = models.ImageField(upload_to='img/')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = "Blog"
        verbose_name_plural = "Blogs"


    def __str__(self):
        return self.titulo

class ImagenBlog(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='img/blog/galeria/')
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden']
        verbose_name = "Imagen de blog"
        verbose_name_plural = "Imágenes de blog"

    def __str__(self):
        return f"Imagen de {self.blog.titulo}"