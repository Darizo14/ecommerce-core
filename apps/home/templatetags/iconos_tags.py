from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Iconos SVG (estilo Feather) usados en la sección de beneficios.
# Heredan color vía `currentColor`.
ICONOS_SVG = {
    'seguro': (
        '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>'
        '<path d="M7 11V7a5 5 0 0 1 10 0v4"></path>'
    ),
    'envio': (
        '<rect x="1" y="3" width="15" height="13" rx="1"></rect>'
        '<polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon>'
        '<circle cx="5.5" cy="18.5" r="2.5"></circle>'
        '<circle cx="18.5" cy="18.5" r="2.5"></circle>'
    ),
    'garantia': (
        '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>'
    ),
    'atencion': (
        '<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>'
    ),
    'verificado': (
        '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>'
        '<polyline points="22 4 12 14.01 9 11.01"></polyline>'
    ),
    'compra': (
        '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>'
    ),
    'reembolso': (
        '<polyline points="1 4 1 10 7 10"></polyline>'
        '<path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path>'
    ),
    'soporte': (
        '<path d="M3 18v-6a9 9 0 0 1 18 0v6"></path>'
        '<path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"></path>'
    ),
}

ICONO_FALLBACK = 'seguro'


@register.filter
def render_icono(icono_key):
    """Devuelve el elemento <svg> completo del icono indicado (vacío si no existe)."""
    contenido = ICONOS_SVG.get(icono_key, '')
    if not contenido:
        return mark_safe('')
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
        'stroke-linejoin="round">{contenido}</svg>'
    ).format(contenido=contenido)
    return mark_safe(svg)
