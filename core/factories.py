import factory
from django.contrib.auth.models import User
from core.models import ContaBancaria, Categoria, Entrada, Saida, Profile
from decimal import Decimal
from django.utils import timezone

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'defaultpassword')

class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    user = factory.SubFactory(UserFactory)
    telefone = factory.Faker('phone_number')
    cidade = factory.Faker('city')

class ContaBancariaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ContaBancaria

    proprietario = factory.SubFactory(UserFactory)
    nome_banco = 'itau'
    tipo = 'corrente'
    agencia = factory.Faker('numerify', text='####')
    numero_conta = factory.Faker('numerify', text='#####-#')
    saldo_atual = Decimal('1000.00')

class CategoriaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Categoria

    usuario = factory.SubFactory(UserFactory)
    nome = factory.Faker('word')

class EntradaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Entrada

    usuario = factory.SubFactory(UserFactory)
    conta_bancaria = factory.SubFactory(ContaBancariaFactory)
    nome = factory.Faker('word')
    valor = Decimal('100.00')

class SaidaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Saida

    usuario = factory.SubFactory(UserFactory)
    conta_bancaria = factory.SubFactory(ContaBancariaFactory)
    nome = factory.Faker('word')
    valor = Decimal('50.00')
    data_vencimento = factory.LazyFunction(timezone.now)
