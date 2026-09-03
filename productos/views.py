from django.shortcuts import get_object_or_404, render

from .models import Producto


def index(request):
    productos = Producto.objects.filter(activo=True)
    return render(request, "productos/lista.html", {"productos": productos})


def detalle(request, pk):
    producto = get_object_or_404(Producto, pk=pk, activo=True)
    relacionados = Producto.objects.filter(
        artista=producto.artista, activo=True
    ).exclude(pk=producto.pk)[:4]
    return render(
        request,
        "productos/detalle.html",
        {"producto": producto, "relacionados": relacionados},
    )
