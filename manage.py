#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from decouple import config


def main():
    """Run administrative tasks."""
    # Usa development como padrão para comandos de manage.py
    settings_module = config(
        'DJANGO_SETTINGS_MODULE', 
        default='financas.settings.development'
    )
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Log do ambiente ao executar runserver
    if 'runserver' in sys.argv:
        env = 'development' if 'development' in settings_module else 'production'
        print(f"🚀 Iniciando servidor em modo: {env.upper()}")
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()