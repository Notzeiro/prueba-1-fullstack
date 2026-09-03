# Cómo funciona el código — Vinyl Hub

Este documento explica la arquitectura del proyecto y el recorrido completo del código, para que cualquiera del equipo pueda entender y explicar cualquier parte. Está pensado para leerse junto al código real del repositorio.

## 1. Arquitectura general

El proyecto es una aplicación **Django** (Python) conectada a una base de datos **PostgreSQL**. Django sigue el patrón MTV (Model-Template-View), una variante del clásico MVC:

- **Model** (`models.py`) — define la estructura de las tablas de la base de datos, como clases de Python.
- **Template** (archivos `.html` en `templates/`) — define cómo se ve cada página.
- **View** (`views.py`) — es el intermediario: recibe la petición HTTP, consulta los modelos si hace falta, y decide qué template renderizar y con qué datos.

El recorrido de una petición siempre es:

```
Usuario visita una URL
        ↓
config/urls.py decide a qué app pertenece esa URL
        ↓
<app>/urls.py decide qué funcion de views.py ejecutar
        ↓
<app>/views.py hace su trabajo (a veces consulta la base con models.py)
        ↓
Se renderiza un template, pasándole los datos como "contexto"
        ↓
El HTML final se le manda al navegador
```

## 2. Las apps del proyecto

El proyecto está dividido en 5 apps de Django, cada una responsable de una parte del sitio:

| App | Responsabilidad |
|---|---|
| `core` | Home, Nosotros, Carrito (páginas generales que no encajan en otra app) |
| `usuarios` | Modelo de usuario personalizado, login, registro, logout |
| `productos` | Catálogo: artistas, categorías, productos (vinilos) |
| `blog` | Publicaciones del blog |
| `contacto` | Formulario de contacto |

Cada app tiene la misma estructura interna:

```
mi_app/
    models.py       -> las tablas de esta app
    views.py        -> la lógica de cada página
    urls.py         -> qué URL ejecuta qué view
    forms.py        -> formularios con validación (si la app lo necesita)
    admin.py        -> cómo se ve esta app en el panel de Django
    migrations/     -> el historial de cambios a las tablas
```

Y las plantillas HTML de todas las apps viven juntas en una sola carpeta, `templates/`, organizadas en subcarpetas por app (`templates/productos/`, `templates/blog/`, etc.), más un `templates/base.html` compartido por todos.

## 3. El archivo central: `config/settings.py`

Es la configuración global del proyecto. Las líneas más importantes:

```python
load_dotenv()
```
Carga las variables del archivo `.env` (que no se sube a git) como si fueran variables de entorno del sistema operativo. Así, `os.getenv('DB_PASSWORD')` puede leer la contraseña real sin que esté escrita en el código.

```python
INSTALLED_APPS = [..., "core", "usuarios", "productos", "blog", "contacto"]
```
Le dice a Django qué apps existen en el proyecto. Si una app no está en esta lista, Django ignora sus modelos por completo (no crea sus tablas, no la reconoce).

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        ...
    }
}
```
Le dice a Django que la base de datos es PostgreSQL, y de dónde sacar las credenciales (del `.env`, nunca escritas directamente acá).

```python
AUTH_USER_MODEL = "usuarios.Usuario"
```
Le dice a Django que use el modelo `Usuario` personalizado (el que está en `usuarios/models.py`) en vez del modelo de usuario genérico que trae Django por defecto. **Esto tiene que estar configurado antes de la primera migración** — cambiarlo después de tener datos reales requiere borrar la base y empezar de nuevo.

```python
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
```
Define dónde se guardan (`MEDIA_ROOT`, una carpeta física) y desde qué URL se acceden (`MEDIA_URL`) los archivos que suben los usuarios (imágenes de productos, del blog, etc.) — distinto de `static/`, que es para archivos que ya vienen con el proyecto (CSS, JS, imágenes fijas).

## 4. Los modelos (`models.py`) — el diseño de la base de datos

### `usuarios/models.py` — `Usuario`

Extiende `AbstractUser` de Django (que ya trae usuario, contraseña hasheada, permisos) y le agrega:
- `run`, `direccion`, `region`, `comuna` — datos personales
- `rol` — con 3 valores posibles definidos en `Usuario.Rol` (cliente, vendedor, administrador)
- `fecha_nacimiento` — opcional

### `productos/models.py` — `Artista`, `Categoria`, `Producto`

- `Artista` y `Categoria` son tablas simples, sin relaciones hacia afuera.
- `Producto` tiene dos `ForeignKey`: a `Artista` (obligatorio) y a `Categoria` (opcional, `null=True`). Cada producto tiene nombre, descripción, precio, stock, imagen, y un flag `activo` para poder "ocultarlo" de la tienda sin borrarlo.

### `blog/models.py` — `Blog`, `ImagenBlog`

`Blog` tiene un `ForeignKey` a `settings.AUTH_USER_MODEL` (el autor). `ImagenBlog` permite que un post tenga una galería de varias imágenes además de la portada.

### `contacto/models.py` — `Contacto`

Tabla independiente, sin relaciones — cualquiera puede enviar un mensaje sin estar registrado.

### El flujo de una migración

Cada vez que se **crea o modifica** un modelo, hay que correr:

```bash
python manage.py makemigrations   # genera el archivo de migración (el "plan de cambios")
python manage.py migrate          # aplica ese plan a la base de datos real
```

Los archivos de migración (`*/migrations/0001_initial.py`, etc.) **sí se suben a git** — son el historial versionado de cómo evolucionó la estructura de la base de datos.

## 5. Las vistas (`views.py`) — la lógica de cada página

### Vistas simples de solo lectura

Ejemplo, `productos/views.py`:

```python
def index(request):
    productos = Producto.objects.filter(activo=True)
    return render(request, "productos/lista.html", {"productos": productos})
```

- `Producto.objects.filter(activo=True)` — el ORM de Django traduce esto a SQL (`SELECT * FROM productos_producto WHERE activo = true`) sin que se escriba SQL a mano.
- `render(request, template, contexto)` — junta la plantilla HTML con los datos (el diccionario `{"productos": productos}`, llamado "contexto") y devuelve el HTML final.

```python
def detalle(request, pk):
    producto = get_object_or_404(Producto, pk=pk, activo=True)
    ...
```

`get_object_or_404` busca un solo registro por su llave primaria (`pk`, el número que viene en la URL); si no existe, automáticamente devuelve una página 404 en vez de romper con un error.

### Vistas que procesan formularios (patrón GET/POST)

Ejemplo, `contacto/views.py`:

```python
def index(request):
    if request.method == "POST":
        form = ContactoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "...")
            return redirect("contacto:index")
    else:
        form = ContactoForm()
    return render(request, "contacto/formulario.html", {"form": form})
```

Este patrón se repite en `usuarios/views.py` (login y registro) y es la base de casi cualquier formulario en Django:

1. Si la petición es **GET** (la persona recién entró a la página), se muestra el formulario vacío.
2. Si es **POST** (la persona envió el formulario), se valida. Si es válido, se guarda y se redirige. Si no, se vuelve a mostrar el mismo formulario con los errores marcados.
3. **Por qué se redirige después de un POST exitoso** (patrón Post/Redirect/Get): si no se redirigiera y la persona recargara la página, el navegador reenviaría el mismo formulario y se duplicaría el envío.

### Autenticación (`usuarios/views.py`)

```python
usuario = authenticate(request, username=email, password=password)
if usuario is not None:
    login(request, usuario)
```

- `authenticate()` verifica las credenciales contra la base de datos (compara el hash de la contraseña, nunca la contraseña en texto plano) y devuelve el objeto `Usuario` si son correctas, o `None` si no.
- `login()` crea la sesión: guarda una cookie en el navegador que Django usa para reconocer a esa persona en las siguientes peticiones, sin que tenga que loguearse en cada página.
- `logout()` hace lo opuesto: destruye la sesión.

Como el registro usa el correo como `username` (no se le pide un nombre de usuario aparte), el login también autentica con `username=email`.

```python
usuario.set_password(datos["password1"])
```

**Nunca se hace `usuario.password = "..."` directo** — eso guardaría la contraseña en texto plano. `set_password()` la pasa primero por un algoritmo de hasheo (PBKDF2, el que usa Django por defecto) antes de guardarla.

## 6. Los formularios (`forms.py`) — validación del lado del servidor

### `usuarios/forms.py`

`RegistroForm` es un `forms.Form` (no `ModelForm`) porque pide menos campos de los que tiene el modelo `Usuario` completo. Tiene dos tipos de validación:

- `clean_email(self)` — valida un campo específico (que el correo no esté repetido). Django ejecuta automáticamente cualquier método `clean_<nombre_de_campo>` que exista.
- `clean(self)` — se ejecuta al final, para validaciones que dependen de más de un campo (que las dos contraseñas sean iguales).

### `contacto/forms.py`

`ContactoForm` es un `ModelForm`: en vez de declarar los campos a mano, los genera automáticamente a partir del modelo `Contacto` (`fields = ["nombre", "correo", "asunto", "mensaje"]`). Esto evita repetir la misma definición de campos en dos lugares (el modelo y el formulario).

## 7. Las plantillas (`templates/`) — cómo se arma el HTML

### Herencia de plantillas

`templates/base.html` es el "molde" que comparten todas las páginas: header (navbar), footer, y un hueco vacío en el medio marcado con `{% block content %}{% endblock %}`.

Cada página específica hace:

```django
{% extends "base.html" %}

{% block content %}
    <!-- lo único que cambia en esta página -->
{% endblock %}
```

Esto evita repetir el navbar y el footer en cada archivo — si se cambia el logo, se cambia en un solo lugar.

También existen los bloques opcionales `{% block extra_css %}` y `{% block extra_js %}` en `base.html`, para que una página pueda agregar su propio CSS/JS sin tocar el archivo base.

### Cómo llegan los datos de la base al HTML

```django
{% for producto in productos %}
    <p>{{ producto.nombre }} - ${{ producto.precio }}</p>
{% endfor %}
```

- `productos` es la variable que la vista pasó en el contexto (`render(request, template, {"productos": productos})`).
- `{% for %}` recorre la lista, un objeto `Producto` a la vez.
- `{{ producto.nombre }}` imprime el valor de ese campo para el objeto actual del loop.

### Formularios en las plantillas

```django
<form method="post">
    {% csrf_token %}
    ...
</form>
```

`{% csrf_token %}` es obligatorio en todo formulario POST: genera un token oculto que Django verifica al recibir el formulario, para confirmar que el envío vino realmente del sitio y no de un ataque externo (CSRF = Cross-Site Request Forgery).

### Mostrar errores y mensajes

```django
{% if form.email.errors %}<div class="text-danger">{{ form.email.errors }}</div>{% endif %}
```
Muestra los errores de validación de un campo específico, si los hay.

```django
{% if messages %}
    {% for message in messages %}
        <div class="alert alert-{{ message.tags }}">{{ message }}</div>
    {% endfor %}
{% endif %}
```
El framework de mensajes de Django (`django.contrib.messages`) permite que una vista deje un mensaje (`messages.success(request, "...")`) que se muestra una sola vez, en la página a la que se redirige después.

## 8. Las URLs (`urls.py`) — cómo se conectan las rutas

`config/urls.py` es el punto de entrada: reparte cada prefijo de URL a la app correspondiente.

```python
path("productos/", include("productos.urls")),
```
Todo lo que empiece con `/productos/` se delega al `urls.py` de la app `productos`.

Dentro de cada app:

```python
app_name = "productos"

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:pk>/", views.detalle, name="detalle"),
]
```

- `app_name` crea un espacio de nombres: en las plantillas se usa `{% url 'productos:detalle' producto.id %}` en vez de escribir la URL a mano (`/productos/5/`). Si el día de mañana cambia la estructura de URLs, no hay que buscar y reemplazar en todos los templates.
- `<int:pk>` captura un número de la URL y se lo pasa a la vista como parámetro.

## 9. El panel de administración (`admin.py`)

Django trae un panel de administración funcional con solo registrar los modelos:

```python
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "artista", "categoria", "precio", "stock", "activo")
    list_filter = ("activo", "categoria", "artista")
```

- `list_display` — qué columnas se ven en el listado.
- `list_filter` — agrega filtros rápidos a la derecha del listado.
- `search_fields` — habilita la caja de búsqueda del admin.
- `list_editable` — permite editar un campo directo desde el listado, sin entrar al detalle.

Para `Usuario`, el admin no se registra "a secas": se hereda de `UserAdmin` (la clase que Django usa para su propio modelo de usuario), porque `UserAdmin` sabe manejar el campo de contraseña de forma segura (mostrar un link para cambiarla en vez de un campo de texto plano editable).

## 10. El carrito de compras (`static/js/carrito.js`)

A diferencia de todo lo anterior, el carrito **no usa la base de datos ni Django**: es JavaScript puro que corre en el navegador, guardando los datos en `localStorage` (un almacenamiento del navegador que persiste aunque se cierre la pestaña).

Flujo:

1. **Agregar** — un botón con la clase `.btn-add-cart` o `.btn-agregar-carrito` y atributos `data-producto-id`, `data-producto-nombre`, `data-producto-precio` (rellenados por la plantilla Django con los datos reales del producto). Al hacer click, `agregarAlCarrito()` lee esos atributos y los guarda en `localStorage`.
2. **Mostrar el contador** — `actualizarContadorCarrito()` recorre el carrito guardado y actualiza el número en el ícono del navbar, en cualquier página (porque el navbar está en `base.html`, que se carga siempre).
3. **Ver el carrito completo** — en la página `/carrito/`, `renderizarCarrito()` busca un `<div id="carrito-contenedor">` (que solo existe en esa página) y dibuja ahí la lista de productos con sus cantidades y el total.
4. **Quitar / cambiar cantidad** — `eliminarDelCarrito()` y `cambiarCantidad()` modifican el arreglo guardado y vuelven a dibujar todo.

Como vive en el navegador, cada persona/dispositivo tiene su propio carrito — no se comparte entre sesiones ni queda registrado en el servidor.

## 11. Cómo levantar el entorno completo (resumen técnico)

```bash
python manage.py makemigrations   # detecta cambios en los modelos
python manage.py migrate          # aplica esos cambios a PostgreSQL
python manage.py createsuperuser  # crea un usuario admin
python manage.py runserver        # levanta el servidor de desarrollo
```

Para más detalle de instalación paso a paso, ver `GUIA_DE_USO.md`.

## 12. El buscador (`productos/views.py`)

```python
busqueda = request.GET.get("q", "").strip()
if busqueda:
    productos = productos.filter(
        Q(nombre__icontains=busqueda) | Q(artista__nombre_artista__icontains=busqueda)
    )
```

`request.GET.get("q", "")` lee el parámetro `q` de la URL (el que manda el formulario del navbar por método GET, ej. `/productos/?q=misfits`). `Q(...) | Q(...)` combina dos condiciones con "o": el término buscado puede coincidir con el nombre del producto **o** con el nombre del artista. `icontains` es "contiene, sin distinguir mayúsculas/minúsculas".

## 13. Páginas de error personalizadas (`403.html`, `404.html`, `500.html`)

Django busca automáticamente plantillas con estos nombres exactos en la raíz de `templates/` (no dentro de una subcarpeta de app) y las usa **solo cuando `DEBUG=False`**. Con `DEBUG=True` (modo desarrollo), Django muestra su página de error detallada con el traceback en vez de estas, a propósito, para facilitar debuggear.

Un detalle importante: `500.html` **no** hereda de `base.html` como las otras. Si el servidor ya está fallando con un error interno, no conviene depender de todo el sistema de plantillas (que podría ser parte del problema) — por eso `500.html` es HTML plano y autocontenido.

Para probar estas páginas localmente hace falta forzar `DEBUG=False` temporalmente (por ejemplo, poniendo `DJANGO_DEBUG=False` en el `.env` un momento) y correr `python manage.py collectstatic` al menos una vez, porque con `DEBUG=False` Django deja de servir archivos estáticos automáticamente con `runserver`.

## 14. Tests automatizados (`tests.py` de cada app)

Los tests usan `django.test.TestCase`, que crea una **base de datos de prueba separada** (una copia vacía de la estructura, sin los datos reales) antes de correr, y la borra al terminar — por eso no hay riesgo de que los tests toquen los datos verdaderos de `vinyl_hub`.

Patrón típico de un test:

```python
def test_login_correcto(self):
    respuesta = self.client.post(reverse("usuarios:login"), {
        "email": "cliente@gmail.com",
        "password": "ClaveCorrecta123",
    })
    self.assertEqual(respuesta.status_code, 302)
```

- `self.client` simula un navegador real, sin necesidad de levantar el servidor.
- `reverse("usuarios:login")` obtiene la URL real a partir del nombre de la ruta (lo mismo que `{% url %}` en los templates, pero para usar en Python).
- `self.assertEqual(...)`, `self.assertContains(...)`, `self.assertTrue(...)` son las "afirmaciones": si lo que se espera no se cumple, el test falla y muestra qué esperaba versus qué recibió.

`setUp(self)` es un método especial que corre automáticamente **antes de cada test** de una clase, para dejar preparados los datos que esos tests van a necesitar (evita repetir el mismo código de armado en cada test).

Para correr todos los tests del proyecto:

```bash
python manage.py test
```

**Nota:** correr tests requiere que el usuario de PostgreSQL (`tienda_user`) tenga permiso para crear bases de datos (`CREATEDB`), porque Django necesita crear la base de prueba temporal. Si da un error de permisos al correr `manage.py test`, hay que conectarse como superusuario de Postgres y ejecutar `ALTER USER tienda_user CREATEDB;`.

## 15. Cosas que todavía quedan pendientes (para que quede registrado)

- Vista propia de administración (más allá del admin de Django) — puntos 14-18 del checklist, opcional según lo conversado con el profesor.
- Más datos de prueba (el checklist pide mínimo 8-12 productos, ahora hay 2).
- Recuperar contraseña.
- Filtro por categoría y orden por precio en el listado de productos (mejoras opcionales del checklist).
- Paginación del listado de productos y del blog.
