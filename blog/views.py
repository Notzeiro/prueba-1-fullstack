from django.shortcuts import get_object_or_404, render

from .models import Blog


def index(request):
    # Solo se muestran los posts marcados como activos (publicados).
    # Un post con activo=False existe en la base de datos pero no
    # aparece en la tienda (por ejemplo, un borrador sin terminar).
    posts = Blog.objects.filter(activo=True)
    return render(request, "blog/lista.html", {"posts": posts})


def detalle(request, pk):
    # Igual que en productos: si el id no existe o el post no esta
    # activo, get_object_or_404 devuelve una pagina 404 automaticamente.
    post = get_object_or_404(Blog, pk=pk, activo=True)
    return render(request, "blog/detalle.html", {"post": post})
