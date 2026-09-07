# Cómo funciona el detalle de producto (y cómo se conecta a la base de datos)

Este documento explica, para poder presentarlo mañana, **de dónde sale cada dato** que se ve en la página de detalle de un producto, qué se cambió hoy y por qué. Está escrito para vos, no es documentación "oficial" del proyecto — así que va con explicaciones de más.

---

## 1. Lo primero y más importante: el HTML que me pasaste NO se conecta a esta base de datos

Miraste `detalle.html` (el que me pasaste) y viste esto al final del archivo:

```js
const API_URL = 'https://api.discogs.com/releases/514858';

async function fetchData() {
    const res = await fetch(API_URL);
    const data = await res.json();
    ...
}
```

Eso es JavaScript que corre **en el navegador del usuario**, después de que la página ya cargó, y le pide los datos a `api.discogs.com` — una página externa de terceros (Discogs, una base de datos pública de discos), **no a tu Postgres**. Por eso ese archivo suelto no mostraba tus productos: literalmente no sabe que tu base de datos existe. El `514858` fijo en la URL es el ID de un disco específico en Discogs, por eso siempre mostraba lo mismo sin importar qué producto quisieras ver.

Nuestra app (Django) funciona **al revés**: en vez de que el navegador pida los datos después, el servidor arma la página completa (ya con los datos adentro) **antes** de mandarla al navegador. Eso se llama *renderizado del lado del servidor* (server-side rendering). Nunca hay un `fetch()` a ningún lado para traer el producto: cuando el HTML llega a tu navegador, el nombre, precio, imágenes, etc. ya están escritos ahí adentro.

Voy a explicar exactamente cómo pasa eso.

---

## 2. Cómo se conecta Django a PostgreSQL

Esto vive en [`config/settings.py`](../config/settings.py):

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

- `ENGINE`: le dice a Django **qué motor de base de datos hablar** (acá, PostgreSQL). Django trae un traductor distinto para cada motor (Postgres, MySQL, SQLite, etc.) — el resto del código (modelos, vistas) no cambia si mañana cambiaras de motor.
- `NAME`, `USER`, `PASSWORD`, `HOST`, `PORT`: **no están escritos en el código**, se leen desde variables de entorno (`os.getenv(...)`) que vienen del archivo `.env` (ver `python-dotenv` al principio del mismo archivo: `load_dotenv()`). Así el mismo código sirve para desarrollo local y para el servidor, cada uno con su propio `.env` y sus propias credenciales — nunca hay contraseñas escritas directo en `settings.py`.
- En tu entorno local (Docker), `DB_HOST=db` — ese `db` es el nombre del servicio de Postgres dentro de `docker-compose.yml`, no una IP. Docker resuelve nombres de contenedor como si fueran hostnames dentro de la misma red.

La librería que realmente "habla" con Postgres por debajo es **psycopg** (ver `requirements.txt`) — Django arma SQL genérico y psycopg lo traduce al protocolo real de Postgres.

**Para la presentación:** si te preguntan "¿dónde están las credenciales de la base de datos?", la respuesta es: en el archivo `.env` (que nunca se sube a Git — está en `.gitignore`), no en el código.

---

## 3. El recorrido completo de una petición a `/productos/5/`

Cuando entrás a `http://127.0.0.1:8089/productos/5/`, pasa esto, en orden:

### Paso 1 — `config/urls.py` → `productos/urls.py`
Django mira la URL y busca qué vista (función Python) tiene que ejecutar. En [`productos/urls.py`](../productos/urls.py):

```python
path("<int:pk>/", views.detalle, name="detalle"),
```

`<int:pk>` le dice a Django "el número que venga acá en la URL, conviértelo a entero y pásaselo a la función `detalle()` con el nombre `pk`" (pk = *primary key*, el ID de la fila en la base de datos).

### Paso 2 — la vista consulta la base de datos (`productos/views.py`)

```python
def detalle(request, pk):
    producto = get_object_or_404(Producto, pk=pk, activo=True)
```

Esta línea es la conexión real a la base de datos. `Producto` es una clase Python (un **modelo**, definido en `productos/models.py`) que representa la tabla `productos_producto` en Postgres. `get_object_or_404(...)` internamente genera y ejecuta algo equivalente a:

```sql
SELECT * FROM productos_producto WHERE id = 5 AND activo = true LIMIT 1;
```

...pero vos nunca escribís ese SQL a mano — esto es el **ORM** (Object-Relational Mapper) de Django: te deja consultar la base de datos escribiendo Python (`Producto.objects.filter(...)`) en vez de SQL, y él se encarga de armar la consulta real. Si el producto no existe (o `activo=False`), esta línea directamente responde con una página 404, sin seguir ejecutando el resto de la función.

Las otras consultas de la misma vista (después de los cambios de hoy):

```python
relacionados = Producto.objects.filter(
    artista=producto.artista, activo=True
).exclude(pk=producto.pk)[:4]

misma_categoria = (
    Producto.objects.filter(categoria=producto.categoria, activo=True)
    .exclude(pk=producto.pk)[:4]
    if producto.categoria_id else Producto.objects.none()
)
```

Esto es lo que arma las góndolas "Más de \<artista\>" y "Más de \<categoría\>": son la **misma tabla**, filtrada distinto. `[:4]` es "traeme como máximo 4 filas" (equivalente a `LIMIT 4` en SQL).

### Paso 3 — la vista le pasa los datos a la plantilla (template)

```python
return render(
    request,
    "productos/detalle.html",
    {
        "producto": producto,
        "relacionados": relacionados,
        "misma_categoria": misma_categoria,
        "urls_galeria": urls_galeria,
    },
)
```

`render()` toma el archivo `templates/productos/detalle.html` y ese diccionario de datos, y devuelve HTML ya armado — con los `{{ producto.nombre }}`, `{{ producto.precio }}`, etc. del template ya reemplazados por los valores reales. **Esto pasa en el servidor**, antes de que el navegador reciba una sola línea de HTML.

### Paso 4 — la plantilla (`templates/productos/detalle.html`) solo pinta lo que ya le llegó

```html
<h1 class="product-title">{{ producto.nombre }}</h1>
<span class="product-price">${{ producto.precio }}</span>
```

El template **no vuelve a consultar la base de datos** ni pide nada a ningún servidor — solo escribe en el HTML los valores que ya venían en el diccionario del paso 3. Por eso no hace falta ningún `fetch()` como en tu archivo original: quien "conecta con la base de datos" es la vista (`views.py`), no el HTML ni el navegador.

**Resumen para la presentación, en una frase:**
> "La URL le dice a Django qué vista ejecutar, la vista usa el ORM para consultar Postgres y arma un diccionario de datos, y ese diccionario se inyecta en la plantilla HTML antes de mandarla al navegador — todo pasa en el servidor, no hay ninguna llamada a una API desde el navegador."

---

## 4. Qué se cambió hoy en la base de datos (y por qué)

### 4.1 — La portada del producto ahora es opcional

Antes:
```python
imagen = models.ImageField(upload_to='img/')
```
Ahora:
```python
imagen = models.ImageField(upload_to='img/', blank=True, null=True)
```

- `null=True`: a nivel de base de datos, la columna ahora acepta `NULL` (antes era obligatoria, `NOT NULL`).
- `blank=True`: a nivel de formularios/admin de Django, el campo ahora puede quedar vacío al crear/editar un producto.

**Por qué importaba esto:** las plantillas *ya* tenían código para mostrar una imagen de reemplazo:
```html
{% if producto.imagen %}
    <img src="{{ producto.imagen.url }}">
{% else %}
    <img src="{% static 'img/DiscoNoEncontrado.jpg' %}">
{% endif %}
```
Pero como el campo era obligatorio, **nunca podía existir un producto sin imagen**, así que esa rama del `{% else %}` era código muerto — estaba ahí pero jamás se ejecutaba. Con el campo opcional, ahora sí puede pasar de verdad, y por eso ahora se ve la imagen personalizada de "álbum no encontrado" (`static/img/DiscoNoEncontrado.jpg`, la que ya tenían hecha) cuando un producto no tiene foto.

Para la demo de hoy, dejé el producto **"Faith" de George Michael** (id 50) sin imagen a propósito, para poder mostrar ese caso funcionando.

### 4.2 — Tabla nueva: `ImagenProducto` (fotos de galería / carrusel)

Nuevo modelo en `productos/models.py`:

```python
class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='img/productos/galeria/')
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden']
```

Esto es exactamente el mismo patrón que ya usaba `ImagenBlog` para las fotos de galería de un post de blog (podés comparar en `blog/models.py`) — no se inventó un patrón nuevo, se copió el que ya existía.

- **Por qué una tabla aparte y no varias columnas en `Producto`:** un producto puede tener 0, 1, 5 o 20 fotos de galería — un número variable. Si le pusiéramos columnas `imagen2`, `imagen3`, `imagen4`... en la tabla `Producto`, tendríamos un límite fijo y arbitrario, y muchas columnas vacías para la mayoría de los productos. Con una tabla aparte, cada producto tiene tantas filas en `ImagenProducto` como fotos realmente tenga (esto se llama una relación "uno a muchos", la misma idea que `Artista` → muchos `Producto`).
- `producto = ForeignKey(...)`: cada fila de `ImagenProducto` "apunta" a un producto (guarda su `id`). `related_name='imagenes'` es lo que te permite escribir después `producto.imagenes.all()` para traer todas sus fotos de galería.
- `on_delete=CASCADE`: si se borra un producto, se borran automáticamente todas sus fotos de galería (no quedan fotos "huérfanas" apuntando a un producto que ya no existe).
- `orden`: para poder decidir en qué orden aparecen las fotos en el carrusel (0 primero, 1 después, etc.), en vez de depender del orden en que se subieron.

### 4.3 — La migración: `productos/migrations/0002_imagenproducto_y_portada_opcional.py`

Una **migración** es un archivo Python que describe un cambio de estructura en la base de datos (crear una tabla, agregar una columna, etc.) de forma que Django lo pueda aplicar (o deshacer) de manera controlada, y que quede en el historial del proyecto (se sube a Git, todos tus compañeros de equipo la reciben con `git pull` y corren `python manage.py migrate` para que su base de datos local quede igual que la tuya).

Esta migración hace dos cosas (mirá el archivo, tiene comentarios en cada bloque):
1. `AlterField`: modifica la columna `imagen` de `productos_producto` para que acepte `NULL`.
2. `CreateModel`: crea la tabla `productos_imagenproducto` (id, imagen, orden, producto_id).

**Cómo se aplicó:** normalmente correrías `python manage.py makemigrations` para que Django genere este archivo solo, comparando tus modelos con el estado anterior. Como no tenías Python instalado localmente (solo Docker), esta vez la escribí a mano con el mismo formato exacto que Django genera — podés confirmarlo comparándola con `0001_initial.py`, tienen la misma estructura. Después se aplicó con:
```bash
docker compose up -d --build web
```
El `Dockerfile` corre `python manage.py migrate` automáticamente cada vez que el contenedor arranca (podés verlo en la última línea del `Dockerfile`), así que no hizo falta ejecutar el comando a mano.

### 4.4 — El admin de Django (`productos/admin.py`)

Se agregó esto:
```python
class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1
```
```python
class ProductoAdmin(admin.ModelAdmin):
    ...
    inlines = [ImagenProductoInline]
```

Esto hace que, al editar un producto en `/admin/`, aparezca abajo una sección para subir sus fotos de galería directo ahí (sin tener que ir a otra pantalla separada). De nuevo, el mismo patrón que ya usaba `BlogAdmin` con `ImagenBlogInline`.

---

## 5. Cómo funciona el carrusel (sin nada externo)

Todo pasa en tres capas, todas dentro de `templates/productos/detalle.html`:

1. **La vista arma la lista de fotos a mostrar** (`productos/views.py`), en este orden de prioridad:
   - la portada del producto (`producto.imagen`), si tiene;
   - después, todas sus fotos de `ImagenProducto` (ya ordenadas por `orden`, porque el modelo tiene `ordering = ['orden']`);
   - si no hay ninguna de las dos, la lista queda con un solo elemento: la imagen `DiscoNoEncontrado.jpg`.

   ```python
   urls_galeria = []
   if producto.imagen:
       urls_galeria.append(producto.imagen.url)
   urls_galeria += [foto.imagen.url for foto in producto.imagenes.all()]
   if not urls_galeria:
       urls_galeria = [static("img/DiscoNoEncontrado.jpg")]
   ```

2. **El template pinta esa lista** como una imagen grande + una fila de miniaturas (si hay más de una foto):
   ```html
   <img id="imagenPrincipal" src="{{ urls_galeria.0 }}">
   ...
   {% for url in urls_galeria %}
       <img src="{{ url }}" class="thumb" onclick="cambiarImagenPrincipal(this)">
   {% endfor %}
   ```

3. **El JavaScript solo cambia qué imagen es la "grande"**, no descarga nada nuevo (las imágenes ya están todas cargadas en la página):
   ```js
   function cambiarImagenPrincipal(elemento) {
       document.getElementById('imagenPrincipal').src = elemento.src;
       document.querySelectorAll('.thumb').forEach(t => t.classList.remove('active'));
       elemento.classList.add('active');
   }
   ```

Esto es básicamente lo mismo que hacía el `changeImage()` de tu archivo original — la diferencia es que ahí las miniaturas venían de la respuesta de la API de Discogs (`data.images`), y acá vienen de `urls_galeria` (armada por nuestra propia vista, con nuestros propios datos).

---

## 6. Cómo agregar fotos de verdad a un producto

1. Entrá a `http://127.0.0.1:8089/admin/` (usuario y clave: ver el resumen que te pasé después de dejar todo desplegado).
2. Productos → elegí un disco → editar.
3. Abajo de todo vas a ver "Imágenes de producto" con una fila vacía — subí una foto ahí, guardá.
4. Recargá la página de detalle de ese producto: ahora el carrusel va a tener esa foto real además de la portada.

---

## 7. Datos de demo que agregué (para que se vea andando en la presentación)

Corrí un comando nuevo, `python manage.py seed_galeria_demo` (`productos/management/commands/seed_galeria_demo.py`), que le agrega 2 fotos de galería "de mentira" (generadas igual que las portadas del `seed_demo.py` original — un fondo de color con texto, no son fotos reales del disco) a los primeros 8 productos, **solo para que el carrusel tenga algo que mostrar** sin necesitar fotos reales de cada disco. Es idempotente (se puede correr de nuevo sin duplicar).

También, a mano, le saqué la portada al producto **"Faith" (George Michael, id 50)** para poder mostrar el caso "producto sin imagen → sale el dibujo de álbum no encontrado".

Ninguno de estos dos cambios (galería demo, sacarle la imagen a "Faith") es una migración ni un cambio de estructura — son solo datos de prueba en tu base de datos **local**. No tocan el servidor de producción para nada.

---

## 8. Resumen de archivos tocados hoy

| Archivo | Qué cambió |
|---|---|
| `productos/models.py` | `imagen` de `Producto` ahora es opcional; se agregó el modelo `ImagenProducto` |
| `productos/migrations/0002_imagenproducto_y_portada_opcional.py` | Migración nueva (escrita a mano, mismo formato que genera Django) |
| `productos/admin.py` | Se agregó `ImagenProductoInline` para subir fotos de galería desde el admin |
| `productos/views.py` | La vista `detalle()` ahora arma `misma_categoria` y `urls_galeria` |
| `templates/productos/detalle.html` | Reemplazado: mismo diseño visual que el HTML que pasaste, pero con carrusel conectado a datos reales (sin `fetch` a Discogs) |
| `productos/management/commands/seed_galeria_demo.py` | Comando nuevo, solo para poblar fotos de galería de ejemplo |

No se tocó nada en el servidor (`notzeiro@192.168.1.8`) hasta el momento en que se desplegó (ver el final de este documento).

---

## 9. El panel de administración (`/admin/`) y cómo funciona `admin.py`

El admin **no es una pantalla que alguien programó a mano** — es una funcionalidad que Django trae de fábrica (`django.contrib.admin`, ver `INSTALLED_APPS` en `settings.py`) y que arma automáticamente un CRUD (crear/leer/editar/borrar) completo para cualquier modelo que le digas. Lo único que escribe el equipo es, para cada modelo, un archivo `admin.py` que le dice **cómo** mostrarlo — no hace falta programar formularios, tablas ni botones de guardar, eso ya viene incluido.

### 9.1 — Registrar un modelo (lo básico)

```python
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "artista", "categoria", "precio", "stock", "activo")
    list_filter = ("activo", "categoria", "artista")
    search_fields = ("nombre", "artista__nombre_artista")
    list_editable = ("activo",)
    inlines = [ImagenProductoInline]
```

`@admin.register(Producto)` es lo que le dice a Django "esta clase (`ProductoAdmin`) es la configuración del admin para el modelo `Producto`". Sin este decorador (o sin `admin.site.register(...)`), el modelo ni siquiera aparecería en `/admin/`.

- `list_display`: qué columnas mostrar en la lista (por defecto, Django solo mostraría el `__str__()` del modelo).
- `list_filter`: agrega filtros a la derecha de la lista.
- `search_fields`: agrega una caja de búsqueda (`artista__nombre_artista` busca por un campo de la tabla relacionada `Artista`, cruzando la relación).
- `list_editable`: permite editar esa columna **directo desde la lista**, sin entrar al detalle del producto.

**Todo esto termina generando SQL por vos:** cuando entrás a `/admin/productos/producto/`, Django arma un `SELECT` con los filtros que hayas aplicado; cuando guardás un cambio, arma el `UPDATE` (o `INSERT` si es nuevo); cuando borrás, el `DELETE`. Es el mismo ORM que vimos en la sección 3, solo que quien llama al ORM ahora es el código del admin, no `views.py`.

### 9.2 — ¿Se pueden cambiar las imágenes desde el admin? **Sí, las dos.**

- **La portada** (`producto.imagen`): es un campo normal del formulario de edición del producto — aparece como un campo de "subir archivo" en la misma pantalla que el nombre, precio, stock, etc. Se puede reemplazar o (desde el cambio de ayer) dejar vacía.
- **Las fotos de galería / carrusel** (`ImagenProducto`): aparecen **debajo** del formulario del producto gracias a esto:

```python
class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1
```

Un `TabularInline` es lo que permite editar filas de una tabla relacionada **dentro de la misma pantalla** del modelo "padre" (acá, `Producto`), en vez de tener que ir a una sección aparte del admin a crear cada `ImagenProducto` a mano y elegir a qué producto pertenece. `extra = 1` es cuántas filas vacías extra mostrar al final, listas para cargar una foto nueva. `TabularInline` las muestra como filas de una tabla; existe también `StackedInline`, que muestra lo mismo pero en formato de formulario apilado en vez de tabla — es solo una diferencia visual, ambos hacen lo mismo por debajo.

Para probarlo: `/admin/` → Productos → elegí uno → vas a ver el campo "Imagen" (portada) arriba, y la sección "Imágenes de producto" (galería) abajo, con espacio para subir fotos nuevas. Al guardar, se crean/actualizan filas reales en la tabla `productos_imagenproducto`.

### 9.3 — El caso especial de `Usuario` (`usuarios/admin.py`)

```python
class UsuarioAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "rol", "is_staff")
    list_filter = ("rol", "is_staff", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("Datos adicionales", {"fields": ("run", "rol", "fecha_nacimiento", "direccion", "region", "comuna")}),
    )

admin.site.register(Usuario, UsuarioAdmin)
```

Acá `UsuarioAdmin` no hereda de `admin.ModelAdmin` como los demás, sino de `UserAdmin` (que Django ya trae hecho para su sistema de usuarios). Es a propósito: `UserAdmin` sabe mostrar la contraseña como un campo especial (hasheada, con un link para "cambiar contraseña" en vez de un cuadro de texto editable) y sabe manejar los permisos/grupos. Si `Usuario` se registrara con un `admin.ModelAdmin` normal, el admin mostraría la contraseña **hasheada** como si fuera texto plano editable — un desastre de seguridad y de usabilidad.

`fieldsets = UserAdmin.fieldsets + (...)`: en vez de definir de cero cómo se ve el formulario, se toma el que ya trae `UserAdmin` (usuario, contraseña, datos personales, permisos) y se le **agrega** al final una sección nueva ("Datos adicionales") con los campos propios de este proyecto (`run`, `rol`, `fecha_nacimiento`, `direccion`, `region`, `comuna`) que `AbstractUser` no trae de fábrica.

---

## 10. Cómo funciona el login actualmente

### 10.1 — El modelo de usuario (`usuarios/models.py`)

```python
class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        CLIENTE = "cliente", "Cliente"
        VENDEDOR = "vendedor", "Vendedor"
        ADMINISTRADOR = "administrador", "Administrador"

    run = models.CharField(max_length=9)
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.CLIENTE)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    direccion = models.CharField(max_length=300)
    region = models.CharField(max_length=300)
    comuna = models.CharField(max_length=300)
```

`Usuario` **no se escribió de cero**: hereda de `AbstractUser`, la clase base de usuarios que ya trae Django, que ya incluye `username`, `email`, `password` (siempre guardada hasheada, nunca en texto plano), `is_active`, `is_staff`, `is_superuser`, y todo el motor de login/permisos. Acá solo se le agregan los campos que pedía el proyecto y que `AbstractUser` no trae (`run`, `rol`, dirección, etc.).

`settings.py` tiene esta línea, que es la que le dice a Django "usá **este** modelo de usuario, no el por defecto":
```python
AUTH_USER_MODEL = "usuarios.Usuario"
```

### 10.2 — Iniciar sesión (`usuarios/views.py` → `login_view`)

```python
usuario = authenticate(request, username=email, password=password)
if usuario is not None:
    login(request, usuario)
```

- `authenticate(...)`: función de Django que busca un usuario con ese `username` (fijate: en este proyecto el **correo se guarda como username**, ver 10.3), toma la contraseña ingresada, la hashea con el mismo algoritmo con el que se guardó la original, y compara los dos hashes. Nunca compara la contraseña "en texto plano" contra nada — por eso, aunque alguien viera la base de datos, no vería contraseñas reales, solo hashes. Si coincide, devuelve el objeto `Usuario`; si no, devuelve `None`.
- `login(request, usuario)`: esto es lo que efectivamente "inicia sesión" — crea una fila en la tabla `django_session` y le manda al navegador una cookie con un ID de sesión. En cada petición siguiente, Django lee esa cookie, busca la sesión en la base de datos, y así sabe quién sos sin que tengas que volver a mandar tu contraseña en cada click (por eso `request.user` funciona en cualquier vista o template después de loguearte).

### 10.3 — Por qué se loguea con correo si el campo se llama `username`

`AbstractUser` exige que exista un `username` único, pero el formulario de login de este proyecto le pide "Correo electrónico" a la persona, no un nombre de usuario aparte. La solución que se usó fue simple: al registrarse, se guarda el mismo valor en los dos campos:

```python
usuario = Usuario(
    username=datos["email"],
    email=datos["email"],
    first_name=datos["nombre"],
)
usuario.set_password(datos["password1"])
usuario.save()
```

`set_password(...)` es el método que hashea la contraseña antes de guardarla (nunca se hace `usuario.password = "texto plano"` a mano, porque eso la guardaría sin hashear). Como `username` y `email` terminan siendo siempre el mismo valor, después `authenticate(request, username=email, ...)` en el login funciona sin problema: busca por `username`, pero lo que la persona escribió como "correo" es exactamente ese valor.

> Nota para la presentación: esto funciona bien mientras nadie pueda registrarse con `username` distinto de su email (acá no se puede, el formulario no lo permite) — es una solución simple y válida para el alcance de este proyecto, no un bug.

### 10.4 — Registro (`registro_view` + `RegistroForm`)

El formulario (`usuarios/forms.py`) valida, **antes** de tocar la base de datos:
- que el correo no esté ya registrado (`clean_email`, hace un `Usuario.objects.filter(email=email).exists()`);
- que las dos contraseñas ingresadas coincidan (`clean`, se ejecuta después de validar cada campo por separado).

Si algo de esto falla, Django nunca llega a crear el `Usuario` — el formulario vuelve con el error mostrado y no se generó ningún cambio en la base de datos. Recién si el formulario es válido se crea el usuario, se hashea su contraseña, y se llama a `login(request, usuario)` para dejarlo con sesión iniciada de una, sin que tenga que loguearse de nuevo después de registrarse.

### 10.5 — Cerrar sesión

```python
def logout_view(request):
    logout(request)
    ...
    return redirect("core:home")
```

`logout(request)` borra la sesión del usuario (la fila en `django_session` y la cookie dejan de ser válidas). Así de simple.

### 10.6 — Resumen para la presentación

> "El login no compara contraseñas en texto plano: usa `authenticate()`, que hashea lo que la persona escribió y lo compara contra el hash guardado. El modelo de usuario extiende el `AbstractUser` de Django en vez de reinventar el sistema de login desde cero, y se le agregaron los campos propios del proyecto (RUN, rol, dirección). El 'nombre de usuario' interno es siempre el correo, para que la persona no tenga que recordar un usuario aparte."

---

## 11. Despliegue a producción

Ver la sección "Cómo redesplegar / actualizar la app" en [`DESPLIEGUE.md`](./DESPLIEGUE.md). Los cambios de este documento (imagen opcional, `ImagenProducto`, admin, vista/plantilla de detalle) se desplegaron el {FECHA_DESPLIEGUE} siguiendo exactamente esos pasos: `git push` desde acá, y en el servidor `git pull` + `docker compose build web` + `docker compose up -d` (la migración se aplica sola al arrancar el contenedor, igual que en local).
