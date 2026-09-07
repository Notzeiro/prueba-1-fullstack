from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.templatetags.static import static

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

    # Góndola "Más de <artista>": otros discos del mismo artista.
    relacionados = Producto.objects.filter(
        artista=producto.artista, activo=True
    ).exclude(pk=producto.pk)[:4]

    # Góndola "Más de <categoría>": otros discos de la misma categoría
    # (si el producto no tiene categoría asignada, no se muestra nada).
    misma_categoria = (
        Producto.objects.filter(categoria=producto.categoria, activo=True)
        .exclude(pk=producto.pk)[:4]
        if producto.categoria_id
        else Producto.objects.none()
    )

    # Fotos del carrusel: primero la portada (si tiene), despues las
    # fotos de galeria cargadas en ImagenProducto (ordenadas por "orden").
    # Si el producto no tiene ninguna foto, se muestra solo el dibujo de
    # "disco no encontrado" como unico elemento del carrusel.
    urls_galeria = []
    if producto.imagen:
        urls_galeria.append(producto.imagen.url)
    urls_galeria += [foto.imagen.url for foto in producto.imagenes.all()]
    if not urls_galeria:
        urls_galeria = [static("img/DiscoNoEncontrado.jpg")]

    return render(
        request,
        "productos/detalle.html",
        {
            "producto": producto,
            "relacionados": relacionados,
            "misma_categoria": misma_categoria,
            "urls_galeria": urls_galeria,
        },
    )
