from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Artista, Categoria, Producto


class ProductoModelTest(TestCase):
    # setUp() corre antes de CADA metodo de test de esta clase. Sirve
    # para dejar preparados los datos que varios tests van a necesitar,
    # sin repetir el mismo codigo en cada uno.
    def setUp(self):
        self.artista = Artista.objects.create(nombre_artista="Misfits")
        self.categoria = Categoria.objects.create(nombre="Punk Rock")
        self.producto = Producto.objects.create(
            nombre="Walk Among Us",
            artista=self.artista,
            categoria=self.categoria,
            precio=Decimal("89.90"),
            stock=10,
            imagen="",
        )

    def test_str_devuelve_el_nombre(self):
        # Verifica que __str__ este devolviendo lo esperado (el nombre
        # del producto), y no el "Producto object (1)" por defecto.
        self.assertEqual(str(self.producto), "Walk Among Us")

    def test_activo_por_defecto_es_true(self):
        # Un producto nuevo deberia quedar visible en la tienda salvo
        # que se indique lo contrario explicitamente.
        self.assertTrue(self.producto.activo)


class ProductoViewsTest(TestCase):
    def setUp(self):
        self.artista = Artista.objects.create(nombre_artista="Red Hot Chili Peppers")
        self.producto_activo = Producto.objects.create(
            nombre="Californication",
            artista=self.artista,
            precio=Decimal("95.50"),
            stock=5,
            imagen="",
            activo=True,
        )
        self.producto_inactivo = Producto.objects.create(
            nombre="Producto descontinuado",
            artista=self.artista,
            precio=Decimal("10.00"),
            stock=0,
            imagen="",
            activo=False,
        )

    def test_listado_muestra_solo_productos_activos(self):
        respuesta = self.client.get(reverse("productos:index"))
        self.assertEqual(respuesta.status_code, 200)
        # assertContains busca un texto dentro del HTML de respuesta.
        self.assertContains(respuesta, "Californication")
        # assertNotContains confirma que el producto inactivo NO aparece
        # en el listado publico.
        self.assertNotContains(respuesta, "Producto descontinuado")

    def test_buscador_filtra_por_nombre(self):
        respuesta = self.client.get(reverse("productos:index"), {"q": "californ"})
        self.assertContains(respuesta, "Californication")

    def test_buscador_filtra_por_artista(self):
        respuesta = self.client.get(reverse("productos:index"), {"q": "red hot"})
        self.assertContains(respuesta, "Californication")

    def test_buscador_sin_resultados(self):
        respuesta = self.client.get(reverse("productos:index"), {"q": "no-deberia-existir"})
        self.assertContains(respuesta, "No se encontraron productos")

    def test_detalle_de_producto_existente(self):
        url = reverse("productos:detalle", args=[self.producto_activo.pk])
        respuesta = self.client.get(url)
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Californication")

    def test_detalle_de_producto_inexistente_da_404(self):
        url = reverse("productos:detalle", args=[9999])
        respuesta = self.client.get(url)
        self.assertEqual(respuesta.status_code, 404)

    def test_detalle_de_producto_inactivo_da_404(self):
        # Un producto desactivado no deberia poder verse ni siquiera
        # accediendo directo a su URL de detalle.
        url = reverse("productos:detalle", args=[self.producto_inactivo.pk])
        respuesta = self.client.get(url)
        self.assertEqual(respuesta.status_code, 404)
