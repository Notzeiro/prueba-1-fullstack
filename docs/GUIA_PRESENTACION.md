# Guía para la presentación — dónde está cada cosa en el código

Este documento está pensado para usarlo EN VIVO durante la presentación: está
organizado en el mismo orden en que probablemente van a recorrer la página
(Home → Productos → Detalle → Carrito → Login → Blog → Contacto → Admin).
Cada sección dice **qué le muestras al profe en pantalla**, **en qué
archivo(s) está el código** (con línea), pega el **fragmento real**, y
termina con una frase corta para decir en voz alta.

Dos documentos hermanos, para no repetir contenido acá:
- [`DETALLE_PRODUCTO_Y_CONEXION_BD.md`](./DETALLE_PRODUCTO_Y_CONEXION_BD.md) — explica a fondo la conexión a PostgreSQL, el recorrido completo de una petición, el panel admin (`admin.py`) y el sistema de login. Acá solo va un resumen con lo esencial de cada uno.
- [`DESPLIEGUE.md`](./DESPLIEGUE.md) — cómo y dónde está desplegado el sitio (Docker, servidor, dominio).

---

## Índice rápido (para saltar directo cuando pregunten)

| Si preguntan por... | Vas a la sección |
|---|---|
| Home / destacados | [1](#1-home-) |
| Catálogo, buscador | [2](#2-catálogo-de-productos-productos) |
| Detalle de un producto | [3](#3-detalle-de-producto-productosid) |
| Carrusel de fotos | [3.2](#32-carrusel-de-fotos) |
| Imagen "no encontrado" / fallback | [3.3](#33-imagen-de-reemplazo-cuando-no-hay-foto) |
| RC / Discogs | [3.4](#34-rc-y-la-api-de-discogs) |
| Carrito de compras | [4](#4-carrito-de-compras-carrito) |
| Login / Registro | [5](#5-login--registro--logout-usuarios) |
| Blog | [6](#6-blog-blog) |
| Contacto | [7](#7-contacto-contacto) |
| Panel admin | [8](#8-panel-de-administración-admin) |
| Base de datos / Docker | [9](#9-base-de-datos-y-despliegue) |

---

## 1. Home (`/`)

**Le muestras:** la página de inicio, con el banner y los "Destacados".

**Código:**

[`core/views.py:6-8`](../core/views.py)
```python
def home(request):
    productos_destacados = Producto.objects.filter(activo=True)[:8]
    return render(request, "core/home.html", {"productos": productos_destacados})
```

[`templates/core/home.html:25-45`](../templates/core/home.html) (recorre esos 8 productos):
```html
{% for producto in productos %}
<div class="product-card">
    <div class="product-image">
        {% if producto.imagen %}
            <img src="{{ producto.imagen.url }}" alt="{{ producto.nombre }}">
        {% else %}
            <img src="{% static 'img/DiscoNoEncontrado.jpg' %}" alt="{{ producto.nombre }}">
        {% endif %}
    </div>
    ...
</div>
{% endfor %}
```

**Cómo explicarlo:** "La vista `home` trae los primeros 8 productos activos de la base de datos con el ORM (`Producto.objects.filter(activo=True)[:8]`) y el template los recorre con un `{% for %}` — es el mismo patrón de tarjeta que se repite en todo el sitio."

---

## 2. Catálogo de productos (`/productos/`)

**Le muestras:** el listado completo, y el buscador de arriba a la derecha.

**Código — la vista con el buscador:**

[`productos/views.py:8-24`](../productos/views.py)
```python
def index(request):
    productos = Producto.objects.filter(activo=True)

    busqueda = request.GET.get("q", "").strip()

    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) | Q(artista__nombre_artista__icontains=busqueda)
        )

    return render(request, "productos/lista.html", {"productos": productos, "busqueda": busqueda})
```

**El buscador del navbar** (está en `base.html`, se ve en todas las páginas) apunta a esta misma vista:
```html
<form class="d-flex" role="search" method="get" action="{% url 'productos:index' %}">
    <input class="form-control" type="search" name="q" placeholder="Buscar productos...">
</form>
```

**Cómo explicarlo:** "El buscador no es JavaScript ni una API aparte: es un `<form method='get'>` normal que manda `?q=lo que escribiste` a la misma URL `/productos/`. La vista lee ese parámetro con `request.GET.get('q')` y, si viene algo, filtra la consulta con `Q(...)` — busca coincidencias en el nombre del producto **o** en el nombre del artista, sin importar mayúsculas (`icontains`)."

---

## 3. Detalle de producto (`/productos/<id>/`)

**Le muestras:** entrás a un disco cualquiera desde el catálogo.

### 3.1 — La vista

[`productos/views.py:27-64`](../productos/views.py)
```python
def detalle(request, pk):
    producto = get_object_or_404(Producto, pk=pk, activo=True)

    relacionados = Producto.objects.filter(
        artista=producto.artista, activo=True
    ).exclude(pk=producto.pk)[:4]

    misma_categoria = (
        Producto.objects.filter(categoria=producto.categoria, activo=True)
        .exclude(pk=producto.pk)[:4]
        if producto.categoria_id
        else Producto.objects.none()
    )

    urls_galeria = []
    if producto.imagen:
        urls_galeria.append(producto.imagen.url)
    urls_galeria += [foto.imagen.url for foto in producto.imagenes.all()]
    if not urls_galeria:
        urls_galeria = [static("img/DiscoNoEncontrado.jpg")]

    return render(request, "productos/detalle.html", {
        "producto": producto,
        "relacionados": relacionados,
        "misma_categoria": misma_categoria,
        "urls_galeria": urls_galeria,
    })
```

**Cómo explicarlo:** "`get_object_or_404` trae el producto por su `id` (`pk` en la URL) — si no existe, Django responde 404 solo. Después arma 3 cosas más: los discos relacionados por artista, los de la misma categoría, y la lista de fotos del carrusel." (El recorrido completo URL → vista → ORM → template está detallado en `DETALLE_PRODUCTO_Y_CONEXION_BD.md`, sección 3.)

### 3.2 — Carrusel de fotos

**Modelo** — cada producto puede tener varias fotos de galería, además de la portada:

[`productos/models.py`](../productos/models.py) (clase `ImagenProducto`)
```python
class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='img/productos/galeria/')
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden']
```

**Template** — pinta la imagen grande + las miniaturas:

[`templates/productos/detalle.html`](../templates/productos/detalle.html)
```html
<div class="main-image">
    <img id="imagenPrincipal" src="{{ urls_galeria.0 }}" alt="{{ producto.nombre }}">
</div>
<div class="thumbnails-container" id="thumbnailsContainer">
    {% for url in urls_galeria %}
    <img src="{{ url }}" class="thumb{% if forloop.first %} active{% endif %}"
         onclick="cambiarImagenPrincipal(this)">
    {% endfor %}
</div>
```

**JavaScript** — clickear una miniatura solo cambia el `src` de la imagen grande, no pide nada a ningún servidor:
```js
function cambiarImagenPrincipal(elemento) {
    document.getElementById('imagenPrincipal').src = elemento.src;
    document.querySelectorAll('.thumb').forEach(m => m.classList.remove('active'));
    elemento.classList.add('active');
}
```

**Cómo explicarlo:** "Las fotos no viven pegadas al producto: hay una tabla aparte, `ImagenProducto`, relacionada por `ForeignKey` — así un disco puede tener 0, 1 o 10 fotos sin tener que agregar columnas `imagen2`, `imagen3`... El carrusel en sí es JavaScript puro: todas las imágenes ya vinieron cargadas en el HTML, clickear una miniatura solo cambia cuál se ve grande."

### 3.3 — Imagen de reemplazo cuando no hay foto

[`productos/models.py`](../productos/models.py)
```python
imagen = models.ImageField(upload_to='img/', blank=True, null=True)
```

[`templates/productos/detalle.html`](../templates/productos/detalle.html) (mismo patrón en `lista.html`, `home.html`, relacionados):
```html
{% if otro.imagen %}
    <img src="{{ otro.imagen.url }}" alt="{{ otro.nombre }}">
{% else %}
    <img src="{% static 'img/DiscoNoEncontrado.jpg' %}" alt="{{ otro.nombre }}">
{% endif %}
```

**Cómo explicarlo:** "La portada es opcional en la base de datos (`blank=True, null=True`). Cada vez que se muestra una imagen de producto en cualquier parte del sitio, se pregunta primero `{% if producto.imagen %}` — si no tiene, se usa `DiscoNoEncontrado.jpg` como reemplazo. Es el mismo patrón repetido en el listado, el home, el detalle y los productos relacionados."

### 3.4 — RC y la API de Discogs

**El campo RC** (Release Code de Discogs) en el producto:

[`productos/models.py`](../productos/models.py)
```python
rc = models.PositiveIntegerField(null=True, blank=True, verbose_name="RC (Discogs)")
```

**Cómo llega el RC del producto hasta el JavaScript** — `producto.rc` ya viaja dentro del objeto `producto` que la vista pasó al template (ver 3.1), así que en el HTML se vuelca a una constante:

[`templates/productos/detalle.html`](../templates/productos/detalle.html)
```js
const RC_PRODUCTO = "{{ producto.rc|default_if_none:'' }}";

async function cargarDatosDiscogs() {
    if (!RC_PRODUCTO) return;   // este producto no tiene RC: no se consulta nada

    try {
        const res = await fetch(`https://api.discogs.com/releases/${RC_PRODUCTO}`);
        if (!res.ok) return;
        const data = await res.json();
        // ... rellena tracklist, ficha técnica, créditos y galería
    } catch (error) {
        console.error('No se pudo cargar la info de Discogs:', error);
    }
}
```

**Cómo explicarlo:** "El RC es el ID del release en Discogs (una base de datos pública de vinilos). Es dinámico: viene de la base de datos de cada producto, nunca está escrito fijo en el código. Con ese RC, el navegador le pregunta directo a la API de Discogs por el tracklist, la ficha técnica y los créditos — esto es lo único del sitio que sí es una llamada del navegador a una API externa; todo lo demás (precio, stock, nombre) sale de nuestra propia base de datos y nunca depende de que Discogs responda."

**Portadas reales del catálogo:** además, hay un comando (`productos/management/commands/descargar_imagenes_discogs.py`) que se corrió una sola vez para descargar la foto real de cada disco desde Discogs y guardarla como la portada (`producto.imagen`) — por eso el catálogo ya muestra fotos reales y no los cuadros de colores generados, sin que cada visita tenga que llamar a Discogs 50 veces.

---

## 4. Carrito de compras (`/carrito/`)

**Le muestras:** agregás un par de discos y entrás a "Carrito".

**Punto clave para decir primero:** el carrito **no usa la base de datos**. Vive completo en el navegador (`localStorage`), producto por producto, en formato JSON.

**La vista es casi vacía a propósito:**

[`core/views.py:24-28`](../core/views.py)
```python
def carrito(request):
    # Esta vista no consulta la base de datos: el contenido del carrito
    # vive en localStorage, en el navegador de quien esta comprando.
    return render(request, "core/carrito.html")
```

**El botón "Añadir al carrito"** (aparece en el listado, el home y el detalle) no es un `<form>` que manda algo al servidor — son atributos `data-*` que JavaScript lee después:

[`templates/productos/lista.html`](../templates/productos/lista.html)
```html
<button class="btn btn-sm btn-outline-primary btn-agregar-carrito"
        data-producto-id="{{ producto.id }}"
        data-producto-nombre="{{ producto.nombre }}"
        data-producto-precio="{{ producto.precio }}">
    Añadir al carrito
</button>
```

**Todo el motor está en un solo archivo JS**, [`static/js/carrito.js`](../static/js/carrito.js), cargado en `base.html` (por eso funciona en cualquier página del sitio, no solo en `/carrito/`):

```js
const CLAVE_CARRITO = "vinylhub_carrito";

function obtenerCarrito() {
    const datos = localStorage.getItem(CLAVE_CARRITO);
    if (!datos) return [];
    try { return JSON.parse(datos); } catch { return []; }
}

function guardarCarrito(carrito) {
    localStorage.setItem(CLAVE_CARRITO, JSON.stringify(carrito));
}

function agregarAlCarrito(id, nombre, precio) {
    const carrito = obtenerCarrito();
    const existente = carrito.find((item) => item.id === id);
    if (existente) {
        existente.cantidad += 1;
    } else {
        carrito.push({ id, nombre, precio, cantidad: 1 });
    }
    guardarCarrito(carrito);
    actualizarContadorCarrito();
    renderizarCarrito();
}
```

**Conectar los botones** (se ejecuta apenas carga cualquier página):
```js
function conectarBotonesAgregar() {
    const botones = document.querySelectorAll(".btn-add-cart, .btn-agregar-carrito");
    botones.forEach((boton) => {
        boton.addEventListener("click", () => {
            const id = boton.dataset.productoId;
            const nombre = boton.dataset.productoNombre;
            const precio = boton.dataset.productoPrecio;
            agregarAlCarrito(id, nombre, precio);
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    actualizarContadorCarrito();
    renderizarCarrito();
    conectarBotonesAgregar();
});
```

**Cómo explicarlo (guion sugerido):**
> "El carrito es 100% JavaScript, no toca la base de datos ni el backend. Cada botón 'Añadir al carrito' trae el id, nombre y precio del producto en atributos `data-*` que Django ya rellenó al armar la página. Cuando lo clickeás, `carrito.js` lee esos datos, arma un arreglo de objetos y lo guarda como texto JSON en `localStorage` — que es memoria del navegador, no del servidor. Por eso el numerito rojo del navbar y el contenido de `/carrito/` se actualizan al instante, sin recargar la página: todo pasa en el navegador. La contra es que el carrito es por navegador — si el cliente entra desde el celular no va a ver lo que agregó en el computador. Así lo pedían las instrucciones del proyecto."

**Si preguntan "¿por qué no en la base de datos?"**: porque el enunciado del proyecto pedía explícitamente usar `localStorage` sin backend para el carrito (está documentado en el `README.md` original y en los commits). Es una decisión de diseño, no un descuido.

---

## 5. Login / Registro / Logout (`/usuarios/...`)

Cubierto a fondo en [`DETALLE_PRODUCTO_Y_CONEXION_BD.md`, sección 10](./DETALLE_PRODUCTO_Y_CONEXION_BD.md#10-cómo-funciona-el-login-actualmente). Resumen para tener a mano:

- **Modelo:** [`usuarios/models.py`](../usuarios/models.py) — `Usuario(AbstractUser)`, le agrega `run`, `rol`, `fecha_nacimiento`, `direccion`, `region`, `comuna`.
- **Login:** [`usuarios/views.py`](../usuarios/views.py) — `authenticate(request, username=email, password=password)` (compara hashes, nunca texto plano) + `login(request, usuario)` (crea la sesión/cookie).
- **Registro:** `RegistroForm` valida correo único y contraseñas coincidentes **antes** de tocar la base de datos; `usuario.set_password(...)` hashea antes de guardar.
- **Detalle importante:** el "username" interno siempre es el mismo valor que el correo — así la persona no tiene que recordar un usuario aparte del email.

**Cómo explicarlo en una frase:** "El modelo de usuario extiende el `AbstractUser` de Django en vez de reinventar el login desde cero — heredamos hasheo de contraseñas, sesiones y permisos gratis, y solo agregamos los campos propios del proyecto."

---

## 6. Blog (`/blog/`)

**Le muestras:** el listado de posts y entrás a uno.

**Modelo — portada + galería, mismo patrón que productos:**

[`blog/models.py`](../blog/models.py)
```python
class Blog(models.Model):
    titulo = models.CharField(max_length=250)
    descripcion = models.CharField(max_length=250, help_text="Extracto corto para el listado")
    contenido = models.TextField(help_text="Contenido completo de la publicación")
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    imagen_portada = models.ImageField(upload_to='img/')
    activo = models.BooleanField(default=True)
```
```python
class ImagenBlog(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='img/blog/galeria/')
    orden = models.PositiveIntegerField(default=0)
```

**Vistas — casi idénticas a las de productos:**

[`blog/views.py`](../blog/views.py)
```python
def index(request):
    posts = Blog.objects.filter(activo=True)
    return render(request, "blog/lista.html", {"posts": posts})

def detalle(request, pk):
    post = get_object_or_404(Blog, pk=pk, activo=True)
    return render(request, "blog/detalle.html", {"post": post})
```

**Cómo explicarlo:** "El blog reutiliza exactamente el mismo patrón que productos: `activo` para poder tener borradores sin publicar, `get_object_or_404` para el detalle, y una tabla aparte (`ImagenBlog`) para la galería — de hecho `ImagenProducto` se copió de acá, no al revés. La única diferencia real es que un post tiene `autor` (`ForeignKey` a `Usuario`) y un producto no."

**Dato curioso si preguntan por `autor`:** usa `settings.AUTH_USER_MODEL` en vez de importar `Usuario` directo, para no crear una dependencia circular entre las apps `blog` y `usuarios`.

---

## 7. Contacto (`/contacto/`)

**Le muestras:** llenás el formulario y lo envías.

**Modelo:**

[`contacto/models.py`](../contacto/models.py)
```python
class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(max_length=100)
    asunto = models.CharField(max_length=150)
    mensaje = models.TextField(max_length=500)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    revisado = models.BooleanField(default=False)
```

**Formulario — se genera solo a partir del modelo:**

[`contacto/forms.py`](../contacto/forms.py)
```python
class ContactoForm(forms.ModelForm):
    class Meta:
        model = Contacto
        fields = ["nombre", "correo", "asunto", "mensaje"]
```

**Vista — patrón Post/Redirect/Get:**

[`contacto/views.py`](../contacto/views.py)
```python
def index(request):
    if request.method == "POST":
        form = ContactoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Tu mensaje fue enviado. Te responderemos pronto.")
            return redirect("contacto:index")
    else:
        form = ContactoForm()
    return render(request, "contacto/formulario.html", {"form": form})
```

**Cómo explicarlo:** "Es un `ModelForm`: en vez de escribir los campos del formulario a mano Y los del modelo, `ModelForm` los genera solos a partir de `Contacto`. Cuando el formulario es válido, `form.save()` crea la fila en la base de datos directamente. Después de guardar, se hace un `redirect` en vez de mostrar la misma página de nuevo — así, si la persona recarga el navegador después de enviar, no se manda el mismo mensaje dos veces (patrón Post/Redirect/Get)."

**Si preguntan "¿a dónde llega el mensaje, a un correo?"**: no, queda guardado como una fila en la tabla `contacto_contacto` de Postgres — se revisa desde `/admin/`, con el campo `revisado` para marcar cuáles ya se contestaron.

---

## 8. Panel de administración (`/admin/`)

Cubierto a fondo en [`DETALLE_PRODUCTO_Y_CONEXION_BD.md`, sección 9](./DETALLE_PRODUCTO_Y_CONEXION_BD.md#9-el-panel-de-administración-admin-y-cómo-funciona-adminpy). Resumen:

- El admin **no se programa a mano** — Django arma el CRUD completo solo; `admin.py` de cada app solo dice *cómo* mostrarlo (`list_display`, `search_fields`, `list_filter`).
- Las fotos de galería (`ImagenProducto`, `ImagenBlog`) se editan **dentro** de la misma pantalla del producto/post gracias a `TabularInline`.
- `Usuario` usa `UserAdmin` (no `ModelAdmin` normal) para que la contraseña se maneje hasheada en vez de mostrarse como texto editable.

---

## 9. Base de datos y despliegue

Cubierto a fondo en:
- [`DETALLE_PRODUCTO_Y_CONEXION_BD.md`, secciones 2 y 3](./DETALLE_PRODUCTO_Y_CONEXION_BD.md#2-cómo-se-conecta-django-a-postgresql) — cómo se conecta Django a Postgres (`DATABASES` en `settings.py`, variables de entorno, el ORM) y el recorrido completo de una petición.
- [`DESPLIEGUE.md`](./DESPLIEGUE.md) — dónde vive el servidor, Docker Compose, Cloudflare Tunnel, cómo redesplegar.

**Un fragmento que vale la pena tener a mano si preguntan "¿dónde están las credenciales?":**

[`config/settings.py`](../config/settings.py)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}
```
"Nunca están escritas en el código — se leen de un archivo `.env` que ni siquiera está en Git (está en `.gitignore`)."

---

## 10. Detalle chico: el footer siempre abajo

Por si preguntan por algo tan simple como el layout: [`static/css/main.css`](../static/css/main.css) tiene el CSS que hace que el footer quede pegado abajo de la pantalla aunque la página tenga poco contenido (usando `display: flex` en el `body` + `flex: 1` en el `main`), en vez de quedar "flotando" justo debajo del contenido.

---

## Preguntas típicas que te puede hacer el profe (y la respuesta corta)

- **"¿Por qué Django y no otro framework?"** → Es lo que pedía el ramo (Fullstack II); Django trae ORM, admin y sistema de usuarios de fábrica, lo que evita reescribir mucho código repetitivo.
- **"¿Por qué el carrito no se guarda en la base de datos?"** → Decisión de diseño pedida por el enunciado: `localStorage`, sin backend, para no complicar el alcance del proyecto con sesiones de carrito por usuario.
- **"¿Qué pasa si Discogs se cae durante la presentación?"** → Nada se rompe: todas las secciones que dependen de Discogs (tracklist, ficha técnica, créditos) empiezan ocultas y el resto de la página (nombre, precio, stock, portada) ya vino armada desde nuestra base de datos antes de que el JavaScript intente pedirle nada a Discogs.
- **"¿Cómo se conectan las tablas entre sí?"** → Con `ForeignKey`: `Producto → Artista`, `Producto → Categoria`, `ImagenProducto → Producto`, `Blog → Usuario` (autor), `ImagenBlog → Blog`.
- **"¿Cómo se actualizan las tablas cuando cambia un modelo?"** → Con migraciones (`python manage.py makemigrations` + `migrate`) — cada cambio de estructura queda como un archivo en `*/migrations/`, versionado en Git.
