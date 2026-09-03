from django.contrib import admin

from .models import Blog, ImagenBlog


# TabularInline muestra las imágenes de galería de un post dentro de la
# misma pantalla de edición del post, en vez de tener que crearlas por
# separado en su propia sección del admin.
class ImagenBlogInline(admin.TabularInline):
    model = ImagenBlog
    extra = 1  # cuántas filas vacías extra mostrar para cargar imágenes nuevas


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ("titulo", "autor", "activo", "fecha_creacion")
    list_filter = ("activo", "autor")
    search_fields = ("titulo", "contenido")
    inlines = [ImagenBlogInline]
