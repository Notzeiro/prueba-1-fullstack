from django.shortcuts import render

from .models import Blog


def index(request):
    posts = Blog.objects.filter(activo=True)
    return render(request, "blog/lista.html", {"posts": posts})
