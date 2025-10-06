from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from django.core.exceptions import ValidationError

from .models import ContaBancaria, Entrada, Saida, Transferencia, Profile

class CoreViewsTestCase(TestCase):
    def setUp(self):
        """
        Configuração inicial para os testes. Cria um usuário e faz login.
        """
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        
        self.conta_origem = ContaBancaria.objects.create(
            proprietario=self.user,
            nome_banco='itau',
            tipo='corrente',
            agencia='1234',
            numero_conta='56789-0',
            saldo_atual=Decimal('1000.00')
        )
        
        self.conta_destino = ContaBancaria.objects.create(
            proprietario=self.user,
            nome_banco='nubank',
            tipo='poupanca',
            agencia='0001',
            numero_conta='11223-3',
            saldo_atual=Decimal('500.00')
        )

    def test_dashboard_view_authenticated(self):
        """
        Verifica se a view do dashboard está acessível para um usuário logado.
        """
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/dashboard.html')

    def test_unauthenticated_access_redirects_to_login(self):
        """
        Verifica se um usuário não logado é redirecionado para a página de login.
        """
        self.client.logout()
        response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('core:login')}?next={reverse('core:dashboard')}")

    def test_conta_list_view(self):
        """
        Testa se a lista de contas é renderizada corretamente.
        """
        response = self.client.get(reverse('core:conta_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.conta_origem.get_nome_banco_display())
        self.assertContains(response, self.conta_destino.get_nome_banco_display())

    def test_entrada_list_view(self):
        """
        Testa se a lista de entradas é renderizada corretamente.
        """
        Entrada.objects.create(
            usuario=self.user,
            conta_bancaria=self.conta_origem,
            nome='Salário',
            valor=Decimal('500.00'),
            data=timezone.now().date()
        )
        response = self.client.get(reverse('core:entrada_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Salário')

    def test_saida_list_view(self):
        """
        Testa se a lista de saídas é renderizada corretamente.
        """
        Saida.objects.create(
            usuario=self.user,
            conta_bancaria=self.conta_origem,
            nome='Aluguel',
            valor=Decimal('300.00'),
            data_lancamento=timezone.now().date(),
            data_vencimento=timezone.now().date()
        )
        response = self.client.get(reverse('core:saida_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Aluguel')

    def test_create_entrada_view(self):
        """
        Testa a criação de uma nova entrada via POST request.
        """
        entradas_count_before = Entrada.objects.count()
        response = self.client.post(reverse('core:entrada_create'), {
            'conta_bancaria': self.conta_origem.pk,
            'nome': 'Freelance',
            'valor': '150.00',
            'data': timezone.now().date().strftime('%Y-%m-%d'),
            'forma_recebimento': 'pix',
        })
        self.assertEqual(response.status_code, 302) # Deve redirecionar após sucesso
        self.assertRedirects(response, reverse('core:entrada_list'))
        self.assertEqual(Entrada.objects.count(), entradas_count_before + 1)
        self.assertTrue(Entrada.objects.filter(nome='Freelance').exists())

    def test_create_saida_view(self):
        """
        Testa a criação de uma nova saída via POST request.
        """
        saidas_count_before = Saida.objects.count()
        response = self.client.post(reverse('core:saida_create'), {
            'conta_bancaria': self.conta_origem.pk,
            'nome': 'Supermercado',
            'valor': '250.00',
            'data_lancamento': timezone.now().date().strftime('%Y-%m-%d'),
            'data_vencimento': timezone.now().date().strftime('%Y-%m-%d'),
            'forma_pagamento': 'debito',
            'situacao': 'pago',
            'tipo_pagamento_detalhe': 'avista',
            'recorrente': 'unica',
            'quantidade_parcelas': 1
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:saida_list'))
        self.assertEqual(Saida.objects.count(), saidas_count_before + 1)
        self.assertTrue(Saida.objects.filter(nome='Supermercado').exists())


class CoreModelsTestCase(TestCase):
    def setUp(self):
        """
        Configuração inicial para os testes de modelo.
        """
        self.user = User.objects.create_user(username='modeluser', password='modelpassword')
        self.conta = ContaBancaria.objects.create(
            proprietario=self.user,
            nome_banco='bradesco',
            tipo='corrente',
            agencia='0011',
            numero_conta='22334-4',
            saldo_atual=Decimal('2000.00')
        )

    def test_user_profile_creation(self):
        """
        Verifica se um Profile é criado automaticamente quando um User é criado.
        """
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, Profile)

    def test_conta_bancaria_creation(self):
        """
        Testa a criação e representação em string de uma ContaBancaria.
        """
        self.assertEqual(str(self.conta), 'bradesco - 0011/22334-4')
        self.assertEqual(ContaBancaria.objects.count(), 1)

    def test_entrada_creation(self):
        """
        Testa a criação de uma Entrada.
        """
        entrada = Entrada.objects.create(
            usuario=self.user,
            conta_bancaria=self.conta,
            nome='Venda de produto',
            valor=Decimal('100.00'),
            data=timezone.now().date()
        )
        self.assertEqual(Entrada.objects.count(), 1)
        self.assertEqual(entrada.valor, Decimal('100.00'))

    def test_saida_parcelada_validation(self):
        """
        Testa a validação de uma Saída parcelada com quantidade de parcelas inválida.
        """
        saida = Saida(
            usuario=self.user,
            conta_bancaria=self.conta,
            nome='Compra parcelada',
            valor=Decimal('1000.00'),
            tipo_pagamento_detalhe='parcelado',
            quantidade_parcelas=1 # Inválido para parcelado
        )
        with self.assertRaises(ValidationError) as cm:
            saida.clean()
        self.assertIn('quantidade_parcelas', cm.exception.message_dict)

    def test_saida_recorrente_parcelada_validation(self):
        """
        Testa a validação que impede uma Saída de ser recorrente e parcelada ao mesmo tempo.
        """
        saida = Saida(
            usuario=self.user,
            conta_bancaria=self.conta,
            nome='Assinatura parcelada',
            valor=Decimal('120.00'),
            tipo_pagamento_detalhe='parcelado',
            quantidade_parcelas=12,
            recorrente='mensal' # Inválido com parcelado
        )
        with self.assertRaises(ValidationError) as cm:
            saida.clean()
        self.assertIn('recorrente', cm.exception.message_dict)

    def test_transferencia_saldo_insuficiente(self):
        """
        Testa a validação de transferência com saldo insuficiente na conta de origem.
        """
        conta_destino = ContaBancaria.objects.create(
            proprietario=self.user,
            nome_banco='inter',
            tipo='corrente',
            agencia='0001',
            numero_conta='12345-6',
            saldo_atual=Decimal('100.00')
        )
        transferencia = Transferencia(
            usuario=self.user,
            conta_origem=self.conta,
            conta_destino=conta_destino,
            valor=Decimal('3000.00') # Maior que o saldo da conta de origem
        )
        with self.assertRaises(ValidationError):
            transferencia.clean()

    def test_transferencia_successful(self):
        """
        Testa uma transferência bem-sucedida e a atualização dos saldos.
        """
        saldo_origem_before = self.conta.saldo_atual
        
        conta_destino = ContaBancaria.objects.create(
            proprietario=self.user,
            nome_banco='inter',
            tipo='corrente',
            agencia='0001',
            numero_conta='12345-6',
            saldo_atual=Decimal('100.00')
        )
        saldo_destino_before = conta_destino.saldo_atual
        
        valor_transferencia = Decimal('500.00')

        # A lógica de atualização de saldo está no método save()
        transferencia = Transferencia(
            usuario=self.user,
            conta_origem=self.conta,
            conta_destino=conta_destino,
            valor=valor_transferencia
        )
        transferencia.save()

        # Recarrega as contas do banco de dados para verificar os saldos atualizados
        self.conta.refresh_from_db()
        conta_destino.refresh_from_db()

        self.assertEqual(self.conta.saldo_atual, saldo_origem_before - valor_transferencia)
        self.assertEqual(conta_destino.saldo_atual, saldo_destino_before + valor_transferencia)
        self.assertEqual(Transferencia.objects.count(), 1)