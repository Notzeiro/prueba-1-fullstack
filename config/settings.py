import os
from dotenv import load_dotenv

load_dotenv()
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-n453^$g+%hd3zwj3==ka2vy#6_^b_r+rw9#!x=k#wr#&dcrn0)")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"

# Necesario para que Django acepte peticiones cuando DEBUG=False (en ese
# modo, por seguridad, Django rechaza cualquier host que no este en esta
# lista explicitamente). En desarrollo local alcanza con estos dos; en
# produccion se agrega el dominio real via variable de entorno.
ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
    if h.strip()
]

# Origenes desde los que Django acepta peticiones POST protegidas por CSRF
# (debe incluir protocolo). Se necesita cuando la app corre detras de un
# proxy/tunel HTTPS con un dominio publico, por eso viene de una variable
# de entorno separada de ALLOWED_HOSTS (que no lleva protocolo).
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if o.strip()
]

# El contenedor recibe trafico plano desde el tunel/proxy que ya termino
# TLS; esta cabecera le dice a Django que la conexion original SI fue
# HTTPS, para que request.is_secure() y las cookies "secure" funcionen.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Solo se activan con DEBUG=False (produccion): en desarrollo local sin
# HTTPS estas opciones impedirian usar cookies o cargar la pagina.
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    "core",
    "usuarios",
    "productos",
    "blog",
    "contacto",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Sirve los archivos de STATIC_ROOT directamente desde Django/gunicorn,
    # sin depender de un nginx aparte dentro del contenedor. Va justo
    # despues de SecurityMiddleware como pide la documentacion de whitenoise.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.1/ref/settings/#databases

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

AUTH_USER_MODEL = "usuarios.Usuario"

# Traduce las categorias de mensajes de Django ("error") a las clases
# de Bootstrap que se usan para pintarlos ("alert-danger"), para que
# {{ message.tags }} en las plantillas arme la clase CSS correcta.
from django.contrib.messages import constants as messages_constants

MESSAGE_TAGS = {
    messages_constants.ERROR: "danger",
}


# Password validation
# https://docs.djangoproject.com/en/6.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
# Carpeta donde "manage.py collectstatic" junta todos los archivos
# estaticos en un solo lugar, para que el servidor web de produccion
# (no Django) los sirva directamente. En desarrollo (runserver) no se
# usa: Django sirve los archivos directo desde STATICFILES_DIRS.
STATIC_ROOT = BASE_DIR / "staticfiles"

# Compresion + hashing de nombres de archivo para cache-busting, servido
# por whitenoise (ver MIDDLEWARE mas arriba).
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    # Sin "Manifest": esa variante exige que exista el archivo generado
    # por "collectstatic" (staticfiles.json) para poder resolver
    # {% static %}, lo que rompe runserver/tests en desarrollo cuando
    # todavia no se corrio collectstatic. Esta variante solo comprime.
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Email
# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration

MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}
