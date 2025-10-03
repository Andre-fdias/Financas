from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class CoreViewsTest(TestCase):
    """Testes para as views do app core."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_home_page_redirects_for_anonymous_user(self):
        """Verifica se a página inicial (home) redireciona usuários anônimos."""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_page_redirects_for_anonymous_user(self):
        """Verifica se o dashboard redireciona se o usuário não estiver logado."""
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/dashboard/')

    def test_dashboard_page_loads_for_logged_in_user(self):
        """Verifica se o dashboard carrega corretamente para um usuário logado."""
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)