# Proyecto Fullstack II --- Tienda Web

Proyecto académico desarrollado para **Desarrollo Fullstack II**.

## Stack tecnológico

-   Python
-   Django
-   PostgreSQL
-   Bootstrap 5
-   Git / GitHub

------------------------------------------------------------------------

## 1. Requisitos previos

Antes de levantar el proyecto, asegúrate de tener instalado:

-   Python 3
-   PostgreSQL
-   Git

Puedes comprobar Python con:

``` powershell
python --version
```

Y Git con:

``` powershell
git --version
```

------------------------------------------------------------------------

## 2. Crear y activar el entorno virtual

Desde la carpeta raíz del proyecto:

``` powershell
python -m venv venv
```

### Activar en Windows PowerShell

``` powershell
venv\Scripts\Activate.ps1
```

Si PowerShell muestra el error **"running scripts is disabled on this
system"**, puedes permitir scripts locales para tu usuario:

``` powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Confirma el cambio cuando PowerShell lo solicite y vuelve a ejecutar:

``` powershell
venv\Scripts\Activate.ps1
```

### Alternativa temporal

Si no quieres cambiar permanentemente la política de ejecución, puedes
habilitarla solo para la sesión actual:

``` powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\Activate.ps1
```

Al cerrar esa ventana de PowerShell, el cambio desaparece.

Cuando el entorno esté activo, la terminal debería comenzar con algo
similar a:

``` text
(venv) PS D:\ruta\del\proyecto>
```

### Desactivar el entorno virtual

Cuando termines de trabajar:

``` powershell
deactivate
```

------------------------------------------------------------------------

## 3. Actualizar pip

Con el entorno virtual activado:

``` powershell
python -m pip install --upgrade pip
```

------------------------------------------------------------------------

## 4. Instalar dependencias

Para una instalación nueva del proyecto:

``` powershell
pip install -r requirements.txt
```

Durante la creación inicial del proyecto se utilizaron:

``` powershell
pip install django psycopg[binary] python-dotenv
```

Las dependencias se guardan con:

``` powershell
pip freeze > requirements.txt
```

> Si agregas una nueva dependencia al proyecto, recuerda actualizar
> `requirements.txt`.

------------------------------------------------------------------------

## 5. Variables de entorno

El proyecto utiliza un archivo `.env` para valores que no deben quedar
escritos directamente en el código.

Crea un archivo `.env` en la raíz:

``` env
DJANGO_SECRET_KEY=tu_clave_secreta
DJANGO_DEBUG=True
```

Para generar una `SECRET_KEY` de Django:

``` powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copia el resultado en `DJANGO_SECRET_KEY`.

> **Importante:** nunca subir `.env` al repositorio.

------------------------------------------------------------------------

## 6. Configuración de Django

En `config/settings.py`, las variables de entorno se cargan mediante
`python-dotenv`:

``` python
import os
from dotenv import load_dotenv

load_dotenv()
```

La configuración utiliza:

``` python
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"
```

------------------------------------------------------------------------

## 7. Base de datos PostgreSQL

El proyecto utilizará **PostgreSQL** como base de datos.

La configuración específica de la base de datos se documentará aquí una
vez definidos:

-   nombre de la base de datos;
-   usuario;
-   host;
-   puerto;
-   variables de entorno necesarias.

Las credenciales de PostgreSQL tampoco deben subirse al repositorio.

------------------------------------------------------------------------

## 8. Migraciones

Después de configurar la base de datos o descargar cambios que incluyan
nuevos modelos:

``` powershell
python manage.py migrate
```

Si modificas modelos:

``` powershell
python manage.py makemigrations
python manage.py migrate
```

------------------------------------------------------------------------

## 9. Ejecutar el proyecto

Con el entorno virtual activado:

``` powershell
python manage.py runserver
```

El servidor de desarrollo estará normalmente disponible en:

``` text
http://127.0.0.1:8000/
```

Para detenerlo:

``` text
Ctrl + C
```

------------------------------------------------------------------------

## 10. Flujo para trabajar cada día

Al abrir nuevamente el proyecto:

``` powershell
cd "ruta\del\proyecto"
venv\Scripts\Activate.ps1
python manage.py runserver
```

Cuando termines:

``` powershell
deactivate
```

------------------------------------------------------------------------

## 11. Estructura inicial

La estructura esperada será aproximadamente:

``` text
proyecto/
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── core/
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
└── venv/
```

`venv/` y `.env` existen localmente, pero **no deben estar versionados
en Git**.

------------------------------------------------------------------------

## 12. `.gitignore`

El proyecto debe incluir como mínimo:

``` gitignore
# Python
__pycache__/
*.py[cod]
*$py.class

# Virtual environments
venv/
.venv/

# Environment variables
.env

# Django
*.log
db.sqlite3
media/

# IDE
.vscode/
.idea/

# Windows
Thumbs.db
Desktop.ini
```

------------------------------------------------------------------------

## 13. Trabajo colaborativo

El proyecto será desarrollado por un equipo de 4 integrantes.

Flujo recomendado:

``` text
main
└── develop
    ├── feature/auth
    ├── feature/productos
    ├── feature/blog
    └── feature/admin
```

Reglas básicas:

1.  No desarrollar directamente sobre `main`.
2.  Crear una rama para cada funcionalidad.
3.  Hacer commits pequeños y descriptivos.
4.  Subir la rama a GitHub.
5.  Crear Pull Request.
6.  Revisar antes de integrar.
7.  Integrar primero en `develop`.
8.  Llevar a `main` solamente versiones estables.

------------------------------------------------------------------------

## 14. Solución de problemas

### PowerShell no permite activar `venv`

Error:

``` text
Activate.ps1 cannot be loaded because running scripts is disabled on this system
```

Solución para el usuario actual:

``` powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

O solo para la sesión actual:

``` powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Después:

``` powershell
venv\Scripts\Activate.ps1
```

### `python` no se reconoce

Prueba:

``` powershell
py --version
```

Si `py` funciona, puedes usar:

``` powershell
py -m venv venv
```

### Faltan dependencias

Asegúrate de tener `venv` activo y ejecuta:

``` powershell
pip install -r requirements.txt
```

------------------------------------------------------------------------

## Estado del proyecto

Actualmente se encuentra en la etapa de **configuración inicial del
entorno de desarrollo**.

Próximos pasos:

-   [ ] Configurar PostgreSQL.
-   [ ] Crear estructura de aplicaciones Django.
-   [ ] Diseñar modelos.
-   [ ] Implementar autenticación y roles.
-   [ ] Implementar productos.
-   [ ] Implementar CRUD administrativo.
-   [ ] Implementar blog.
-   [ ] Implementar contacto.
-   [ ] Integrar interfaz con Bootstrap 5.
-   [ ] Crear pruebas.
-   [ ] Preparar entrega.
