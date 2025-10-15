from django.conf import settings
from financas import __version__ as app_version

def version_context(request):
    """
    Fornece a versão da aplicação e informações de build para todos os templates.
    """
    return {
        'APP_VERSION': app_version,
        'BUILD_DATE': '',  # O CHANGELOG.md será a fonte da verdade para datas
        'BUILD_HASH': '',  # O CHANGELOG.md será a fonte da verdade para hashes
    }
