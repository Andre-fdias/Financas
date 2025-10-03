from .base import *

DEBUG = False

# ==============================================================================
# SECURITY SETTINGS
# ==============================================================================

# It is crucial to set ALLOWED_HOSTS in your production environment variables.
# This is a fallback and should be configured properly for your domain.
# Example: ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
# In your .env for production:
# ALLOWED_HOSTS=.yourdomain.com,www.yourdomain.com

# Enforce HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True

# HSTS (HTTP Strict Transport Security)
# Uncomment and configure after you have confirmed your site works correctly over HTTPS
# SECURE_HSTS_SECONDS = 31536000  # 1 year
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

# Additional security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
