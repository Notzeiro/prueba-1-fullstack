from django.shortcuts import render

from productos.models import Producto


def home(request):
    productos_destacados = Producto.objects.filter(activo=True)[:8]
    return render(request, "core/home.html", {"productos": productos_destacados})


def nosotros(request):
    # Lista fija (no viene de la base de datos) con el equipo del proyecto.
    # Se pasa como contexto para que el template la recorra con {% for %},
    # en vez de escribir 4 bloques de HTML iguales a mano.
    equipo = [
        {"nombre": "Esteban", "rol": "Desarrollo backend / base de datos"},
        {"nombre": "Javier", "rol": "Desarrollo frontend"},
        {"nombre": "Héctor", "rol": "Integración y control de versiones"},
        {"nombre": "Miguel", "rol": "Desarrollo frontend"},
    ]
    return render(request, "core/nosotros.html", {"equipo": equipo})


def carrito(request):
    # Esta vista no consulta la base de datos: el contenido del carrito
    # vive en localStorage, en el navegador de quien esta comprando.
    # static/js/carrito.js es el que realmente dibuja los productos
    # dentro de esta pagina, una vez que el HTML ya cargo.
    return render(request, "core/carrito.html")