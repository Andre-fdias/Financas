from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# ALLOWED_HOSTS é configurado via variável de ambiente no base.py

# Configurações de segurança para HTTPS e cookies seguros
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

# Configurações de HSTS (HTTP Strict Transport Security)
# Aumente o valor de SECURE_HSTS_SECONDS em um ambiente de produção real
SECURE_HSTS_SECONDS = 3600  # 1 hora
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_CONTENT_TYPE_NOSNIFF = True
