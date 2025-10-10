"""
WSGI config for financas project.
"""

import os
from decouple import config
from django.core.wsgi import get_wsgi_application

# Para WSGI (produção), sempre use production settings
settings_module = config(
    'DJANGO_SETTINGS_MODULE', 
    default='financas.settings.production'
)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

application = get_wsgi_application()

print(f"✅ WSGI Application carregada com settings: {settings_module}")