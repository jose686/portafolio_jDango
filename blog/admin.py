# backend_jDango/blog/admin.py

from django.contrib import admin
from django.utils import timezone # Importar timezone para la lógica de publicación
from django.db import models # Necesario para Q objects en PublicadoListFilter

# Importa tus modelos desde el mismo directorio
from .models import Articulo, BloqueContenido, Categoria

# 1. Definir el Inline para BloqueContenido
class BloqueContenidoInline(admin.StackedInline): # O admin.TabularInline para un formato de tabla
    model = BloqueContenido
    extra = 1 # Cuántos formularios vacíos mostrar para añadir nuevos bloques
    # Es recomendable listar los campos que quieres que aparezcan, para tener control.
    fields = ['tipo_bloque', 'contenido_texto', 'ruta_imagen', 'orden']
    # Si quieres campos de solo lectura (por ejemplo, 'fecha_creacion' si lo tuvieras en BloqueContenido):
    # readonly_fields = ['fecha_creacion']

# 2. Definir un filtro personalizado para el estado de Publicación
class PublicadoListFilter(admin.SimpleListFilter):
    title = 'Estado de publicación' # Título que se mostrará en el filtro del admin
    parameter_name = 'estado_publicacion' # Nombre del parámetro en la URL

    def lookups(self, request, model_admin):
        # Devuelve una lista de tuplas (valor_parametro, etiqueta_para_mostrar)
        return [
            ('publicado', 'Publicado'),
            ('no_publicado', 'No Publicado'),
        ]

    def queryset(self, request, queryset):
        # Implementa la lógica de filtrado
        if self.value() == 'publicado':
            return queryset.filter(fecha_publicacion__isnull=False, fecha_publicacion__lte=timezone.now())
        if self.value() == 'no_publicado':
            # Artículos sin fecha_publicacion o con fecha_publicacion futura
            return queryset.filter(
                models.Q(fecha_publicacion__isnull=True) | models.Q(fecha_publicacion__gt=timezone.now())
            )
        return queryset # Devuelve el queryset sin filtrar si no se selecciona ninguna opción

# 3. Registrar Articulo con el inline y un método personalizado para 'publicado'
@admin.register(Articulo) # Usa el decorador para registrar el modelo Articulo
class ArticuloAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'slug', 'fecha_publicacion', 'publicado', 'categoria_display')
    list_filter = (PublicadoListFilter, 'fecha_publicacion') # Usa el filtro personalizado
    search_fields = ('titulo', 'meta_descripcion') # Ajustado, ya que el contenido de los bloques está en BloqueContenido

    prepopulated_fields = {'slug': ('titulo',)}
    ordering = ('-fecha_publicacion',)
    date_hierarchy = 'fecha_publicacion' # Permite navegar por fechas

    # Aquí es donde se añaden los inlines
    inlines = [BloqueContenidoInline]

    # METODO PERSONALIZADO PARA 'PUBLICADO'
    def publicado(self, obj):
        # Un artículo se considera publicado si tiene una fecha_publicacion
        # y esa fecha es igual o anterior a la fecha y hora actuales.
        if obj.fecha_publicacion and obj.fecha_publicacion <= timezone.now():
            return True
        return False
    publicado.boolean = True # Esto hace que Django muestre un icono de check/cruz
    publicado.short_description = 'Publicado' # Nombre de la columna en el admin

    # Método para mostrar las categorías
    def categoria_display(self, obj):
        return ", ".join([cat.nombre for cat in obj.categorias.all()]) if obj.categorias.exists() else "N/A"
    categoria_display.short_description = 'Categorías' # Nombre de la columna en el admin

# 4. Registrar Categoria (BloqueContenido no se registra directamente si solo se usa en inlines)
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}

# # Ya no necesitas estas líneas si usas @admin.register
# admin.site.register(Categoria)
# admin.site.register(Articulo)
# admin.site.register(BloqueContenido) # No se registra directamente si lo usas como inline