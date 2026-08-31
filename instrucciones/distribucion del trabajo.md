Checklist completo del proyecto
1. Preparación y organización
 Definir nombre definitivo del proyecto.
 Confirmar funcionalidades exigidas por el profesor/rúbrica.
 Confirmar tecnologías permitidas.
 Crear repositorio en GitHub.
 Agregar a los 4 integrantes como colaboradores.
 Crear ramas:
main
develop
 Definir convención para ramas:
feature/login
feature/productos
feature/blog
etc.
 Crear .gitignore para Python/Django.
 Crear README.md.
 Definir metodología de trabajo: issues, tareas y pull requests.
 Definir quién se encargará inicialmente de cada módulo.
2. Crear el proyecto base
 Instalar Python.
 Crear entorno virtual.
 Instalar Django.
 Instalar driver para PostgreSQL.
 Crear requirements.txt.
 Crear proyecto Django.
 Crear archivo .env.
 Sacar credenciales sensibles de settings.py.
 Configurar SECRET_KEY desde variables de entorno.
 Configurar modo desarrollo.
 Verificar que Django levante correctamente.
 Crear página inicial temporal para comprobar funcionamiento.
3. PostgreSQL
 Instalar PostgreSQL.
 Crear base de datos.
 Crear usuario específico para la aplicación.
 Asignar contraseña.
 Configurar Django para conectarse a PostgreSQL.
 Probar conexión.
 Ejecutar migraciones iniciales.
 Verificar tablas creadas.
 Documentar cómo configurar la BD para que los 4 puedan levantar el proyecto.
 No subir contraseñas de PostgreSQL a GitHub.
4. Definir arquitectura Django

Crear las apps principales:

 core
 usuarios
 productos
 blog
 contacto

Opcional:

 dashboard o administracion.

Luego:

 Registrar las apps en INSTALLED_APPS.
 Crear URLs independientes por aplicación.
 Crear carpeta global de templates.
 Crear carpeta de archivos estáticos.
 Crear estructura CSS.
 Crear estructura JavaScript.
 Crear carpeta para imágenes.
 Configurar carga de archivos multimedia.
 Configurar MEDIA_ROOT.
 Configurar MEDIA_URL.
5. Diseñar la base de datos
Usuario
 Decidir si usar User de Django o AbstractUser.
 Crear modelo personalizado antes de avanzar demasiado.
 Definir campos:
nombre
apellido
correo
username
rol
 Definir roles:
cliente
administrador
 Configurar contraseñas mediante Django.
 No guardar contraseñas manualmente.
Productos
 Crear modelo Producto.
 Agregar:
nombre
descripción
precio
stock
imagen
activo
fecha creación
fecha modificación
 Definir validaciones.
 Definir representación __str__.

Si corresponde:

 Crear modelo Categoria.
 Relacionar productos con categorías.
Blog
 Crear modelo Post.
 Agregar:
título
contenido
imagen
autor
fecha
estado/publicado.
 Relacionar autor con usuario.
Contacto
 Crear modelo Contacto.
 Agregar:
nombre
correo
asunto
mensaje
fecha
revisado.
General
 Crear migraciones.
 Ejecutar migraciones.
 Revisar estructura en PostgreSQL.
 Crear diagrama entidad-relación actualizado.
6. Layout general de la tienda
 Crear base.html.
 Crear navbar.
 Agregar logo.
 Agregar enlace Home.
 Agregar Productos.
 Agregar Nosotros.
 Agregar Blog.
 Agregar Contacto.
 Agregar Iniciar sesión.
 Agregar Registro.
 Mostrar nombre de usuario cuando esté autenticado.
 Agregar cerrar sesión.
 Mostrar acceso administrador solo cuando corresponda.
 Crear footer.
 Hacer diseño responsive.
 Integrar Bootstrap 5.
 Comprobar funcionamiento móvil.
7. Página principal

Según su diagrama:

 Crear ruta /.
 Crear vista Home.
 Crear template Home.
 Crear sección principal/hero.
 Mostrar productos destacados.
 Crear acceso a productos.
 Crear acceso a blog.
 Crear acceso a Nosotros.
 Crear acceso a Contacto.
 Crear acceso a login.
 Crear acceso a registro.
 Revisar responsive.
8. Registro de usuarios
 Crear ruta /registro/.
 Crear formulario.
 Pedir nombre.
 Pedir apellido.
 Pedir username o email.
 Pedir contraseña.
 Confirmar contraseña.
 Validar email.
 Validar contraseñas.
 Evitar usuarios duplicados.
 Mostrar errores correctamente.
 Crear usuario en PostgreSQL.
 Hashear contraseña mediante Django.
 Mostrar mensaje de registro exitoso.
 Redirigir a login o iniciar sesión automáticamente.
 Probar registros inválidos.
9. Inicio y cierre de sesión
 Crear vista de login.
 Crear formulario de login.
 Validar credenciales.
 Mostrar error cuando sean incorrectas.
 Crear sesión.
 Redirigir según corresponda.
 Crear logout.
 Destruir sesión correctamente.
 Proteger páginas privadas.
 Evitar acceso administrativo sin login.
 Evitar acceso administrativo a usuarios comunes.
10. Productos — tienda

Según el lado izquierdo de su diagrama:

Listado
 Crear /productos/.
 Obtener productos desde PostgreSQL.
 Mostrar solo productos activos.
 Mostrar imagen.
 Mostrar nombre.
 Mostrar precio.
 Mostrar stock si corresponde.
 Crear botón "Ver producto".
Detalle
 Crear /productos/<id>/.
 Mostrar imagen.
 Mostrar nombre.
 Mostrar descripción.
 Mostrar precio.
 Mostrar disponibilidad.
 Manejar producto inexistente.
 Manejar producto desactivado.
Mejoras opcionales
 Buscador.
 Filtro por categoría.
 Ordenar por precio.
 Paginación.
11. Página Nosotros
 Crear /nosotros/.
 Explicar proyecto/empresa.
 Mostrar equipo.
 Agregar integrantes.
 Agregar roles.
 Mantener diseño coherente.
 Responsive.
12. Blog
Listado
 Crear /blog/.
 Mostrar publicaciones.
 Mostrar título.
 Mostrar imagen.
 Mostrar pequeño extracto.
 Mostrar fecha.
 Crear botón "Leer más".
Detalle
 Crear /blog/<id>/.
 Mostrar publicación completa.
 Mostrar autor.
 Mostrar fecha.
 Mostrar imagen.
 Manejar posts inexistentes.
 Mostrar solo publicaciones activas/publicadas.
13. Contacto
 Crear /contacto/.
 Crear formulario.
 Nombre.
 Email.
 Asunto.
 Mensaje.
 Validar campos.
 Guardar solicitudes en PostgreSQL.
 Mostrar mensaje de confirmación.
 Evitar doble envío accidental.

Opcional:

 Enviar correo.
 Mostrar mensajes en panel administrador.
14. Panel administrativo

Este es el lado derecho de su diagrama.

 Crear /administrador/.
 Exigir login.
 Exigir rol administrador.
 Crear dashboard.
 Mostrar menú:
Productos
Usuarios
Blog
Contactos.
 Crear navegación consistente.
 Agregar botón volver a la tienda.
 Agregar cerrar sesión.
15. Administración de productos
Mostrar productos
 Crear listado.
 Mostrar ID.
 Mostrar nombre.
 Mostrar precio.
 Mostrar stock.
 Mostrar estado.
 Mostrar editar.
 Mostrar eliminar/ver.
Nuevo producto
 Crear formulario.
 Nombre.
 Descripción.
 Precio.
 Stock.
 Imagen.
 Categoría si existe.
 Estado.
 Validaciones.
 Guardar en PostgreSQL.
 Mostrar mensaje de éxito.
Editar producto
 Cargar información actual.
 Permitir modificarla.
 Validar cambios.
 Guardar cambios.
 Mostrar confirmación.
Mostrar producto
 Crear vista administrativa de detalle.
 Mostrar toda la información.
Eliminar

Aunque no está dibujado claramente, yo lo agregaría.

 Crear opción eliminar.
 Solicitar confirmación.
 Decidir entre eliminación física o desactivar producto.
 Preferiblemente usar activo=False.
16. Administración de usuarios
Mostrar usuarios
 Crear listado.
 Mostrar nombre.
 Mostrar email.
 Mostrar username.
 Mostrar rol.
 Mostrar estado.
Nuevo usuario
 Crear formulario.
 Crear usuario.
 Asignar rol.
 Validar información.
 Hashear contraseña correctamente.
Editar usuario
 Cambiar nombre.
 Cambiar email.
 Cambiar rol.
 Activar/desactivar usuario.
Mostrar usuario
 Crear detalle.
 Mostrar información relevante.
Seguridad
 Evitar que usuarios normales cambien su propio rol.
 Impedir acceso a URLs administrativas mediante URL manual.
 Evitar que un admin accidentalmente elimine al último administrador, si quieren hacerlo más robusto.
17. Administración del blog

Aunque no aparece en la propuesta original del administrador, conviene muchísimo incluirlo.

 Listar publicaciones.
 Crear publicación.
 Editar publicación.
 Ver publicación.
 Eliminar/desactivar publicación.
 Subir imagen.
 Asociar autor.
 Publicar/despublicar.
18. Administración de mensajes

También recomendable:

 Mostrar mensajes de contacto.
 Mostrar detalle.
 Marcar como leído.
 Eliminar mensaje.
 Mostrar cantidad de mensajes pendientes.
19. Django Admin

Aunque hagan su propio dashboard:

 Registrar modelos en admin.py.
 Crear superusuario.
 Configurar visualización de productos.
 Configurar usuarios.
 Configurar posts.
 Configurar contactos.

Esto además les salva la vida si algo falla.

20. Permisos y seguridad

Muy importante para la evaluación:

 CSRF habilitado.
 Passwords hasheadas.
 Validación backend.
 Validación frontend.
 Protección de rutas administrativas.
 Comprobar rol del usuario desde servidor.
 No confiar solamente en ocultar botones.
 Variables sensibles mediante .env.
 .env incluido en .gitignore.
 Sanitizar/validar inputs.
 Restringir archivos permitidos.
 Limitar tamaño de imágenes.
 Crear páginas 403.
 Crear página 404.
 Crear página 500.
21. Diseño responsive
 Desktop.
 Notebook.
 Tablet.
 Celular.
 Navbar móvil.
 Cards adaptables.
 Formularios móviles.
 Tablas administrativas responsivas.
 Imágenes adaptables.
 Botones suficientemente grandes.
 Revisar textos desbordados.
22. UX
 Mostrar mensajes de éxito.
 Mostrar errores claros.
 Confirmar eliminación.
 Mantener botones consistentes.
 Usar mismo estilo de formularios.
 No dejar páginas vacías sin explicación.
 Mostrar estado "No hay productos".
 Mostrar estado "No hay publicaciones".
 Mostrar estado "No hay mensajes".
 Agregar indicadores de carga si fuese necesario.
 Mantener navegación clara.
23. Datos iniciales para presentación

Antes de presentar:

 Crear administrador.
 Crear usuarios de prueba.
 Crear mínimo 8-12 productos.
 Subir imágenes.
 Crear categorías.
 Crear 3-5 posts.
 Crear mensajes de contacto.
 Revisar que no haya información ridícula tipo "producto123 prueba xddd" en la demo 😭.
 Preparar datos creíbles.
24. Testing
Usuarios
 Registro correcto.
 Registro duplicado.
 Login correcto.
 Login incorrecto.
 Logout.
 Acceso administrador.
 Acceso denegado a cliente.
Productos
 Crear.
 Leer.
 Editar.
 Desactivar/eliminar.
 Precio inválido.
 Stock inválido.
 Imagen inválida.
Blog
 Crear.
 Editar.
 Mostrar.
 Eliminar.
Contacto
 Enviar correctamente.
 Email inválido.
 Campos vacíos.
Navegación
 Revisar todos los enlaces.
 Revisar botones.
 Revisar URLs inexistentes.
 Revisar responsive.
Automatizados
 Crear tests para modelos.
 Crear tests para vistas.
 Crear tests de permisos.
 Crear tests de formularios.
25. Git y trabajo colaborativo

Para cada funcionalidad:

 Crear issue.
 Crear rama desde develop.
 Desarrollar.
 Probar localmente.
 Hacer commits pequeños.
 Push.
 Pull Request.
 Otro integrante revisa.
 Corregir conflictos.
 Merge a develop.
 Probar develop.
 Cuando esté estable → main.

Eviten trabajar directamente en main.

26. Documentación
 Nombre del proyecto.
 Descripción.
 Objetivo.
 Integrantes.
 Tecnologías.
 Arquitectura.
 Requisitos.
 Instalación.
 Configuración PostgreSQL.
 Variables de entorno necesarias.
 Cómo ejecutar.
 Credenciales de prueba.
 Diagrama de navegación.
 Diagrama entidad-relación.
 Casos de uso.
 Modelo de datos.
 Capturas del sistema.
 Explicar roles.
 Explicar CRUD.
 Explicar medidas de seguridad.
27. Mejorar el diagrama actual

Su diagrama también debería evolucionar. Yo agregaría:

 Cerrar sesión.
 Recuperar contraseña, si se exige.
 Administrar blog.
 Administrar contacto.
 Eliminar/desactivar producto.
 Eliminar/desactivar usuario.
 Control de roles.
 Estados de error.
 Actualizar diagrama final después de implementar.
28. Preparar entrega
 Congelar requirements.txt.
 Limpiar código muerto.
 Eliminar print() de debugging.
 Eliminar comentarios innecesarios.
 Revisar nombres de variables.
 Revisar ortografía.
 Revisar responsive.
 Revisar errores de consola.
 Revisar errores Django.
 Probar desde cero.
 Clonar repo en otro computador.
 Instalar dependencias.
 Crear BD.
 Ejecutar migraciones.
 Confirmar que funciona sin archivos locales faltantes.
 Crear versión/tag de entrega.
29. Presentación

Los cuatro deberían poder explicar:

 Qué problema resuelve el proyecto.
 Qué hace Django.
 Qué hace PostgreSQL.
 Cómo se conecta Django a PostgreSQL.
 Qué es un modelo.
 Qué es una vista.
 Qué es un template.
 Qué es una migración.
 Qué es CRUD.
 Cómo funciona el login.
 Cómo funcionan las sesiones.
 Cómo funcionan los roles.
 Cómo protegen rutas administrativas.
 Cómo está estructurada la BD.
 Cómo trabajaron con Git.
 Qué hizo cada integrante.