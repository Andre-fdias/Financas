
import pytest
from core.forms import ContaBancariaForm, EntradaForm, SaidaForm
from core.factories import UserFactory, ContaBancariaFactory
from django.utils import timezone

pytestmark = pytest.mark.django_db

# Tests for ContaBancariaForm
def test_conta_bancaria_form_valid():
    user = UserFactory()
    data = {
        'nome_banco': '341',
        'tipo': 'corrente',
        'agencia': '1234',
        'numero_conta': '56789-0',
        'saldo_atual': '1000.00',
    }
    form = ContaBancariaForm(data=data, user=user)
    assert form.is_valid()

def test_conta_bancaria_form_invalid():
    user = UserFactory()
    data = {
        'nome_banco': 'itau',
    }
    form = ContaBancariaForm(data=data, user=user)
    assert not form.is_valid()

# Tests for EntradaForm
def test_entrada_form_valid():
    user = UserFactory()
    conta = ContaBancariaFactory(proprietario=user)
    data = {
        'conta_bancaria': conta.pk,
        'nome': 'Salario',
        'valor': '150.00',
        'data': timezone.now().date().strftime('%Y-%m-%d'),
        'forma_recebimento': 'pix',
    }
    form = EntradaForm(data=data, user=user)
    assert form.is_valid()

def test_entrada_form_invalid():
    user = UserFactory()
    data = {
        'nome': 'Salario',
    }
    form = EntradaForm(data=data, user=user)
    assert not form.is_valid()

# Tests for SaidaForm
def test_saida_form_valid():
    user = UserFactory()
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
    form = SaidaForm(data=data, user=user)
    assert form.is_valid()

def test_saida_form_invalid():
    user = UserFactory()
    data = {
        'nome': 'Aluguel',
    }
    form = SaidaForm(data=data, user=user)
    assert not form.is_valid()
