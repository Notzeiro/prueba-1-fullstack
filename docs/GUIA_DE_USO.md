# Guía de uso — Vinyl Hub

Este documento explica cómo usar la aplicación una vez que está corriendo, sin entrar en detalles de código (para eso está `COMO_FUNCIONA_EL_CODIGO.md`).

## 1. Cómo levantar el proyecto en tu máquina

1. Cloná el repositorio y entrá a la carpeta del proyecto.
2. Creá un entorno virtual e instalá las dependencias:
   ```bash
   python -m venv venv
   venv\Scripts\Activate.ps1      # Windows PowerShell
   pip install -r requirements.txt
   ```
3. Instalá PostgreSQL en tu máquina (si no lo tenés) y creá:
   - Una base de datos llamada `vinyl_hub`
   - Un usuario llamado `tienda_user` con una contraseña a tu elección, dueño de esa base
4. Copiá `.env.example` a `.env` y completá tus propios datos:
   ```
   DJANGO_SECRET_KEY=<generá una con el comando de abajo>
   DJANGO_DEBUG=True
   DB_NAME=vinyl_hub
   DB_USER=tienda_user
   DB_PASSWORD=<tu contraseña>
   DB_HOST=localhost
   DB_PORT=5432
   ```
   Para generar una `SECRET_KEY` nueva:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
5. Aplicá las migraciones (esto crea las tablas en tu base de datos):
   ```bash
   python manage.py migrate
   ```
6. Creá un usuario administrador para poder entrar al panel de Django:
   ```bash
   python manage.py createsuperuser
   ```
7. Levantá el servidor:
   ```bash
   python manage.py runserver
   ```
8. Abrí `http://127.0.0.1:8000/` en el navegador.

**Importante:** cada persona del equipo tiene que hacer los pasos 3 y 4 en su propia máquina, con sus propios datos. La base de datos de PostgreSQL no se comparte por internet ni por git — solo se comparte el diseño de las tablas (los modelos y las migraciones), no los datos.

## 2. Recorrido de la tienda (lado del cliente)

### Página principal (`/`)
Muestra un banner de bienvenida y una vitrina con productos destacados (los primeros 8 productos activos de la base de datos). Desde acá se puede navegar a cualquier otra sección con el menú de arriba.

### Productos (`/productos/`)
Lista todos los productos activos. Cada tarjeta muestra imagen, nombre, artista y precio, con un botón para ver el detalle y otro para agregarlo directo al carrito sin entrar al detalle.

### Detalle de un producto (`/productos/<id>/`)
Muestra la ficha completa de un disco: imagen, descripción, artista, categoría, stock disponible, y un botón "Añadir al carrito". Al final se muestran otros discos del mismo artista, si hay.

### Nosotros (`/nosotros/`)
Página institucional con una breve descripción del proyecto y el equipo que lo desarrolló.

### Blog (`/blog/`)
Lista las publicaciones activas del blog (noticias, novedades). Cada una muestra título, un extracto corto y la imagen de portada.

### Contáctanos (`/contacto/`)
Formulario para enviar un mensaje (nombre, correo, asunto, mensaje). Al enviarlo, queda guardado en la base de datos para que el administrador lo revise después desde el panel.

### Registro (`/usuarios/registro/`)
Crea una cuenta nueva. Pide nombre completo, correo, contraseña (dos veces, para confirmar) y teléfono opcional. Si el correo ya está registrado, o las contraseñas no coinciden, el formulario avisa el error sin perder lo ya escrito. Al registrarse con éxito, la sesión se inicia automáticamente.

### Inicio de sesión (`/usuarios/login/`)
Pide correo y contraseña. Si son incorrectos, muestra un mensaje de error genérico (por seguridad, no dice si el problema es el correo o la contraseña). Al iniciar sesión, el menú de arriba cambia y muestra el nombre de la persona junto con la opción de "Cerrar sesión".

### Cerrar sesión
Disponible en el menú superior una vez logueado. Termina la sesión y vuelve al Home.

### Carrito de compras (`/carrito/`)
Muestra todos los productos agregados, con su cantidad, subtotal y el total general. Se puede:
- Cambiar la cantidad de un producto (escribiendo el número nuevo)
- Quitar un producto por completo con el botón "Quitar"

**El carrito se guarda en el navegador (localStorage), no en la base de datos.** Esto significa:
- Si cerrás el navegador y volvés a entrar desde el mismo navegador y computador, el carrito sigue ahí.
- Si entrás desde otro dispositivo o navegador, el carrito va a estar vacío — no es el mismo carrito.
- Si borrás los datos de navegación del navegador, el carrito se pierde.

### Buscador (en el menú superior)
Permite escribir un término y buscar entre los productos. *(Pendiente de conectar a un filtro real en la vista — por ahora el campo existe visualmente pero no filtra resultados todavía).*

## 3. El panel de administración (`/admin/`)

Es el admin que trae Django de fábrica. Para entrar hace falta un usuario con permiso de staff (el que se crea con `createsuperuser`, o cualquier usuario al que se le active `is_staff` desde ahí mismo).

Desde el panel se puede:

- **Usuarios**: ver, crear, editar usuarios y su rol (cliente/vendedor/administrador).
- **Productos → Vinilos**: crear/editar/desactivar productos, ver stock, precio, artista y categoría. Se puede activar/desactivar un producto directo desde el listado, sin entrar al detalle.
- **Productos → Artistas** y **Categorías**: administrar el catálogo de artistas y categorías que se usan al crear un producto.
- **Blog → Blogs**: crear/editar publicaciones, incluyendo subir imágenes de galería desde la misma pantalla.
- **Contacto → Mensajes de contacto**: ver los mensajes enviados desde el formulario público, filtrar por revisados/no revisados, y marcar varios como revisados de una vez seleccionándolos y usando la acción del listado.

## 4. Datos de prueba ya cargados

Al momento de escribir este documento, la base de datos tiene cargados como ejemplo:

- **Productos**: *Walk Among Us* (Misfits) y *Californication* (Red Hot Chili Peppers)
- **Categorías**: Punk Rock, Funk Rock
- **Un usuario administrador** (creado con `createsuperuser` — pedile la contraseña a quien lo creó, o creá el tuyo propio en tu base de datos local)

Estos datos existen solo en la base de datos de quien los cargó — cada integrante del equipo va a tener que cargar sus propios datos de prueba en su base local (o usar el admin para hacerlo).
