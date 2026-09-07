"""
Carga (o actualiza) el catalogo de 50 vinilos con su codigo RC (Release
ID de Discogs, https://api.discogs.com/releases/<rc>).

Es idempotente: busca cada producto por (nombre, artista) antes de
crear uno nuevo -- como estos 50 productos ya existian (cargados antes
por seed_demo), en la practica esto no crea productos nuevos, solo les
completa el campo "rc" y actualiza categoria/precio/stock/activo para
que coincidan exactamente con los valores entregados.

No se uso SQL crudo a proposito: los datos originales venian como un
INSERT contra una tabla "Vinilos" con columnas "Artista"/"Categoria"
como texto plano, pero en este proyecto Artista y Categoria son tablas
aparte relacionadas por ForeignKey (ver productos/models.py) -- correr
ese SQL tal cual no es compatible con el esquema real. La adaptacion
correcta es usar el ORM, que arma las relaciones y evita duplicar
Artista/Categoria (get_or_create).

Tambien el SQL original traia "Activo=NULL" en todas las filas, lo cual
no es un valor valido para nuestro campo "activo" (BooleanField sin
null=True) -- se adapta usando el valor por defecto del campo (True),
que es ademas el que ya tienen el resto de los productos de la tienda.

Uso:
    python manage.py cargar_rc_discogs
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from productos.models import Artista, Categoria, Producto

# (nombre, artista, categoria, precio, stock, rc)
DATOS = [
    ("Faith", "George Michael", "Pop", Decimal("24990.00"), 40, 413315),
    ("Purple Rain", "Prince", "Pop", Decimal("29990.00"), 19, 125874),
    ("Arrival", "ABBA", "Pop", Decimal("17990.00"), 38, 441165),
    ("Like a Prayer", "Madonna", "Pop", Decimal("19990.00"), 11, 116237),
    ("Thriller", "Michael Jackson", "Pop", Decimal("26990.00"), 12, 152946),
    ("Marcus Garvey", "Burning Spear", "Reggae", Decimal("26990.00"), 28, 135352),
    ("Funky Kingston", "Toots and the Maytals", "Reggae", Decimal("21990.00"), 16, 581580),
    ("Legalize It", "Peter Tosh", "Reggae", Decimal("14990.00"), 16, 521861),
    ("Legend", "Bob Marley & The Wailers", "Reggae", Decimal("24990.00"), 20, 509235),
    ("Otis Blue", "Otis Redding", "Soul", Decimal("12990.00"), 23, 1200101),
    ("Let's Stay Together", "Al Green", "Soul", Decimal("12990.00"), 17, 1431306),
    ("Songs in the Key of Life", "Stevie Wonder", "Soul", Decimal("17990.00"), 23, 266650),
    ("I Never Loved a Man the Way I Love You", "Aretha Franklin", "Soul", Decimal("19990.00"), 38, 488037),
    ("What's Going On", "Marvin Gaye", "Soul", Decimal("26990.00"), 27, 359107),
    ("You've Come a Long Way, Baby", "Fatboy Slim", "Electronica", Decimal("17990.00"), 13, 11234),
    ("Cross", "Justice", "Electronica", Decimal("16990.00"), 37, 992104),
    ("Selected Ambient Works 85-92", "Aphex Twin", "Electronica", Decimal("19990.00"), 7, 32662),
    ("Trans-Europe Express", "Kraftwerk", "Electronica", Decimal("21990.00"), 16, 214065),
    ("Discovery", "Daft Punk", "Electronica", Decimal("16990.00"), 26, 2879),
    ("Time Out", "Dave Brubeck", "Jazz", Decimal("26990.00"), 26, 372423),
    ("Brilliant Corners", "Thelonious Monk", "Jazz", Decimal("24990.00"), 20, 10917189),
    ("Head Hunters", "Herbie Hancock", "Jazz", Decimal("17990.00"), 9, 31381),
    ("A Love Supreme", "John Coltrane", "Jazz", Decimal("19990.00"), 8, 857505),
    ("Kind of Blue", "Miles Davis", "Jazz", Decimal("12990.00"), 17, 1353040),
    ("It Takes a Nation of Millions to Hold Us Back", "Public Enemy", "Hip-Hop", Decimal("17990.00"), 7, 86169),
    ("To Pimp a Butterfly", "Kendrick Lamar", "Hip-Hop", Decimal("21990.00"), 39, 6787439),
    ("The Low End Theory", "A Tribe Called Quest", "Hip-Hop", Decimal("29990.00"), 21, 87291),
    ("Enter the Wu-Tang (36 Chambers)", "Wu-Tang Clan", "Hip-Hop", Decimal("24990.00"), 8, 153749),
    ("Illmatic", "Nas", "Hip-Hop", Decimal("29990.00"), 10, 392604),
    ("Painkiller", "Judas Priest", "Metal", Decimal("12990.00"), 32, 689377),
    ("Reign in Blood", "Slayer", "Metal", Decimal("21990.00"), 19, 373186),
    ("The Number of the Beast", "Iron Maiden", "Metal", Decimal("14990.00"), 25, 367137),
    ("Master of Puppets", "Metallica", "Metal", Decimal("14990.00"), 27, 371142),
    ("Paranoid", "Black Sabbath", "Metal", Decimal("21990.00"), 9, 376679),
    ("Risque", "Chic", "Funk Rock", Decimal("16990.00"), 16, 68599),
    ("Street Songs", "Rick James", "Funk Rock", Decimal("21990.00"), 20, 176072),
    ("There's a Riot Goin' On", "Sly and the Family Stone", "Funk Rock", Decimal("16990.00"), 30, 473679),
    ("Mothership Connection", "Parliament", "Funk Rock", Decimal("19990.00"), 3, 1992884),
    ("Californication", "Red Hot Chili Peppers", "Funk Rock", Decimal("17990.00"), 31, 367220),
    ("Fresh Fruit for Rotting Vegetables", "Dead Kennedys", "Punk Rock", Decimal("29990.00"), 29, 372568),
    ("London Calling", "The Clash", "Punk Rock", Decimal("29990.00"), 15, 378698),
    ("Never Mind the Bollocks", "Sex Pistols", "Punk Rock", Decimal("29990.00"), 4, 369999),
    ("Ramones", "Ramones", "Punk Rock", Decimal("17990.00"), 17, 890352),
    ("Walk Among Us", "Misfits", "Punk Rock", Decimal("12990.00"), 8, 14089131),
    ("The Rise and Fall of Ziggy Stardust", "David Bowie", "Rock", Decimal("24990.00"), 5, 422477),
    ("Abbey Road", "The Beatles", "Rock", Decimal("14990.00"), 40, 612916),
    ("A Night at the Opera", "Queen", "Rock", Decimal("14990.00"), 37, 371966),
    ("Rumours", "Fleetwood Mac", "Rock", Decimal("17990.00"), 11, 374881),
    ("IV", "Led Zeppelin", "Rock", Decimal("19990.00"), 18, 1015465),
    ("The Dark Side of the Moon", "Pink Floyd", "Rock", Decimal("14990.00"), 4, 367104),
]


class Command(BaseCommand):
    help = "Carga/actualiza el catalogo de 50 vinilos con su RC (Release ID de Discogs)."

    @transaction.atomic
    def handle(self, *args, **options):
        creados = 0
        actualizados = 0

        for nombre, artista_nombre, categoria_nombre, precio, stock, rc in DATOS:
            artista, _ = Artista.objects.get_or_create(nombre_artista=artista_nombre)
            categoria, _ = Categoria.objects.get_or_create(nombre=categoria_nombre)

            producto, creado = Producto.objects.get_or_create(
                nombre=nombre,
                artista=artista,
                defaults={
                    "categoria": categoria,
                    "precio": precio,
                    "stock": stock,
                    "activo": True,
                    "rc": rc,
                },
            )

            if creado:
                creados += 1
            else:
                # Ya existia (por ejemplo, de seed_demo): se actualiza para
                # que coincida exactamente con los valores entregados, y
                # sobre todo, se le agrega el RC que antes no tenia.
                producto.categoria = categoria
                producto.precio = precio
                producto.stock = stock
                producto.activo = True
                producto.rc = rc
                producto.save()
                actualizados += 1

        self.stdout.write(self.style.SUCCESS(
            f"Listo: {creados} productos nuevos, {actualizados} actualizados con su RC (de {len(DATOS)} en total)."
        ))
