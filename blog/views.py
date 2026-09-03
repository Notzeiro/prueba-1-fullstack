from django.shortcuts import render

from .models import Blog


def index(request):
    # Solo se muestran los posts marcados como activos (publicados).
    # Un post con activo=False existe en la base de datos pero no
    # aparece en la tienda (por ejemplo, un borrador sin terminar).
    posts = Blog.objects.filter(activo=True)
    return render(request, "blog/lista.html", {"posts": posts})
