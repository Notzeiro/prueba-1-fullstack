from django.http import HttpResponse


def index(request):
    return HttpResponse("Productos funcionando")


def detalle(request, pk):
    # TODO: reemplazar por la consulta real: Producto.objects.get(pk=pk)
    return HttpResponse(f"Detalle del producto {pk} (pendiente de conectar a la base de datos)")