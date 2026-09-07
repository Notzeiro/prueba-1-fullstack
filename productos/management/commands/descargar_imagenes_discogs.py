"""
Reemplaza la portada generada localmente (la de seed_demo, un fondo de
color con texto) por la portada real del disco, descargada desde Discogs
usando el RC de cada producto -- para que el catalogo (/productos/) y
cualquier lugar que use "producto.imagen" (listado, relacionados, la
imagen inicial del detalle) muestren la foto real, no el placeholder.

No agrega ninguna libreria nueva: usa "urllib" (viene con Python) en vez
de "requests", que no esta en requirements.txt.

Es seguro correrlo varias veces: si un producto no tiene RC, o Discogs
no tiene imagenes para ese release, o falla la descarga, simplemente se
deja la imagen que ya tenia (nunca se rompe ni se borra nada) -- solo se
reemplaza cuando la descarga fue exitosa.

Uso:
    python manage.py descargar_imagenes_discogs
"""
import json
import time
import urllib.error
import urllib.request

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from productos.models import Producto

# Discogs exige un User-Agent identificable; sin esto puede responder 403.
USER_AGENT = "VynilStoreApp/1.0 (+https://vynilstore.notzeiro.tech)"

# Pausa entre productos para no golpear de mas la API publica de Discogs
# (tiene limite de peticiones por minuto para consumidores sin token, y
# cada producto hace 2 peticiones: el JSON del release + la imagen).
PAUSA_SEGUNDOS = 3

# Sufijo que se le pone al archivo cuando la portada ya es la real de
# Discogs (ver "nombre_archivo" mas abajo). Sirve para poder cortar el
# comando a la mitad (por ejemplo, por un 429 de Discogs) y volver a
# correrlo despues sin re-descargar lo que ya se habia conseguido.
SUFIJO_YA_DESCARGADA = "-discogs.jpg"


def _pedir_json(url):
    peticion = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(peticion, timeout=10) as respuesta:
        return json.loads(respuesta.read().decode("utf-8"))


def _descargar_bytes(url):
    peticion = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(peticion, timeout=10) as respuesta:
        return respuesta.read()


class Command(BaseCommand):
    help = "Descarga la portada real de Discogs (via RC) para cada producto y reemplaza su imagen generada."

    def handle(self, *args, **options):
        productos = Producto.objects.filter(rc__isnull=False).order_by("id")

        reemplazadas = 0
        sin_imagen_en_discogs = 0
        con_error = 0

        for producto in productos:
            if producto.imagen and producto.imagen.name.endswith(SUFIJO_YA_DESCARGADA):
                continue  # ya tiene la portada real de una corrida anterior

            try:
                datos = _pedir_json(f"https://api.discogs.com/releases/{producto.rc}")
            except (urllib.error.URLError, TimeoutError, ValueError) as error:
                self.stdout.write(self.style.WARNING(
                    f"[{producto.id}] {producto.nombre}: no se pudo consultar Discogs ({error})"
                ))
                con_error += 1
                time.sleep(PAUSA_SEGUNDOS)
                continue

            imagenes = datos.get("images") or []
            url_imagen = imagenes[0].get("uri") if imagenes else None

            if not url_imagen:
                sin_imagen_en_discogs += 1
                time.sleep(PAUSA_SEGUNDOS)
                continue

            try:
                contenido = _descargar_bytes(url_imagen)
            except (urllib.error.URLError, TimeoutError) as error:
                self.stdout.write(self.style.WARNING(
                    f"[{producto.id}] {producto.nombre}: no se pudo descargar la imagen ({error})"
                ))
                con_error += 1
                time.sleep(PAUSA_SEGUNDOS)
                continue

            nombre_archivo = f"{producto.artista.nombre_artista}-{producto.nombre}-discogs.jpg".lower().replace(" ", "-")
            producto.imagen.save(nombre_archivo, ContentFile(contenido), save=True)
            reemplazadas += 1
            time.sleep(PAUSA_SEGUNDOS)

        self.stdout.write(self.style.SUCCESS(
            f"Listo: {reemplazadas} portadas reemplazadas por la real de Discogs, "
            f"{sin_imagen_en_discogs} sin imagen en Discogs (se dejo la local), "
            f"{con_error} con error de red (se dejo la local)."
        ))
