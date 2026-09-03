# Imagen base ligera con Python 3.12
FROM python:3.12-alpine

# Logs sin buffer (aparecen en "docker logs" de inmediato) y sin .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Dependencias de sistema necesarias para compilar psycopg (driver de
# PostgreSQL) y Pillow (procesamiento de imagenes de productos/blog).
RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    jpeg-dev \
    zlib-dev \
    libffi-dev

# Usuario sin privilegios: el contenedor no necesita correr como root.
RUN addgroup -g 1000 -S app && adduser -u 1000 -S -D -G app app

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app/

# media/ y staticfiles/ los escribe el propio contenedor en runtime
# (uploads de usuarios y "collectstatic"); se crean con dueno "app" de
# antemano para que el usuario sin privilegios pueda escribir ahi.
RUN mkdir -p /app/media /app/staticfiles && chown -R app:app /app

USER app

EXPOSE 8000

# Antes de levantar el servidor: aplica migraciones pendientes y junta
# los estaticos (whitenoise los sirve desde STATIC_ROOT). Se hace en el
# arranque, no en el build, para que tome la base de datos real del
# entorno (no existe todavia cuando se construye la imagen).
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --access-logfile - --error-logfile -"]
