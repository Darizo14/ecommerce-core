from django.conf import settings


def currency_context(request):
    current_currency = request.session.get('currency', 'USD')
    return {
        'current_currency': current_currency,
        'exchange_rate': getattr(settings, 'USD_TO_CUP_RATE', 680),
        'currencies': ['USD', 'CUP'],
    }
