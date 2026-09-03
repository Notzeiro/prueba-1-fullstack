from django.contrib import admin

from .models import Artista, Categoria, Producto


@admin.register(Artista)
class ArtistaAdmin(admin.ModelAdmin):
    # Columnas visibles en el listado.
    list_display = ("nombre_artista", "pais")
    # Caja de búsqueda del admin: busca coincidencias en estos campos.
    search_fields = ("nombre_artista",)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "artista", "categoria", "precio", "stock", "activo")
    # Filtros rápidos a la derecha del listado.
    list_filter = ("activo", "categoria", "artista")
    search_fields = ("nombre", "artista__nombre_artista")
    # Permite editar "activo" directamente desde la lista, sin entrar
    # al detalle del producto (útil para desactivar productos rápido).
    list_editable = ("activo",)
