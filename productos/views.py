from django.shortcuts import render


def index(request):
    return render(request, "productos/lista.html")


def detalle(request, pk):
    # TODO: reemplazar por la consulta real: Producto.objects.get(pk=pk)
    return render(request, "productos/detalle.html")