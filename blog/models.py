# mi_blog_django/blog/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager # Importar para modelo de usuario personalizado si lo usas
from django.utils.text import slugify
from django.utils import timezone # Para manejar fechas y horas con zonas horarias

# Nota: Django ya tiene un modelo de usuario robusto (django.contrib.auth.models.User).
# Si solo necesitas los campos básicos (username, password, is_admin), puedes extenderlo
# o usarlo directamente. Aquí te pongo cómo podrías definir tu propio modelo de usuario
# si necesitaras campos muy específicos, aunque para empezar es más fácil usar el de Django.
# Por simplicidad, en este ejemplo usaremos el User de Django, pero mantenemos tu idea de is_admin.

# Si quieres usar el User de Django y solo añadir is_admin, es mejor extender AbstractUser.
# Pero para empezar, vamos a usar el User por defecto y asumimos que 'is_admin' se gestiona
# a través del grupo 'staff' o 'superuser' en el admin de Django.
# Si más adelante necesitas campos extra para el usuario, usarías una técnica de "Custom User Model".

# Vamos a asumir que usaremos el modelo de usuario por defecto de Django para la relación.
# Si quieres añadir 'is_admin' a ese modelo, necesitarías un Custom User Model.
# Por ahora, simplemente nos relacionamos con settings.AUTH_USER_MODEL.
from django.conf import settings

class Categoria(models.Model):
    # Django automáticamente crea un campo 'id' como Primary Key
    nombre = models.CharField(max_length=100, unique=True) # unique=True para que no haya categorías con el mismo nombre
    slug = models.CharField(max_length=100, unique=True, blank=True) # blank=True para que no sea obligatorio en el form

    class Meta:
        verbose_name_plural = "Categorías" # Nombre amigable en el panel de admin

    def save(self, *args, **kwargs):
        if not self.slug: # Si el slug no está definido, lo genera
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self): # Equivalente a __repr__ pero para representaciones amigables
        return self.nombre

class Articulo(models.Model):
    titulo = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(auto_now_add=True) # Se establece automáticamente la primera vez
    fecha_publicacion = models.DateTimeField(null=True, blank=True) # Puede estar vacío
    slug = models.CharField(max_length=255, unique=True, blank=True)
    # Relación con el modelo de usuario por defecto de Django
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    meta_descripcion = models.CharField(max_length=500, blank=True)
    palabras_clave = models.CharField(max_length=255, blank=True)

    # Relación Many-to-Many con Categoria
    categorias = models.ManyToManyField(Categoria, related_name='articulos_relacionados', blank=True)

    class Meta:
        ordering = ['-fecha_creacion'] # Ordena los artículos por fecha de creación descendente

    def save(self, *args, **kwargs):
        if not self.slug: # Si el slug no está definido, lo genera
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo

class BloqueContenido(models.Model):
    # Relación One-to-Many con Articulo
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE, related_name='bloques')

    # Opciones para tipo_bloque
    TIPO_BLOQUE_CHOICES = [
        ('titulo', 'Título'),
        ('parrafo', 'Párrafo'),
        ('imagen', 'Imagen'),
        ('lista', 'Lista'),
        ('codigo', 'Código'), # Añadido para un programador :)
        ('otro', 'Otro'),
    ]
    tipo_bloque = models.CharField(max_length=20, choices=TIPO_BLOQUE_CHOICES, default='parrafo')

    orden = models.IntegerField(default=0) # Para definir el orden de los bloques

    contenido_texto = models.TextField(blank=True, null=True) # Para párrafos, títulos, listas, código
    ruta_imagen = models.ImageField(upload_to='imagenes_bloques/', blank=True, null=True) # Requiere pillow
    datos_adicionales = models.JSONField(blank=True, null=True) # Para datos JSON extra

    class Meta:
        ordering = ['orden'] # Asegura que los bloques se muestran en el orden correcto
        verbose_name_plural = "Bloques de Contenido"

    def __str__(self):
        return f"Bloque {self.orden} de {self.articulo.titulo} ({self.get_tipo_bloque_display()})"

# Nota sobre TokenBlocklist:
# Para JWTs en Django, normalmente usarías una librería como `djangorestframework-simplejwt`
# que ya tiene su propia implementación de token blocklist.
# No es necesario migrar este modelo si usas esa librería, ya que la librería lo gestiona.
# Si de todas formas lo quisieras tener, sería así:
# class TokenBlocklist(models.Model):
#    jti = models.CharField(max_length=36, unique=True, db_index=True)
#    created_at = models.DateTimeField(auto_now_add=True)
#
#    def __str__(self):
#        return self.jti