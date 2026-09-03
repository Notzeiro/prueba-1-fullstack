from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Producto


def index(request):
    productos = Producto.objects.filter(activo=True)

    # request.GET.get('q') lee el parametro "q" de la URL (por ejemplo,
    # /productos/?q=metallica). Si el buscador del navbar no se uso,
    # este valor viene vacio y no se aplica ningun filtro extra.
    busqueda = request.GET.get("q", "").strip()

    if busqueda:
        # Q permite combinar condiciones con "o" (aca: que el termino
        # buscado aparezca en el nombre del producto, O en el nombre del
        # artista). icontains = "contains" sin distinguir mayusculas.
        productos = productos.filter(
            Q(nombre__icontains=busqueda) | Q(artista__nombre_artista__icontains=busqueda)
        )

    return render(request, "productos/lista.html", {"productos": productos, "busqueda": busqueda})


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
