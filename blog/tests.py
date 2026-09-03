from django.test import TestCase
from django.urls import reverse

from usuarios.models import Usuario

from .models import Blog


class BlogTest(TestCase):
    def setUp(self):
        self.autor = Usuario.objects.create_user(username="autor", email="autor@gmail.com")
        self.post_activo = Blog.objects.create(
            titulo="Post publicado",
            descripcion="Un resumen corto",
            contenido="Contenido completo del post.",
            autor=self.autor,
            imagen_portada="",
            activo=True,
        )
        self.post_borrador = Blog.objects.create(
            titulo="Post sin publicar",
            descripcion="Todavia no deberia verse",
            contenido="Borrador.",
            autor=self.autor,
            imagen_portada="",
            activo=False,
        )

    def test_listado_solo_muestra_posts_activos(self):
        respuesta = self.client.get(reverse("blog:index"))
        self.assertContains(respuesta, "Post publicado")
        self.assertNotContains(respuesta, "Post sin publicar")

    def test_detalle_de_post_activo(self):
        url = reverse("blog:detalle", args=[self.post_activo.pk])
        respuesta = self.client.get(url)
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Contenido completo del post.")

    def test_detalle_de_post_inactivo_da_404(self):
        url = reverse("blog:detalle", args=[self.post_borrador.pk])
        respuesta = self.client.get(url)
        self.assertEqual(respuesta.status_code, 404)
