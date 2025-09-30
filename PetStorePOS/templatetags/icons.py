from django import template
from django.utils.safestring import mark_safe
from pathlib import Path

register = template.Library()

@register.simple_tag
def icon(name):
    path = Path(__file__).resolve().parent.parent / "img/icons" / f"{name}.svg"
    return mark_safe(path.read_text())
# Usage in template: {% load icons %} {% icon 'icon_name' %}
# Example SVG files should be placed in the 'img/icons' directory.
