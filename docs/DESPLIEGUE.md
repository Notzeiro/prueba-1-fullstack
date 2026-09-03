# Despliegue en producción — Vinyl Hub

Este documento explica cómo y dónde está desplegada la aplicación, para poder mantenerla, redesplegarla o depurar un problema sin tener que redescubrir todo desde cero.

## 1. Dónde vive

| Cosa | Valor |
|---|---|
| Servidor | `zeiro-server` (propio, accedido por SSH vía Tailscale) |
| Dominio público | `https://vynilstore.notzeiro.tech` |
| Carpeta en el servidor | `/opt/docker/apps/vynilstore/` |
| Orquestación | Docker Compose (un contenedor de la app + un contenedor de PostgreSQL) |
| Entrada pública | Cloudflare Tunnel (`cloudflared`) → contenedor `vynilstore-web`, puerto 8000 |
| Monitoreo | Uptime Kuma (`kuma.notzeiro.tech`), monitor HTTP contra `http://vynilstore-web:8000` |

El servidor aloja **varias apps distintas de distintos proyectos**, cada una en su propia carpeta bajo `/opt/docker/apps/<nombre>`, con su propia base de datos y su propia red Docker aislada — así un problema (o una fuga de credenciales) en una app no afecta a las demás. Vinyl Hub sigue exactamente ese mismo patrón.

## 2. Por qué un subdominio y no `notzeiro.tech/vynilstore`

Se evaluó exponer la tienda como una ruta bajo el dominio principal (`notzeiro.tech/vynilstore`), pero se descartó:

- El resto de las apps del servidor ya usan el patrón "un subdominio por app" (`kuma.notzeiro.tech`, `egg.notzeiro.tech`, etc.) — mantener el mismo patrón hace todo más predecible.
- Django no está pensado para vivir bajo una ruta base sin configuración extra (`FORCE_SCRIPT_NAME`, ajustar `STATIC_URL`, `MEDIA_URL`, y revisar cada `{% url %}`/`reverse()` y redirect del proyecto). Un subdominio evita todo ese trabajo y esa fuente de bugs.
- El servidor ya no usa un nginx propio como proxy: usa **Cloudflare Tunnel en modo remoto** (ver más abajo), que rutea por **hostname**, no por ruta — un subdominio encaja de forma natural con esa pieza.

## 3. Cómo entra el tráfico (Cloudflare Tunnel)

El servidor no tiene el puerto 80/443 abierto directo a internet ni un nginx local escuchando ahí. En su lugar corre un contenedor `cloudflared` (`/opt/docker/cloudflared/`) que abre un túnel saliente hacia Cloudflare. Ese túnel es **"remotely-managed"** (se identifica con un `TUNNEL_TOKEN`, no con un archivo `config.yml` local), lo que significa que las reglas de "este hostname público va a este servicio interno" **se configuran desde el dashboard de Cloudflare Zero Trust**, no editando un archivo en el servidor.

La regla para esta app:

```
Public hostname: vynilstore.notzeiro.tech
Service:         http://vynilstore-web:8000
```

`vynilstore-web` se resuelve porque el contenedor `cloudflared` y el contenedor `vynilstore-web` comparten la red Docker `frontend-proxy` — Docker resuelve el nombre del contenedor como si fuera un hostname DNS dentro de esa red. Por eso el contenedor de la app **no necesita** publicar el puerto 8000 hacia afuera del servidor: solo lo necesitan los contenedores vecinos en `frontend-proxy`.

## 4. La imagen Docker (`Dockerfile`)

```dockerfile
FROM python:3.12-alpine
...
RUN mkdir -p /app/media /app/staticfiles && chown -R app:app /app
USER app
EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 ..."]
```

Puntos clave:

- **Alpine + gcc/postgresql-dev/jpeg-dev**: Alpine no trae compilador ni headers de PostgreSQL/JPEG, y hacen falta para compilar `psycopg` (driver de Postgres) y `Pillow` (procesa las imágenes de productos/blog) al instalar `requirements.txt`.
- **Usuario `app` (UID 1000), no root**: si alguien lograra ejecutar código arbitrario dentro del contenedor, no tendría privilegios de root ahí adentro. Es el mismo patrón que usan los otros proyectos Python del servidor (ver `sii-api`).
- **`migrate` y `collectstatic` en el arranque (`CMD`), no en el build**: en el momento de construir la imagen todavía no existe una base de datos a la que conectarse (la base vive en otro contenedor, que puede no estar corriendo aún) — por eso esos comandos se corren recién cuando el contenedor arranca de verdad, no al hacer `docker build`.
- **`gunicorn`, no `runserver`**: `manage.py runserver` es exclusivamente para desarrollo (de un solo hilo, sin manejo serio de errores/concurrencia). `gunicorn` es un servidor WSGI de producción real, acá con 3 workers (procesos) para atender varias peticiones a la vez.

## 5. `docker-compose.yml`

Dos servicios:

- **`db`**: `postgres:16-alpine`, con un volumen nombrado (`vynilstore_postgres_data`) para que los datos sobrevivan si el contenedor se recrea. Solo está en la red `db-net-vynilstore` — **no** está en `frontend-proxy`, así que no es alcanzable desde ningún otro contenedor del servidor ni desde internet, solo desde `vynilstore-web`. Esto es el "entorno completamente aislado" que se pidió: ni la base de datos ni el resto de la app comparten red con las otras aplicaciones del servidor.
- **`web`**: construye la imagen del `Dockerfile`, está en dos redes: `db-net-vynilstore` (para hablar con su base) y `frontend-proxy` (para que `cloudflared` y `uptime-kuma` puedan alcanzarlo). También expone `127.0.0.1:8089:8000` — **solo accesible desde dentro del propio servidor** (no desde internet), útil para probar con `curl http://127.0.0.1:8089` sin pasar por Cloudflare.
- `depends_on: db: condition: service_healthy` — el contenedor `web` no arranca (y por lo tanto no intenta migrar) hasta que Postgres realmente esté aceptando conexiones, no solo "iniciado".

Variables (`.env` en el servidor, **no** el mismo `.env` que se usa en desarrollo local — ver sección 7):

```
DJANGO_SECRET_KEY=...
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=vynilstore.notzeiro.tech
DJANGO_CSRF_TRUSTED_ORIGINS=https://vynilstore.notzeiro.tech
DB_NAME=vinyl_hub
DB_USER=tienda_user
DB_PASSWORD=...
DB_HOST=db
DB_PORT=5432
```

`DB_HOST=db` porque dentro de Docker Compose los contenedores se llaman entre sí por el nombre del *servicio* (`db`), no por `localhost` — cada contenedor tiene su propia red y su propio "localhost" aislado del resto.

## 6. Cambios que se hicieron en el código de Django para poder desplegarlo

Estos cambios viven en `config/settings.py` y `config/urls.py`, y son los mismos tanto en desarrollo como en producción (se activan o no según las variables de entorno, no hay dos versiones del código):

- **`ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` ahora vienen del `.env`** (`DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, separados por coma) en vez de estar fijos en el código. Antes solo aceptaban `127.0.0.1`/`localhost`; en el servidor hace falta agregar el dominio real.
- **`SECURE_PROXY_SSL_HEADER`**: Cloudflare Tunnel le habla al contenedor en HTTP plano (el HTTPS ya lo terminó Cloudflare antes de llegar al servidor). Sin esta línea, Django pensaría que toda conexión es insegura y rompería las cookies `secure` y las redirecciones HTTPS.
- **`SESSION_COOKIE_SECURE` / `CSRF_COOKIE_SECURE`** activadas solo cuando `DEBUG=False`: las cookies de sesión y CSRF solo se envían por HTTPS en producción (en desarrollo local, sin HTTPS, romperían el login si estuvieran activadas).
- **`whitenoise`** agregado a `MIDDLEWARE` y como `STORAGES["staticfiles"]`: sirve los archivos estáticos (CSS/JS/imágenes fijas) directamente desde el propio proceso de Django/gunicorn, comprimidos, sin necesitar un nginx aparte dentro del contenedor. Se usa la variante *sin* manifest (`CompressedStaticFilesStorage`) porque la variante con manifest exige haber corrido `collectstatic` antes de poder resolver `{% static %}`, lo que rompía `runserver` y los tests en desarrollo.
- **`config/urls.py`: los archivos de `media/` (imágenes subidas de productos y blog) ahora se sirven siempre**, no solo con `DEBUG=True`. Lo normal en un despliegue "serio" es que esto lo haga un servidor aparte (nginx, un bucket S3, etc.), pero este despliegue es un único contenedor sin esa pieza extra — para el volumen de tráfico de este proyecto (un trabajo académico) es una simplificación razonable. Si el proyecto creciera, el siguiente paso sería mover `media/` a almacenamiento externo (o agregar un contenedor nginx que sirva ese volumen, como hace `portfolio-web` con `nginx:alpine` en este mismo servidor).

## 7. Credenciales: qué pasó y qué se hizo

El archivo `.env` original (con `DJANGO_SECRET_KEY` y `DB_PASSWORD` reales) **estaba comiteado en git** y ya se había subido al repositorio remoto (GitHub) en varios commits — quedó expuesto ahí, aunque el repositorio sea privado/de uso académico, cualquiera con acceso al repo (o a su historial) podía verlo.

Se hizo lo siguiente:

1. `.env` se sacó del control de versiones (`git rm --cached .env`) y se agregó a `.gitignore`, junto con `venv/`, `media/`, `db.sqlite3` y `*.log`. Se agregó `.env.example` (sin datos reales) para que cualquiera sepa qué variables necesita definir.
2. **Se generaron credenciales nuevas** — el `SECRET_KEY` y el `DB_PASSWORD` viejos (los que estaban expuestos) ya no se usan en ningún lado, ni en desarrollo local ni en el servidor. El de desarrollo local y el de producción son además **distintos entre sí**.
3. No se reescribió el historial de git (`git filter-repo`/`BFG`) para borrar el secreto viejo de los commits antiguos: hacerlo requeriría *force-push* y rompería los clones existentes de cualquier otra persona del equipo. Como el valor viejo ya no se usa en ningún entorno real, dejarlo en el historial antiguo ya no es una fuga explotable — es un dato muerto.
4. Si alguna vez se usó `DB_PASSWORD=popUSER` en un Postgres local de verdad, hay que actualizar esa contraseña ahí también (`ALTER USER tienda_user WITH PASSWORD '...';`) para que coincida con el nuevo valor del `.env` local — cambiar el `.env` no cambia por sí solo la contraseña ya configurada en un Postgres que ya existía.

## 8. Cómo redesplegar / actualizar la app

En el servidor:

```bash
cd /opt/docker/apps/vynilstore
git pull
docker compose build web
docker compose up -d
```

`migrate` y `collectstatic` se corren solos al arrancar el contenedor (ver `Dockerfile`, sección 4), así que no hace falta correrlos a mano después de un `git pull` normal.

Para ver logs en vivo:

```bash
docker compose logs -f web
```

Para entrar a una shell de Django dentro del contenedor (por ejemplo, para crear un superusuario en el servidor):

```bash
docker compose exec web python manage.py createsuperuser
```

## 9. Monitoreo (Uptime Kuma)

El servidor tiene una única instancia de Uptime Kuma (`kuma.notzeiro.tech`) que ya monitorea todas las apps del servidor — Vinyl Hub se agregó ahí como un monitor más, no como una instancia aparte. El contenedor de Kuma está conectado a la red `frontend-proxy`, la misma donde vive `vynilstore-web`, así que puede alcanzarlo directo por nombre de contenedor:

```
Tipo:      HTTP(s)
Nombre:    Vynil Store
URL:       http://vynilstore-web:8000/
Intervalo: el mismo que usan las demás apps del servidor
```

## 10. Aislamiento

Todo lo que pidió específicamente el despliegue — "un entorno completamente aislado del resto" — se cumple así:

- Base de datos propia (`vynilstore-db`), en su propia red Docker (`db-net-vynilstore`), sin acceso desde ninguna otra app del servidor.
- Volumen de datos propio (`vynilstore_postgres_data`), no compartido.
- La única red que `vynilstore-web` comparte con el resto del servidor es `frontend-proxy`, y ahí solo participan contenedores "de entrada" (el túnel de Cloudflare y Uptime Kuma) — no otras bases de datos ni otras apps.
- Usuario Linux sin privilegios (`app`, UID 1000) dentro del contenedor.
- Credenciales propias, generadas para este despliegue, no reutilizadas de ningún otro proyecto del servidor.
