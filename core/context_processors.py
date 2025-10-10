# core/context_processors.py
from django.conf import settings

def messages_config(request):
    """
    Context processor para configurações de mensagens
    """
    return {
        'MESSAGE_TIMEOUT': 5000,  # 5 segundos em milissegundos
        'DEBUG': settings.DEBUG,
    }