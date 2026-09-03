from django.test import TestCase
from django.urls import reverse

from .models import Usuario


class RegistroTest(TestCase):
    def test_registro_crea_usuario_y_inicia_sesion(self):
        respuesta = self.client.post(reverse("usuarios:registro"), {
            "nombre": "Estudiante Prueba",
            "email": "estudiante@gmail.com",
            "password1": "ClaveSegura123",
            "password2": "ClaveSegura123",
        })

        # 302 = redireccion. Si el registro hubiera fallado, la vista
        # vuelve a mostrar el formulario (200) en vez de redirigir.
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(Usuario.objects.filter(email="estudiante@gmail.com").exists())

        usuario = Usuario.objects.get(email="estudiante@gmail.com")
        # check_password compara contra el hash guardado, nunca contra
        # texto plano: confirma que la contraseña se guardo hasheada
        # y que set_password() funciono bien.
        self.assertTrue(usuario.check_password("ClaveSegura123"))

        # La sesion deberia haber quedado iniciada automaticamente.
        respuesta_home = self.client.get(reverse("core:home"))
        self.assertContains(respuesta_home, "Estudiante Prueba")

    def test_no_permite_correos_duplicados(self):
        Usuario.objects.create_user(username="ya_existe@gmail.com", email="ya_existe@gmail.com")

        respuesta = self.client.post(reverse("usuarios:registro"), {
            "nombre": "Otra Persona",
            "email": "ya_existe@gmail.com",
            "password1": "ClaveSegura123",
            "password2": "ClaveSegura123",
        })

        # Si el formulario tiene errores, la vista vuelve a mostrar la
        # pagina (200), no redirige.
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Ya existe una cuenta registrada")
        # No se debe haber creado un segundo usuario con el mismo correo.
        self.assertEqual(Usuario.objects.filter(email="ya_existe@gmail.com").count(), 1)

    def test_contrasenas_distintas_no_pasan_la_validacion(self):
        respuesta = self.client.post(reverse("usuarios:registro"), {
            "nombre": "Otra Persona",
            "email": "nueva@gmail.com",
            "password1": "ClaveUno123",
            "password2": "ClaveDistinta456",
        })
        self.assertContains(respuesta, "Las contraseñas no coinciden")
        self.assertFalse(Usuario.objects.filter(email="nueva@gmail.com").exists())


class LoginTest(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="cliente@gmail.com",
            email="cliente@gmail.com",
            password="ClaveCorrecta123",
        )

    def test_login_correcto(self):
        respuesta = self.client.post(reverse("usuarios:login"), {
            "email": "cliente@gmail.com",
            "password": "ClaveCorrecta123",
        })
        self.assertEqual(respuesta.status_code, 302)

    def test_login_con_clave_incorrecta(self):
        respuesta = self.client.post(reverse("usuarios:login"), {
            "email": "cliente@gmail.com",
            "password": "clave-mala",
        })
        # No deberia redirigir: se queda en la misma pagina con el error.
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Correo o contraseña incorrectos")

    def test_logout_cierra_la_sesion(self):
        self.client.login(username="cliente@gmail.com", password="ClaveCorrecta123")
        self.client.get(reverse("usuarios:logout"))

        respuesta = self.client.get(reverse("core:home"))
        # Si la sesion se cerro bien, el navbar deberia volver a mostrar
        # "Iniciar sesión" en vez del nombre del usuario.
        self.assertContains(respuesta, "Iniciar sesión")
