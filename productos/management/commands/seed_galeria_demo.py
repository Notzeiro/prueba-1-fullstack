"""
Comando de demo: agrega 2 fotos extra de galeria a los primeros N
productos, solo para poder mostrar el carrusel del detalle funcionando
sin tener fotos reales de contraportada/interior de cada disco.

Reutiliza "generar_portada" de seed_demo.py (dibuja un fondo de color +
texto): estas fotos NO son fotos reales del disco, son placeholders de
demo para probar que el carrusel funciona con mas de una imagen.

Es idempotente: si un producto ya tiene fotos de galeria, no le agrega
mas (se puede correr de nuevo sin duplicar).

Uso:
    python manage.py seed_galeria_demo
"""
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from productos.management.commands.seed_demo import generar_portada
from productos.models import ImagenProducto, Producto

CANTIDAD_PRODUCTOS_DEMO = 8
ETIQUETAS = ["Contraportada (demo)", "Detalle interior (demo)"]


class Command(BaseCommand):
    help = "Agrega fotos de galeria de ejemplo a algunos productos, para probar el carrusel del detalle."

    def handle(self, *args, **options):
        productos = Producto.objects.filter(activo=True).order_by('id')[:CANTIDAD_PRODUCTOS_DEMO]
        creadas = 0
        for producto in productos:
            if producto.imagenes.exists():
                continue
            for orden, etiqueta in enumerate(ETIQUETAS, start=1):
                imagen_bytes = generar_portada(producto.nombre, etiqueta)
                nombre_archivo = f"{producto.nombre}-{etiqueta}.webp".lower().replace(" ", "-")
                foto = ImagenProducto(producto=producto, orden=orden)
                foto.imagen.save(nombre_archivo, ContentFile(imagen_bytes), save=True)
                creadas += 1

        self.stdout.write(self.style.SUCCESS(
            f"Listo: {creadas} fotos de galeria (demo) creadas en hasta {CANTIDAD_PRODUCTOS_DEMO} productos."
        ))
