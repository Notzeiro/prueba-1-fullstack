"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("usuarios/", include("usuarios.urls")),
    path("productos/", include("productos.urls")),
    path("blog/", include("blog.urls")),
    path("contacto/", include("contacto.urls")),
]

# Django no sirve archivos subidos por los usuarios (imagenes de
# productos, blog, etc.) a menos que se le indique explicitamente con
# esta linea. Lo normal es que en produccion esto lo haga un servidor
# web aparte (nginx, etc.), pero este despliegue es un contenedor unico
# sin sidecar de estaticos, asi que se sirve siempre, tambien con
# DEBUG=False. Para el volumen de trafico de este proyecto es aceptable.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
