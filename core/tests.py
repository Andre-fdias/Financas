
import pytest
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from django.core.exceptions import ValidationError
from core.models import ContaBancaria, Entrada, Saida, Transferencia, Profile
from core.factories import UserFactory, ContaBancariaFactory, EntradaFactory, SaidaFactory

pytestmark = pytest.mark.django_db

# Tests for Views
def test_dashboard_view_authenticated(client, django_user_model):
    user = UserFactory()
    client.force_login(user)
    response = client.get(reverse('core:dashboard'))
    assert response.status_code == 200
    assert 'core/dashboard.html' in [t.name for t in response.templates]

def test_unauthenticated_access_redirects_to_login(client):
    response = client.get(reverse('core:dashboard'))
    assert response.status_code == 302
    assert response.url == f"{reverse('core:login')}?next={reverse('core:dashboard')}"

def test_conta_list_view(client):
    user = UserFactory()
    client.force_login(user)
    conta1 = ContaBancariaFactory(proprietario=user)
    conta2 = ContaBancariaFactory(proprietario=user)
    response = client.get(reverse('core:conta_list'))
    assert response.status_code == 200
    assert response.context['contas'].count() == 2
    assert conta1 in response.context['contas']
    assert conta2 in response.context['contas']

def test_entrada_list_view(client):
    user = UserFactory()
    client.force_login(user)
    conta = ContaBancariaFactory(proprietario=user)
    entrada = EntradaFactory(usuario=user, conta_bancaria=conta)
    response = client.get(reverse('core:entrada_list'))
    assert response.status_code == 200
    assert entrada in response.context['entradas']

def test_saida_list_view(client):
    user = UserFactory()
    client.force_login(user)
    conta = ContaBancariaFactory(proprietario=user)
    saida = SaidaFactory(usuario=user, conta_bancaria=conta)
    response = client.get(reverse('core:saida_list'))
    assert response.status_code == 200
    assert saida in response.context['saidas']

def test_create_entrada_view(client):
    user = UserFactory()
    client.force_login(user)
    conta = ContaBancariaFactory(proprietario=user)
    data = {
        'conta_bancaria': conta.pk,
        'nome': 'Salario',
        'valor': '150.00',
        'data': timezone.now().date().strftime('%Y-%m-%d'),
        'forma_recebimento': 'pix',
    }
    response = client.post(reverse('core:entrada_create'), data)
    assert response.status_code == 302
    assert response.url == reverse('core:entrada_list')
    assert Entrada.objects.filter(nome='Salario').exists()

def test_create_saida_view(client):
    user = UserFactory()
    client.force_login(user)
    conta = ContaBancariaFactory(proprietario=user)
    data = {
        'conta_bancaria': conta.pk,
        'nome': 'Aluguel',
        'valor': '250.00',
        'valor_parcela': '250.00',
        'data_lancamento': timezone.now().date().strftime('%Y-%m-%d'),
        'data_vencimento': timezone.now().date().strftime('%Y-%m-%d'),
        'forma_pagamento': 'cartao_debito',
        'situacao': 'pago',
        'tipo_pagamento_detalhe': 'avista',
        'recorrente': 'unica',
        'quantidade_parcelas': 1
    }
    response = client.post(reverse('core:saida_create'), data)
    assert response.status_code == 302
    assert response.url == reverse('core:saida_list')
    assert Saida.objects.filter(nome='Aluguel').exists()

def test_entrada_update_view(client):
    user = UserFactory()
    client.force_login(user)
    conta = ContaBancariaFactory(proprietario=user)
    entrada = EntradaFactory(usuario=user, conta_bancaria=conta, nome='Old Name')
    data = {
        'conta_bancaria': conta.pk,
        'nome': 'New Name',
        'valor': '200.00',
        'data': timezone.now().date().strftime('%Y-%m-%d'),
        'forma_recebimento': 'pix',
    }
    response = client.post(reverse('core:entrada_update', kwargs={'pk': entrada.pk}), data)
    assert response.status_code == 302
    assert response.url == reverse('core:entrada_list')
    entrada.refresh_from_db()
    assert entrada.nome == 'New Name'

def test_saida_update_view(client):
    user = UserFactory()
    client.force_login(user)
    conta = ContaBancariaFactory(proprietario=user)
    saida = SaidaFactory(usuario=user, conta_bancaria=conta, nome='Old Name')
    data = {
        'conta_bancaria': conta.pk,
        'nome': 'New Name',
        'valor': '300.00',
        'valor_parcela': '300.00',
        'data_lancamento': timezone.now().date().strftime('%Y-%m-%d'),
        'data_vencimento': timezone.now().date().strftime('%Y-%m-%d'),
        'forma_pagamento': 'cartao_credito',
        'situacao': 'pendente',
        'tipo_pagamento_detalhe': 'avista',
        'recorrente': 'unica',
        'quantidade_parcelas': 1
    }
    response = client.post(reverse('core:saida_update', kwargs={'pk': saida.pk}), data)
    assert response.status_code == 302
    assert response.url == reverse('core:saida_list')
    saida.refresh_from_db()
    assert saida.nome == 'New Name'

def test_entrada_delete_view(client):
    user = UserFactory()
    client.force_login(user)
    entrada = EntradaFactory(usuario=user)
    response = client.post(reverse('core:entrada_delete', kwargs={'pk': entrada.pk}))
    assert response.status_code == 302
    assert response.url == reverse('core:entrada_list')
    assert not Entrada.objects.filter(pk=entrada.pk).exists()

def test_saida_delete_view(client):
    user = UserFactory()
    client.force_login(user)
    saida = SaidaFactory(usuario=user)
    response = client.post(reverse('core:saida_delete', kwargs={'pk': saida.pk}))
    assert response.status_code == 302
    assert response.url == reverse('core:saida_list')
    assert not Saida.objects.filter(pk=saida.pk).exists()

# Tests for Models
def test_user_profile_creation():
    user = UserFactory()
    assert hasattr(user, 'profile')
    assert isinstance(user.profile, Profile)

def test_conta_bancaria_creation():
    conta = ContaBancariaFactory()
    assert isinstance(conta, ContaBancaria)
    assert str(conta) == f'{conta.get_nome_banco_display()} - {conta.agencia}/{conta.numero_conta}'

def test_entrada_creation():
    entrada = EntradaFactory()
    assert isinstance(entrada, Entrada)
    assert entrada.valor == Decimal('100.00')

def test_saida_parcelada_validation():
    with pytest.raises(ValidationError, match='Para pagamento parcelado, o número de parcelas deve ser maior que 1.'):
        SaidaFactory.build(tipo_pagamento_detalhe='parcelado', quantidade_parcelas=1).clean()

def test_saida_recorrente_parcelada_validation():
    with pytest.raises(ValidationError, match='Não é possível ter recorrência em pagamentos parcelados.'):
        SaidaFactory.build(tipo_pagamento_detalhe='parcelado', recorrente='mensal', quantidade_parcelas=2).clean()

def test_transferencia_saldo_insuficiente():
    user = UserFactory()
    conta_origem = ContaBancariaFactory(proprietario=user, saldo_atual=Decimal('100.00'))
    conta_destino = ContaBancariaFactory(proprietario=user)
    with pytest.raises(ValidationError, match='Saldo insuficiente na conta de origem.'):
        Transferencia(usuario=user, conta_origem=conta_origem, conta_destino=conta_destino, valor=Decimal('200.00')).clean()

def test_transferencia_successful():
    user = UserFactory()
    conta_origem = ContaBancariaFactory(proprietario=user, saldo_atual=Decimal('1000.00'))
    conta_destino = ContaBancariaFactory(proprietario=user, saldo_atual=Decimal('500.00'))
    
    valor_transferencia = Decimal('200.00')
    
    transferencia = Transferencia(
        usuario=user,
        conta_origem=conta_origem,
        conta_destino=conta_destino,
        valor=valor_transferencia
    )
    transferencia.save()

    conta_origem.refresh_from_db()
    conta_destino.refresh_from_db()

    assert conta_origem.saldo_atual == Decimal('800.00')
    assert conta_destino.saldo_atual == Decimal('700.00')
