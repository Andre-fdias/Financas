from decimal import Decimal, InvalidOperation
import os
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import (
    ContaBancaria, Entrada, Saida, Transferencia, 
    Profile, Lembrete, OperacaoSaque
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


class SaidaForm(forms.ModelForm):
    class Meta:
        model = Saida
        fields = [
            'nome', 'valor', 'valor_parcela', 'data_lancamento', 'data_vencimento', 'local',
            'categoria', 'subcategoria', 'forma_pagamento', 'tipo_pagamento_detalhe',
            'situacao', 'quantidade_parcelas', 'recorrente', 'observacao', 'conta_bancaria'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nome da transação'}),
            'valor': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0.01'}),
            'valor_parcela': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'readonly': 'readonly'}),
            'data_lancamento': forms.DateInput(attrs={'type': 'date', 'class': 'form-input', 'max': timezone.now().date().isoformat()}),
            'data_vencimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-input', 'min': timezone.now().date().isoformat()}),
            'local': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Local'}),
            'categoria': forms.Select(attrs={'class': 'form-input'}),
            'subcategoria': forms.Select(attrs={'class': 'form-input'}),
            'forma_pagamento': forms.Select(attrs={'class': 'form-input'}),
            'tipo_pagamento_detalhe': forms.Select(attrs={'class': 'form-input'}),
            'situacao': forms.Select(attrs={'class': 'form-input'}),
            'quantidade_parcelas': forms.NumberInput(attrs={'class': 'form-input', 'min': '1'}),
            'recorrente': forms.Select(attrs={'class': 'form-input'}),
            'observacao': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Observações adicionais'}),
            'conta_bancaria': forms.Select(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['conta_bancaria'].queryset = ContaBancaria.objects.filter(proprietario=user, ativa=True)
        # Opcional: se usar categorias/subcategorias do usuário, pode filtrar assim:
        # self.fields['categoria'].queryset = Categoria.objects.filter(usuario=user)
        # self.fields['subcategoria'].queryset = Subcategoria.objects.filter(usuario=user)

    def clean(self):
        cleaned_data = super().clean()
        data_lancamento = cleaned_data.get('data_lancamento')
        situacao = cleaned_data.get('situacao')
        tipo_pagamento = cleaned_data.get('tipo_pagamento_detalhe')

        # Segurança: converte datetime para date
        if data_lancamento and hasattr(data_lancamento, 'date'):
            data_lancamento = data_lancamento.date()

        # Validação de data de lançamento
        if data_lancamento and data_lancamento > timezone.now().date():
            raise ValidationError({'data_lancamento': 'Data de lançamento não pode ser futura.'})

        # Se for à vista e pago, data de vencimento deve ser igual a data de lançamento
        if tipo_pagamento == 'avista' and situacao == 'pago':
            cleaned_data['data_vencimento'] = data_lancamento

        return cleaned_data



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
    




# forms.py
from django import forms
from decimal import Decimal, InvalidOperation
from .models import OperacaoSaque
from .choices import INSTITUICOES_FINANCEIRAS, TIPO_OPERACAO_CHOICES  # Importe as choices

class OperacaoSaqueForm(forms.ModelForm):
    class Meta:
        model = OperacaoSaque
        fields = [
            'nome_banco', 'tipo_operacao', 'data_contratacao', 
            'valor_saque', 'valor_financiado', 'valor_iof', 'valor_liberado_cliente',
            'quantidade_parcelas', 'valor_parcela', 'data_inicio_parcelas', 'data_termino_parcelas'
        ]
        widgets = {
            'data_contratacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'data_inicio_parcelas': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'data_termino_parcelas': forms.DateInput(attrs={'type': 'date', 'class': 'form-input', 'readonly': 'readonly'}),
            'nome_banco': forms.Select(choices=INSTITUICOES_FINANCEIRAS, attrs={'class': 'form-input'}),
            'tipo_operacao': forms.Select(choices=TIPO_OPERACAO_CHOICES, attrs={'class': 'form-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classes CSS aos campos
        for field_name, field in self.fields.items():
            if field_name not in ['data_contratacao', 'data_inicio_parcelas', 'data_termino_parcelas', 'nome_banco']:
                field.widget.attrs['class'] = 'form-input'
        
        # Configurar placeholder para campos monetários
        monetary_fields = ['valor_saque', 'valor_financiado', 'valor_iof', 'valor_liberado_cliente', 'valor_parcela']
        for field in monetary_fields:
            self.fields[field].widget.attrs['placeholder'] = '0,00'
    
    def clean_decimal_field(self, value, field_name):
        """Método auxiliar para limpar campos decimais"""
        if not value:
            return None
            
        try:
            # Remove R$, pontos e converte vírgula para ponto
            value_str = str(value).replace('R$', '').replace('.', '').replace(',', '.').strip()
            return Decimal(value_str)
        except (InvalidOperation, ValueError):
            raise forms.ValidationError(f'Por favor, insira um valor válido para {field_name}')
    
    def clean_valor_saque(self):
        return self.clean_decimal_field(self.cleaned_data.get('valor_saque'), 'valor do saque')
    
    def clean_valor_financiado(self):
        return self.clean_decimal_field(self.cleaned_data.get('valor_financiado'), 'valor financiado')
    
    def clean_valor_iof(self):
        return self.clean_decimal_field(self.cleaned_data.get('valor_iof'), 'IOF')
    
    def clean_valor_liberado_cliente(self):
        return self.clean_decimal_field(self.cleaned_data.get('valor_liberado_cliente'), 'valor liberado')
    
    def clean_valor_parcela(self):
        return self.clean_decimal_field(self.cleaned_data.get('valor_parcela'), 'valor da parcela')
    
    def clean(self):
        cleaned_data = super().clean()
        valor_saque = cleaned_data.get('valor_saque')
        valor_liberado = cleaned_data.get('valor_liberado_cliente')
        quantidade_parcelas = cleaned_data.get('quantidade_parcelas')
        valor_parcela = cleaned_data.get('valor_parcela')
        data_inicio = cleaned_data.get('data_inicio_parcelas')
        data_termino = cleaned_data.get('data_termino_parcelas')
        
        # Validação: valor liberado não pode ser maior que valor do saque
        if valor_saque and valor_liberado and valor_liberado > valor_saque:
            raise forms.ValidationError(
                'O valor liberado não pode ser maior que o valor do saque.'
            )
        
        # Validação: se tem quantidade de parcelas, deve ter valor da parcela
        if quantidade_parcelas and not valor_parcela:
            raise forms.ValidationError(
                'Se informar a quantidade de parcelas, deve informar o valor da parcela.'
            )
        
        # Validação: se tem valor da parcela, deve ter quantidade de parcelas
        if valor_parcela and not quantidade_parcelas:
            raise forms.ValidationError(
                'Se informar o valor da parcela, deve informar a quantidade de parcelas.'
            )
        
        # Validação: datas consistentes
        if data_inicio and data_termino and data_termino < data_inicio:
            raise forms.ValidationError(
                'A data de término das parcelas não pode ser anterior à data de início.'
            )
        
        return cleaned_data
    

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