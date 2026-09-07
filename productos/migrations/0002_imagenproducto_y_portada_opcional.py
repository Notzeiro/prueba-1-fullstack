# Migracion escrita a mano (con el mismo formato que genera
# "manage.py makemigrations"), para: 1) permitir productos sin portada,
# y 2) agregar la tabla de imagenes de galeria del carrusel.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0001_initial'),
    ]

    operations = [
        # 1) La portada (Producto.imagen) pasa a ser opcional: antes era
        # obligatoria (NOT NULL en la base de datos, requerida en el admin),
        # asi que nunca existia un producto sin imagen y el fallback a
        # DiscoNoEncontrado.jpg de las plantillas nunca se llegaba a usar.
        migrations.AlterField(
            model_name='producto',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='img/'),
        ),
        # 2) Tabla nueva para las fotos extra de cada producto (galeria /
        # carrusel del detalle), igual en estructura a ImagenBlog.
        migrations.CreateModel(
            name='ImagenProducto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagen', models.ImageField(upload_to='img/productos/galeria/')),
                ('orden', models.PositiveIntegerField(default=0)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='imagenes', to='productos.producto')),
            ],
            options={
                'verbose_name': 'Imagen de producto',
                'verbose_name_plural': 'Imágenes de producto',
                'ordering': ['orden'],
            },
        ),
    ]
