from django.shortcuts import render

from productos.models import Producto


def home(request):
    productos_destacados = Producto.objects.filter(activo=True)[:8]
    return render(request, "core/home.html", {"productos": productos_destacados})