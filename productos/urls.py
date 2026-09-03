from django.urls import path
from . import views

app_name = "productos"

urlpatterns = [
    # /productos/  -> listado de todos los productos
    path("", views.index, name="index"),
    # /productos/5/  -> detalle del producto con id=5.
    # <int:pk> le dice a Django: toma el numero de la URL, conviertelo a
    # entero, y pasaselo a la vista detalle() como el parametro "pk".
    path("<int:pk>/", views.detalle, name="detalle"),
]