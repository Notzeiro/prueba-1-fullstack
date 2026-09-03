from django.urls import path
from . import views

# app_name crea un "espacio de nombres": permite usar {% url 'core:home' %}
# en las plantillas en vez de {% url 'home' %} a secas, evitando choques
# si dos apps distintas usan el mismo nombre de ruta (ej. dos "index").
app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("nosotros/", views.nosotros, name="nosotros"),
    path("carrito/", views.carrito, name="carrito"),
]