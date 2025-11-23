"""
Filtros personalizados para la app adoption.
"""
import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def remove_p_tags(value):
    """
    Elimina las etiquetas HTML <p> y </p> del texto, incluyendo sus atributos.
    
    Uso:
        {{ mascota.desc_fisica|remove_p_tags|safe }}
    """
    if not value:
        return value
    
    # Convertir a string si no lo es
    text = str(value)
    
    # Eliminar etiquetas <p> con cualquier atributo (case-insensitive)
    # Patrón regex para capturar <p>, <p >, <p class="...">, <P id="...">, etc.
    text = re.sub(r'<p[^>]*>', '', text, flags=re.IGNORECASE)
    # Eliminar etiquetas de cierre </p>
    text = re.sub(r'</p\s*>', '', text, flags=re.IGNORECASE)
    
    return mark_safe(text)

