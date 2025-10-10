"""
ASGI config for financas project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from decouple import config
from django.core.asgi import get_asgi_application

# Define o ambiente para produção em ASGI
settings_module = config(
    'DJANGO_SETTINGS_MODULE', 
    default='financas.settings.production'  # Padrão é produção para ASGI
)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

application = get_asgi_application()

print(f"✅ ASGI Application carregada com settings: {settings_module}")