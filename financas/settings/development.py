from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Configurações específicas para desenvolvimento
ALLOWED_HOSTS = ['*']  # Permite todos os hosts em desenvolvimento

# Configurações de segurança relaxadas para desenvolvimento
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# CORS para desenvolvimento
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Configurações de sessão para desenvolvimento
SESSION_COOKIE_AGE = 1209600  # 2 semanas
SESSION_SAVE_EVERY_REQUEST = True

# Database connection para desenvolvimento
DATABASES['default']['CONN_MAX_AGE'] = 0  # Desativa connection pooling

# Logging mais detalhado em desenvolvimento
LOGGING['loggers']['django']['level'] = 'DEBUG'
LOGGING['loggers']['core']['level'] = 'DEBUG'

# Adiciona renderizador de API browsable em desenvolvimento
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] += (
    'rest_framework.renderers.BrowsableAPIRenderer',
)

# Email para desenvolvimento (console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Cache dummy para desenvolvimento (mais rápido)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Debug toolbar (opcional - remova se não quiser)
try:
    import debug_toolbar
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
    print("🔧 Debug Toolbar ativado")
except ImportError:
    pass

# Informações do ambiente
db_engine = DATABASES['default']['ENGINE']
db_name = DATABASES['default'].get('NAME', 'N/A')

print("=" * 60)
print("🛠️  MODO DESENVOLVIMENTO ATIVADO")
print(f"📊 Database: {db_engine}")
print(f"📁 DB Name: {db_name}")
print(f"📧 Email: {EMAIL_BACKEND}")
print(f"🔒 SSL: {SECURE_SSL_REDIRECT}")
print(f"🌐 Allowed Hosts: {ALLOWED_HOSTS}")
print("=" * 60)