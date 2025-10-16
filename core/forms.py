from decimal import Decimal, InvalidOperation
import os
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models # <-- Adicione esta linha
from .choices import CATEGORIA_CHOICES
from .models import (
    ContaBancaria, Entrada, Saida, Transferencia, 
    Profile, Lembrete, OperacaoSaque, Categoria, Subcategoria
)

from .choices import TIPO_OPERACAO_CHOICES


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ("username", "email")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está em uso. Por favor, escolha outro.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class ContaBancariaForm(forms.ModelForm):
    class Meta:
        model = ContaBancaria
        fields = ['nome_banco', 'tipo', 'agencia', 'numero_conta', 'saldo_atual',
                  'numero_cartao', 'limite_cartao', 'dia_fechamento_fatura',
                  'dia_vencimento_fatura', 'ativa', 'nome_do_titular']  # Adicione o campo aqui
        widgets = {
            'nome_banco': forms.Select(attrs={'class': 'form-input'}),
            'tipo': forms.Select(attrs={'class': 'form-input'}),
            'agencia': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '0000'}),
            'numero_conta': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '00000-0'}),
            'saldo_atual': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': '0,00'}),
            'numero_cartao': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '**** **** **** ****'}),
            'limite_cartao': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': '0,00'}),
            'dia_fechamento_fatura': forms.NumberInput(attrs={'class': 'form-input', 'min': '1', 'max': '31', 'placeholder': '1-31'}),
            'dia_vencimento_fatura': forms.NumberInput(attrs={'class': 'form-input', 'min': '1', 'max': '31', 'placeholder': '1-31'}),
            'ativa': forms.CheckboxInput(attrs={'class': 'checkbox-input'}),
            'nome_do_titular': forms.TextInput(attrs={  # Adicione este widget
                'class': 'form-input',
                'placeholder': 'Nome do titular da conta (se diferente)'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')

        # Validações específicas para contas bancárias
        if tipo in ['corrente', 'poupanca']:
            if not cleaned_data.get('agencia'):
                self.add_error('agencia', 'Agência é obrigatória para este tipo de conta')
            if not cleaned_data.get('numero_conta'):
                self.add_error('numero_conta', 'Número da conta é obrigatório para este tipo de conta')

        # Validações específicas para cartão de crédito
        if tipo == 'cartao_credito':
            if not cleaned_data.get('limite_cartao'):
                self.add_error('limite_cartao', 'Limite do cartão é obrigatório para cartões de crédito')

        return cleaned_data


class EntradaForm(forms.ModelForm):
    class Meta:
        model = Entrada
        fields = ['nome', 'valor', 'data', 'local', 'forma_recebimento', 'conta_bancaria', 'observacao']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Descrição da entrada'
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0.01'
            }),
            'data': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'local': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Origem do recebimento'
            }),
            'forma_recebimento': forms.Select(attrs={
                'class': 'form-input'
            }),
            'conta_bancaria': forms.Select(attrs={
                'class': 'form-input'
            }),
            'observacao': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Observações adicionais'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            # Filtra apenas contas bancárias ativas do usuário
            self.fields['conta_bancaria'].queryset = ContaBancaria.objects.filter(
                proprietario=user,
                ativa=True
            )

    def clean_valor(self):
        valor = self.cleaned_data.get('valor')
        if isinstance(valor, str):
            # Converte de formato brasileiro para decimal
            valor = valor.replace('.', '').replace(',', '.')
            try:
                return Decimal(valor)
            except (InvalidOperation, ValueError):
                raise forms.ValidationError("Valor inválido")
        return valor

from django import forms
from .models import Saida
from core.choices import (
    CATEGORIA_CHOICES, 
    SUBCATEGORIA_CHOICES,
    SUBCATEGORIA_PARA_CATEGORIA
)

class SaidaForm(forms.ModelForm):
    class Meta:
        model = Saida
        # Remover 'usuario' dos fields - será definido automaticamente
        fields = ['conta_bancaria', 'nome', 'local', 'categoria', 'subcategoria', 
                 'observacao', 'valor', 'data_lancamento', 'data_vencimento', 
                 'forma_pagamento', 'tipo_pagamento_detalhe', 'recorrente', 
                 'quantidade_parcelas', 'valor_parcela', 'situacao']
        widgets = {
            'data_lancamento': forms.DateInput(attrs={'type': 'date'}),
            'data_vencimento': forms.DateInput(attrs={'type': 'date'}),
            'observacao': forms.Textarea(attrs={'rows': 3}),
            'valor': forms.TextInput(attrs={'class': 'currency-input'}),
            'valor_parcela': forms.TextInput(attrs={'class': 'currency-input', 'readonly': 'readonly'}),
            'recorrente': forms.Select(attrs={'class': 'form-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        # Extrair o parâmetro 'user' antes de chamar o super()
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Garantir que as choices sejam carregadas corretamente
        self.fields['categoria'].choices = [('', 'Selecione uma categoria')] + list(CATEGORIA_CHOICES)
        self.fields['subcategoria'].choices = [('', 'Selecione uma subcategoria')] + list(SUBCATEGORIA_CHOICES)
        
        # Tornar campos opcionais
        self.fields['subcategoria'].required = False
        self.fields['local'].required = False
        self.fields['observacao'].required = False
        
        # Filtrar contas bancárias do usuário, se disponível
        if self.user and 'conta_bancaria' in self.fields:
            from .models import ContaBancaria
            self.fields['conta_bancaria'].queryset = ContaBancaria.objects.filter(
                proprietario=self.user, ativa=True
            )
            # Adicionar placeholder
            self.fields['conta_bancaria'].empty_label = "Selecione uma conta"
    
    def clean(self):
        cleaned_data = super().clean()
        categoria = cleaned_data.get('categoria')
        subcategoria = cleaned_data.get('subcategoria')
        
        # Validar se a subcategoria pertence à categoria
        if categoria and subcategoria:
            categoria_da_subcategoria = SUBCATEGORIA_PARA_CATEGORIA.get(subcategoria)
            if categoria_da_subcategoria and categoria_da_subcategoria != categoria:
                self.add_error('subcategoria', f'A subcategoria selecionada não pertence à categoria "{dict(CATEGORIA_CHOICES).get(categoria)}"')
        
        return cleaned_data
    
def clean_valor(self):
    valor = self.cleaned_data.get("valor")
    if isinstance(valor, str):
        valor = valor.replace("R$", "").replace(".", "").replace(",", ".").strip()
        try:
            valor = Decimal(valor)
        except (InvalidOperation, ValueError):
            raise forms.ValidationError("Valor inválido.")
    return valor

    
    def save(self, commit=True):
        # Definir o usuário automaticamente antes de salvar
        saida = super().save(commit=False)
        if self.user:
            saida.usuario = self.user
        
        if commit:
            saida.save()
        
        return saida

# forms.py - Atualize o formulário
class TransferenciaForm(forms.ModelForm):
    class Meta:
        model = Transferencia
        fields = ['conta_origem', 'conta_destino', 'valor', 'data', 'observacao']
        widgets = {
            'conta_origem': forms.Select(attrs={'class': 'form-input'}),
            'conta_destino': forms.Select(attrs={'class': 'form-input'}),
            'valor': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'data': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'observacao': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }
        labels = {
            'conta_origem': 'Conta de Origem',
            'conta_destino': 'Conta de Destino',
            'valor': 'Valor',
            'data': 'Data',
            'observacao': 'Observação',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filtra as contas apenas do usuário logado
            contas = ContaBancaria.objects.filter(proprietario=user, ativa=True)
            self.fields['conta_origem'].queryset = contas
            self.fields['conta_destino'].queryset = contas
    
    def clean(self):
        cleaned_data = super().clean()
        conta_origem = cleaned_data.get('conta_origem')
        conta_destino = cleaned_data.get('conta_destino')
        valor = cleaned_data.get('valor')
        
        # Validação: Contas não podem ser iguais
        if conta_origem and conta_destino and conta_origem == conta_destino:
            raise forms.ValidationError("A conta de origem e a conta de destino não podem ser a mesma.")
        
        # Validação: Saldo suficiente na conta de origem
        if conta_origem and valor and conta_origem.saldo_atual < valor:
            raise forms.ValidationError(
                f"Saldo insuficiente na conta de origem. "
                f"Saldo atual: R$ {conta_origem.saldo_atual:.2f}"
            )
            
        return cleaned_data
    


from decimal import Decimal, InvalidOperation

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.forms import UserChangeForm

from .models import ContaBancaria, Entrada, Saida, Profile

# Seu CustomUserCreationForm
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


# forms.py - Atualize o ProfileUpdateForm

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['foto_perfil']
        widgets = {
            'foto_perfil': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'hidden',
                'id': 'id_foto_perfil'
            })
        }
    
    def clean_foto_perfil(self):
        foto = self.cleaned_data.get('foto_perfil')
        
        if foto:
            # Validar tamanho do arquivo (máximo 2MB)
            if foto.size > 2 * 1024 * 1024:
                raise forms.ValidationError('A imagem deve ter menos de 2MB.')
            
            # Validar tipo de arquivo
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            ext = os.path.splitext(foto.name)[1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError('Formatos suportados: JPG, JPEG, PNG, GIF, WEBP.')
            
            # Renomear o arquivo para forçar a sobrescrita
            # Usar o ID do usuário como nome do arquivo
            user_id = self.instance.user.id
            filename = f"user_{user_id}{ext}"
            foto.name = filename
            
            # Validar dimensões (opcional)
            try:
                from PIL import Image
                img = Image.open(foto)
                if img.width > 2000 or img.height > 2000:
                    raise forms.ValidationError('A imagem não pode ter mais de 2000px em qualquer dimensão.')
            except:
                pass
        
        return foto
    


from django import forms
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import OperacaoSaque

class OperacaoSaqueForm(forms.ModelForm):
    # Campos monetários tratados como texto (aceita R$, vírgula, ponto etc.)
    valor_saque = forms.CharField(
        max_length=20,
        required=True,
        label="Valor do Saque",
        widget=forms.TextInput(attrs={
            'class': 'form-input monetary-input',
            'placeholder': 'Ex: 10.000,00',
            'required': 'required'
        })
    )

    valor_liberado_cliente = forms.CharField(
        max_length=20,
        required=True,
        label="Valor Liberado ao Cliente",
        widget=forms.TextInput(attrs={
            'class': 'form-input monetary-input',
            'placeholder': 'Ex: 10.000,00',
            'required': 'required'
        })
    )

    valor_parcela = forms.CharField(
        max_length=20,
        required=False,
        label="Valor da Parcela",
        widget=forms.TextInput(attrs={
            'class': 'form-input monetary-input',
            'placeholder': 'Ex: 1.000,00'
        })
    )

    quantidade_parcelas = forms.IntegerField(
        required=False,
        min_value=1,
        label="Quantidade de Parcelas",
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ex: 12',
            'min': '1'
        })
    )

    class Meta:
        model = OperacaoSaque
        fields = [
            'nome_banco',
            'tipo_operacao',
            'data_contratacao',
            'valor_saque',
            'valor_liberado_cliente',
            'quantidade_parcelas',
            'valor_parcela',
            'data_inicio_parcelas',
            'data_termino_parcelas'
        ]
        widgets = {
            'nome_banco': forms.Select(attrs={'class': 'form-input', 'required': 'required'}),
            'tipo_operacao': forms.Select(attrs={'class': 'form-input', 'required': 'required'}),
            'data_contratacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-input', 'required': 'required'}),
            'data_inicio_parcelas': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'data_termino_parcelas': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        }

    # -------------------------
    # 🔹 Funções auxiliares
    # -------------------------
    def _parse_currency_value(self, value):
        """
        Converte string de valor monetário brasileiro para Decimal.
        Ex:
          "R$ 1.234,56" -> Decimal("1234.56")
          "10000" -> Decimal("10000.00")
          "10.000,50" -> Decimal("10000.50")
        """
        if not value:
            return None

        value = str(value).strip()
        # Remove símbolos, espaços e letras
        cleaned = ''.join(ch for ch in value if ch.isdigit() or ch in ',.-')

        if cleaned == '':
            return None

        # Substitui vírgula decimal e remove pontos de milhar
        if ',' in cleaned:
            cleaned = cleaned.replace('.', '').replace(',', '.')
        else:
            # se vier apenas número inteiro (ex: 15000)
            if '.' not in cleaned:
                cleaned += '.00'

        try:
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return None

    # -------------------------
    # 🔹 Validações individuais
    # -------------------------
    def clean_valor_saque(self):
        valor = self.cleaned_data.get('valor_saque')
        parsed_value = self._parse_currency_value(valor)
        if parsed_value is None:
            raise ValidationError('Por favor, insira um valor válido. Ex: 10000 ou 10.000,50')
        if parsed_value <= 0:
            raise ValidationError('O valor do saque deve ser maior que zero.')
        return parsed_value

    def clean_valor_liberado_cliente(self):
        valor = self.cleaned_data.get('valor_liberado_cliente')
        parsed_value = self._parse_currency_value(valor)
        if parsed_value is None:
            raise ValidationError('Por favor, insira um valor válido. Ex: 10000 ou 10.000,50')
        if parsed_value <= 0:
            raise ValidationError('O valor liberado deve ser maior que zero.')
        return parsed_value

    def clean_valor_parcela(self):
        valor = self.cleaned_data.get('valor_parcela')
        if not valor:
            return None
        parsed_value = self._parse_currency_value(valor)
        if parsed_value is None:
            raise ValidationError('Por favor, insira um valor válido. Ex: 1000 ou 1.000,50')
        return parsed_value

    def clean_quantidade_parcelas(self):
        quantidade = self.cleaned_data.get('quantidade_parcelas')
        if quantidade and quantidade < 1:
            raise ValidationError('A quantidade de parcelas deve ser pelo menos 1.')
        return quantidade

    def clean_data_contratacao(self):
        data = self.cleaned_data.get('data_contratacao')
        if data and data > timezone.now().date():
            raise ValidationError('A data de contratação não pode ser futura.')
        return data

    # -------------------------
    # 🔹 Validação cruzada
    # -------------------------
    def clean(self):
        cleaned_data = super().clean()

        valor_saque = cleaned_data.get('valor_saque')
        valor_liberado_cliente = cleaned_data.get('valor_liberado_cliente')
        quantidade_parcelas = cleaned_data.get('quantidade_parcelas')
        valor_parcela = cleaned_data.get('valor_parcela')

        # Valor liberado não pode ser maior que o saque
        if valor_saque and valor_liberado_cliente and valor_liberado_cliente > valor_saque:
            self.add_error('valor_liberado_cliente',
                'O valor liberado ao cliente não pode ser maior que o valor do saque.')

        # Parcelamento
        if quantidade_parcelas and not valor_parcela:
            self.add_error('valor_parcela', 'Informe o valor da parcela.')
        if valor_parcela and not quantidade_parcelas:
            self.add_error('quantidade_parcelas', 'Informe a quantidade de parcelas.')

        # Validação do total de parcelas
        if valor_saque and valor_parcela and quantidade_parcelas:
            total = valor_parcela * quantidade_parcelas
            if abs(total - valor_saque) > Decimal('0.01'):
                self.add_error('valor_parcela',
                    f'O total das parcelas (R$ {total:,.2f}) não corresponde ao valor do saque (R$ {valor_saque:,.2f}).')

        return cleaned_data

    # -------------------------
    # 🔹 Salvamento ajustado
    # -------------------------
    def save(self, commit=True):
        instance = super().save(commit=False)

        # Calcula data final automaticamente
        data_inicio = self.cleaned_data.get('data_inicio_parcelas')
        quantidade_parcelas = self.cleaned_data.get('quantidade_parcelas')
        if data_inicio and quantidade_parcelas:
            from dateutil.relativedelta import relativedelta
            instance.data_termino_parcelas = data_inicio + relativedelta(months=quantidade_parcelas)

        if commit:
            instance.save()
        return instance

class LembreteForm(forms.ModelForm):
    class Meta:
        model = Lembrete
        fields = ['titulo', 'descricao', 'data_limite', 'concluido']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-input'}),
            'descricao': forms.Textarea(attrs={'class': 'form-textarea'}),
            'data_limite': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'concluido': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }





# Adicione estes formulários ao forms.py
class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nome da categoria',
                'required': 'required'
            })
        }

class SubcategoriaForm(forms.ModelForm):
    class Meta:
        model = Subcategoria
        fields = ['nome', 'categoria']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nome da subcategoria',
                'required': 'required'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-input',
                'required': 'required'
            })
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['categoria'].queryset = Categoria.objects.filter(usuario=user)