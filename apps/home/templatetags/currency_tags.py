from django import template
from django.conf import settings

register = template.Library()


@register.filter
def currency_format(value, currency_code='USD'):
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0.0

    rate = getattr(settings, 'USD_TO_CUP_RATE', 680)

    if currency_code == 'CUP':
        converted = value * rate
        return f'${converted:,.2f} CUP'

    return f'${value:,.2f}'
