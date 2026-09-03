from django.test import TestCase
from django.urls import reverse

from .models import Contacto


class ContactoTest(TestCase):
    def test_formulario_valido_guarda_el_mensaje(self):
        respuesta = self.client.post(reverse("contacto:index"), {
            "nombre": "Juan Perez",
            "correo": "juan@gmail.com",
            "asunto": "Consulta de stock",
            "mensaje": "Hola, queria saber si tienen mas stock de Misfits.",
        })

        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(Contacto.objects.count(), 1)

        mensaje = Contacto.objects.first()
        self.assertEqual(mensaje.nombre, "Juan Perez")
        # Todo mensaje nuevo deberia arrancar sin revisar.
        self.assertFalse(mensaje.revisado)

    def test_correo_invalido_no_se_guarda(self):
        respuesta = self.client.post(reverse("contacto:index"), {
            "nombre": "Juan Perez",
            "correo": "esto-no-es-un-correo",
            "asunto": "Consulta",
            "mensaje": "Mensaje de prueba.",
        })

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Contacto.objects.count(), 0)

    def test_campos_vacios_no_se_guardan(self):
        respuesta = self.client.post(reverse("contacto:index"), {
            "nombre": "",
            "correo": "",
            "asunto": "",
            "mensaje": "",
        })

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Contacto.objects.count(), 0)
