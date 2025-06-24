from django import template
from django.template.defaultfilters import stringfilter # Importamos para usar @stringfilter

register = template.Library()

@register.filter(name='split_lines')
@stringfilter
def split_lines(value):
    """
    Divide una cadena de texto en una lista de líneas.
    """
    return value.splitlines()

@register.filter(name='trim') # Registramos el filtro 'trim'
@stringfilter
def trim_filter(value): # Le ponemos un nombre de función diferente para evitar conflictos si ya existe
    """
    Elimina los espacios en blanco al principio y al final de una cadena.
    """
    return value.strip()