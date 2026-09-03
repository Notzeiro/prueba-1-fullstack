"""
Comando de datos de prueba: puebla la tienda con categorias, artistas,
50 productos y 2 posts de blog, generando una portada simple para cada
uno (no se descarga ninguna imagen de internet: se dibuja con Pillow y
se guarda directo en formato WEBP, que pesa bastante menos que un JPG/PNG
equivalente sin perder calidad visible).

Es idempotente: se puede correr mas de una vez sin duplicar datos,
porque busca por nombre antes de crear (get_or_create).

Uso:
    python manage.py seed_demo
"""
import hashlib
import io
import random

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image, ImageDraw, ImageFont

from blog.models import Blog
from productos.models import Artista, Categoria, Producto

# Paleta de colores de fondo para las portadas generadas. Se elige una
# pareja de colores de forma determinista a partir del texto (mismo
# titulo -> siempre la misma portada), asi que no hace falta guardar
# ninguna semilla aparte.
PALETA = [
    ("#E36236", "#1A1A1A"),
    ("#2E4057", "#F3EFE0"),
    ("#6A4C93", "#F3EFE0"),
    ("#1B998B", "#1A1A1A"),
    ("#C1292E", "#F3EFE0"),
    ("#3A506B", "#F3EFE0"),
    ("#8D5A97", "#F3EFE0"),
    ("#2A9D8F", "#1A1A1A"),
    ("#E76F51", "#1A1A1A"),
    ("#264653", "#F3EFE0"),
]


def _wrap(draw, texto, fuente, max_ancho):
    """Corta "texto" en varias lineas para que ninguna supere max_ancho
    al dibujarse con "fuente" (PIL no hace word-wrap solo)."""
    palabras = texto.split()
    lineas, actual = [], ""
    for palabra in palabras:
        prueba = f"{actual} {palabra}".strip()
        ancho = draw.textbbox((0, 0), prueba, font=fuente)[2]
        if ancho <= max_ancho or not actual:
            actual = prueba
        else:
            lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


def generar_portada(titulo, subtitulo="", tamano=(600, 600)):
    """Genera una imagen cuadrada simple (fondo de color + texto) y la
    devuelve como bytes WEBP, lista para guardar en un ImageField."""
    indice = int(hashlib.md5(titulo.encode("utf-8")).hexdigest(), 16) % len(PALETA)
    color_fondo, color_texto = PALETA[indice]

    img = Image.new("RGB", tamano, color_fondo)
    draw = ImageDraw.Draw(img)

    # Franja diagonal simple, solo para que no sea un cuadrado 100% plano.
    ancho, alto = tamano
    draw.polygon(
        [(0, alto), (ancho, 0), (ancho, alto * 0.25), (0, alto * 0.6)],
        fill=color_texto,
    )
    draw.rectangle([0, 0, ancho, alto], outline=color_texto, width=8)

    try:
        fuente_titulo = ImageFont.load_default(size=42)
        fuente_subtitulo = ImageFont.load_default(size=26)
    except TypeError:
        # Pillow viejo: load_default() no acepta "size".
        fuente_titulo = ImageFont.load_default()
        fuente_subtitulo = fuente_titulo

    margen = 40
    y = alto * 0.35
    for linea in _wrap(draw, titulo, fuente_titulo, ancho - margen * 2):
        draw.text((margen, y), linea, font=fuente_titulo, fill=color_texto)
        y += 52

    if subtitulo:
        y += 10
        for linea in _wrap(draw, subtitulo, fuente_subtitulo, ancho - margen * 2):
            draw.text((margen, y), linea, font=fuente_subtitulo, fill=color_texto)
            y += 32

    buffer = io.BytesIO()
    img.save(buffer, format="WEBP", quality=82)
    return buffer.getvalue()


# (artista, pais, categoria, album, descripcion breve)
CATALOGO = [
    ("Pink Floyd", "Reino Unido", "Rock", "The Dark Side of the Moon", "Album conceptual de 1973, uno de los mas vendidos de la historia."),
    ("Led Zeppelin", "Reino Unido", "Rock", "IV", "Cuarto disco de la banda, incluye 'Stairway to Heaven'."),
    ("Fleetwood Mac", "Reino Unido", "Rock", "Rumours", "Clasico de 1977 grabado en medio de las rupturas de la banda."),
    ("Queen", "Reino Unido", "Rock", "A Night at the Opera", "Disco que incluye 'Bohemian Rhapsody'."),
    ("The Beatles", "Reino Unido", "Rock", "Abbey Road", "Ultimo disco grabado por la banda, 1969."),
    ("David Bowie", "Reino Unido", "Rock", "The Rise and Fall of Ziggy Stardust", "Album conceptual glam rock de 1972."),
    ("Misfits", "Estados Unidos", "Punk Rock", "Walk Among Us", "Debut de 1982, referencia del horror punk."),
    ("Ramones", "Estados Unidos", "Punk Rock", "Ramones", "Debut de 1976, pionero del punk rock."),
    ("Sex Pistols", "Reino Unido", "Punk Rock", "Never Mind the Bollocks", "Unico disco de estudio de la banda, 1977."),
    ("The Clash", "Reino Unido", "Punk Rock", "London Calling", "Doble album de 1979, mezcla punk con reggae y rockabilly."),
    ("Dead Kennedys", "Estados Unidos", "Punk Rock", "Fresh Fruit for Rotting Vegetables", "Debut de 1980, punk hardcore con letras politicas."),
    ("Red Hot Chili Peppers", "Estados Unidos", "Funk Rock", "Californication", "Septimo disco de la banda, 1999."),
    ("Parliament", "Estados Unidos", "Funk Rock", "Mothership Connection", "Clasico del funk de 1975."),
    ("Sly and the Family Stone", "Estados Unidos", "Funk Rock", "There's a Riot Goin' On", "Album de 1971, funk experimental."),
    ("Rick James", "Estados Unidos", "Funk Rock", "Street Songs", "Disco de 1981, incluye 'Super Freak'."),
    ("Chic", "Estados Unidos", "Funk Rock", "Risque", "Album de 1979, incluye 'Good Times'."),
    ("Black Sabbath", "Reino Unido", "Metal", "Paranoid", "Segundo disco de la banda, 1970, pilar del heavy metal."),
    ("Metallica", "Estados Unidos", "Metal", "Master of Puppets", "Tercer disco de estudio, 1986."),
    ("Iron Maiden", "Reino Unido", "Metal", "The Number of the Beast", "Album de 1982 con Bruce Dickinson."),
    ("Slayer", "Estados Unidos", "Metal", "Reign in Blood", "Disco clave del thrash metal, 1986."),
    ("Judas Priest", "Reino Unido", "Metal", "Painkiller", "Disco de 1990, referencia del speed metal."),
    ("Nas", "Estados Unidos", "Hip-Hop", "Illmatic", "Debut de 1994, considerado un clasico del hip-hop."),
    ("Wu-Tang Clan", "Estados Unidos", "Hip-Hop", "Enter the Wu-Tang (36 Chambers)", "Debut de 1993."),
    ("A Tribe Called Quest", "Estados Unidos", "Hip-Hop", "The Low End Theory", "Segundo disco, 1991, mezcla jazz y hip-hop."),
    ("Kendrick Lamar", "Estados Unidos", "Hip-Hop", "To Pimp a Butterfly", "Tercer disco de estudio, 2015."),
    ("Public Enemy", "Estados Unidos", "Hip-Hop", "It Takes a Nation of Millions to Hold Us Back", "Disco de 1988, hip-hop politico."),
    ("Miles Davis", "Estados Unidos", "Jazz", "Kind of Blue", "Album de 1959, el disco de jazz mas vendido de la historia."),
    ("John Coltrane", "Estados Unidos", "Jazz", "A Love Supreme", "Album espiritual de 1965."),
    ("Herbie Hancock", "Estados Unidos", "Jazz", "Head Hunters", "Disco de 1973, fusion de jazz y funk."),
    ("Thelonious Monk", "Estados Unidos", "Jazz", "Brilliant Corners", "Disco de 1957."),
    ("Dave Brubeck", "Estados Unidos", "Jazz", "Time Out", "Album de 1959, incluye 'Take Five'."),
    ("Daft Punk", "Francia", "Electronica", "Discovery", "Segundo disco del duo, 2001."),
    ("Kraftwerk", "Alemania", "Electronica", "Trans-Europe Express", "Album de 1977, pionero de la musica electronica."),
    ("Aphex Twin", "Reino Unido", "Electronica", "Selected Ambient Works 85-92", "Compilado de 1992, referencia del ambient."),
    ("Justice", "Francia", "Electronica", "Cross", "Debut del duo frances, 2007."),
    ("Fatboy Slim", "Reino Unido", "Electronica", "You've Come a Long Way, Baby", "Disco de 1998, big beat."),
    ("Marvin Gaye", "Estados Unidos", "Soul", "What's Going On", "Album conceptual de 1971."),
    ("Aretha Franklin", "Estados Unidos", "Soul", "I Never Loved a Man the Way I Love You", "Disco de 1967."),
    ("Stevie Wonder", "Estados Unidos", "Soul", "Songs in the Key of Life", "Doble album de 1976."),
    ("Al Green", "Estados Unidos", "Soul", "Let's Stay Together", "Disco de 1972."),
    ("Otis Redding", "Estados Unidos", "Soul", "Otis Blue", "Disco de 1965."),
    ("Bob Marley & The Wailers", "Jamaica", "Reggae", "Legend", "Compilado de 1984, el mas vendido de reggae."),
    ("Peter Tosh", "Jamaica", "Reggae", "Legalize It", "Debut solista de 1976."),
    ("Toots and the Maytals", "Jamaica", "Reggae", "Funky Kingston", "Disco de 1973."),
    ("Burning Spear", "Jamaica", "Reggae", "Marcus Garvey", "Disco de 1975."),
    ("Michael Jackson", "Estados Unidos", "Pop", "Thriller", "Album de 1982, el mas vendido de la historia."),
    ("Madonna", "Estados Unidos", "Pop", "Like a Prayer", "Disco de 1989."),
    ("ABBA", "Suecia", "Pop", "Arrival", "Disco de 1976, incluye 'Dancing Queen'."),
    ("Prince", "Estados Unidos", "Pop", "Purple Rain", "Banda sonora de la pelicula homonima, 1984."),
    ("George Michael", "Reino Unido", "Pop", "Faith", "Debut solista de 1987."),
]

PRECIOS = [12990, 14990, 16990, 17990, 19990, 21990, 24990, 26990, 29990]

BLOGS_DEMO = [
    {
        "titulo": "Como cuidar tus discos de vinilo",
        "descripcion": "Consejos basicos para que tu coleccion dure toda la vida.",
        "contenido": (
            "Un vinilo bien cuidado puede sonar bien durante decadas. Estos son "
            "algunos cuidados basicos:\n\n"
            "1. Guardalos siempre en posicion vertical, nunca apilados uno "
            "sobre otro (el peso puede deformarlos).\n"
            "2. Limpia el disco con un cepillo antiestatico antes de cada "
            "reproduccion, para sacar el polvo antes de que raye el surco.\n"
            "3. Evita tocar la superficie con los dedos: la grasa de la piel "
            "atrae mas polvo. Sujetalo por el borde y la etiqueta central.\n"
            "4. Guardalos lejos de la luz solar directa y de fuentes de "
            "calor, que pueden deformar el vinilo.\n"
            "5. Usa fundas internas antiestaticas, no solo la funda de carton "
            "original.\n\n"
            "Con estos cuidados basicos, tu coleccion te va a acompanar "
            "muchos anos mas."
        ),
    },
    {
        "titulo": "Novedades en Vynil Store",
        "descripcion": "Ampliamos el catalogo: mas artistas, mas generos.",
        "contenido": (
            "Acabamos de ampliar bastante el catalogo de la tienda: ahora hay "
            "discos de rock, punk, funk, metal, hip-hop, jazz, electronica, "
            "soul, reggae y pop, de artistas clasicos de cada genero.\n\n"
            "La idea es que cualquiera que entre a la tienda encuentre algo "
            "de su estilo, ya sea que este empezando una coleccion o que "
            "lleve anos comprando vinilos.\n\n"
            "Como siempre, pueden filtrar por artista desde el buscador de "
            "arriba, y revisar el detalle de cada disco antes de agregarlo "
            "al carrito. Gracias por visitarnos."
        ),
    },
]


class Command(BaseCommand):
    help = "Puebla la base de datos con categorias, artistas, 50 productos y 2 posts de blog de ejemplo."

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(42)  # reproducible: mismos precios/stock cada vez que se corre en una base vacia

        creados_productos = 0
        for artista_nombre, pais, categoria_nombre, album, descripcion in CATALOGO:
            artista, _ = Artista.objects.get_or_create(
                nombre_artista=artista_nombre,
                defaults={"pais": pais},
            )
            categoria, _ = Categoria.objects.get_or_create(nombre=categoria_nombre)

            producto, creado = Producto.objects.get_or_create(
                nombre=album,
                artista=artista,
                defaults={
                    "categoria": categoria,
                    "descripcion": descripcion,
                    "precio": random.choice(PRECIOS),
                    "stock": random.randint(3, 40),
                    "activo": True,
                },
            )
            if creado:
                imagen_bytes = generar_portada(album, artista_nombre)
                nombre_archivo = f"{artista_nombre}-{album}.webp".lower().replace(" ", "-")
                producto.imagen.save(nombre_archivo, ContentFile(imagen_bytes), save=True)
                creados_productos += 1

        Usuario = get_user_model()
        autor = Usuario.objects.filter(is_superuser=True).order_by("id").first()
        if autor is None:
            autor = Usuario.objects.create_superuser(
                username="admin@vynilstore.local",
                email="admin@vynilstore.local",
                password="ChangeMe123!",
            )
            self.stdout.write(self.style.WARNING(
                "No habia ningun superusuario: se creo admin@vynilstore.local / ChangeMe123! como autor del blog."
            ))

        creados_blogs = 0
        for post in BLOGS_DEMO:
            blog, creado = Blog.objects.get_or_create(
                titulo=post["titulo"],
                defaults={
                    "descripcion": post["descripcion"],
                    "contenido": post["contenido"],
                    "autor": autor,
                    "activo": True,
                },
            )
            if creado:
                imagen_bytes = generar_portada(post["titulo"])
                nombre_archivo = post["titulo"].lower().replace(" ", "-") + ".webp"
                blog.imagen_portada.save(nombre_archivo, ContentFile(imagen_bytes), save=True)
                creados_blogs += 1

        self.stdout.write(self.style.SUCCESS(
            f"Listo: {creados_productos} productos nuevos (de {len(CATALOGO)} en el catalogo), "
            f"{creados_blogs} posts de blog nuevos (de {len(BLOGS_DEMO)})."
        ))
