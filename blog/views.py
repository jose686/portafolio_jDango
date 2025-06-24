from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from .models import Articulo, BloqueContenido
from django.utils import timezone # Importa timezone para filtrar por fecha de publicación

app_name = 'blog' 


def lista_articulos(request):
    # Obtener artículos publicados y ordenados por fecha de publicación
    articulos = Articulo.objects.filter(
        fecha_publicacion__isnull=False,
        fecha_publicacion__lte=timezone.now()
    ).order_by('-fecha_publicacion')

    # Añadir dinámicamente la URL de la primera imagen de bloque a cada artículo
    for articulo in articulos:
        primera_imagen_bloque = BloqueContenido.objects.filter(
            articulo=articulo,
            tipo_bloque='imagen'
        ).order_by('orden').first()

        # Asignar una URL de imagen, o None si no hay imagen de bloque
        articulo.display_image_url = primera_imagen_bloque.ruta_imagen.url if primera_imagen_bloque and primera_imagen_bloque.ruta_imagen else None

    context = {
        'articulos': articulos, # Pasamos la lista de artículos directamente como la plantilla la espera
        # Puedes añadir is_loading y error_message si tu front-end los gestiona,
        # pero en Django el render es síncrono, por lo que suelen ser False/None por defecto.
        # 'is_loading': False,
        # 'error_message': None,
    }
    return render(request, 'blog/lista_articulos.html', context)

def detalle_articulo(request, slug):
    articulo = get_object_or_404(
        Articulo,
        slug=slug,
        fecha_publicacion__isnull=False,
        fecha_publicacion__lte=timezone.now()
    )
    # **ESTO ES CLAVE:** Obtener los bloques de contenido asociados y ordenarlos.
    bloques = BloqueContenido.objects.filter(articulo=articulo).order_by('orden')

    context = {
        'articulo': articulo,
        'bloques': bloques, # Asegúrate de que esta línea esté presente y pase 'bloques'
    }
    return render(request, 'blog/detalle_articulo.html', context)

def sobre_mi(request):
    return render(request, 'blog/about.html')

def contacto(request):
    return render(request, 'blog/contact.html')