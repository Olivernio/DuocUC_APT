"""
Context processors para hacer variables disponibles en todos los templates.
"""
from django.conf import settings


def openai_chatbot(request):
    """
    Hace disponible la configuración de OpenAI Chatbot en todos los templates.
    """
    return {
        'OPENAI_ENABLED': getattr(settings, 'OPENAI_ENABLED', False),
    }

