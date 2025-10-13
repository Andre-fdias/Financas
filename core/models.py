from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from decimal import Decimal
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
import os
import re

from .choices import (
    PERIODICIDADE_CHOICES, FORMA_RECEBIMENTO_CHOICES, FORMA_PAGAMENTO_CHOICES,
    TIPO_PAGAMENTO_DETALHE_CHOICES, SITUACAO_CHOICES, TIPO_CONTA_CHOICES, 
    BANCO_CHOICES,CATEGORIA_CHOICES, SUBCATEGORIA_CHOICES, THEME_CHOICES, TIPO_OPERACAO_CHOICES
)


class BaseModel(models.Model):
    """Modelo base com campos comuns"""
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class ContaBancaria(BaseModel):
    """
    Representa uma conta bancária ou cartão associado a um usuário.
    Pode ser uma conta corrente, poupança, cartão de crédito, etc.
    """
    proprietario = models.ForeignKey(User, on_delete=models.CASCADE)
    nome_banco = models.CharField(max_length=20, choices=BANCO_CHOICES)
    nome_do_titular = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name="Nome do Titular da Conta",
        help_text="Nome do titular real da conta (ex: filho, cônjuge), se diferente do usuário gestor."
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CONTA_CHOICES, verbose_name="Tipo de Conta")
    agencia = models.CharField(max_length=10, blank=True, null=True)
    numero_conta = models.CharField(max_length=20, blank=True, null=True)
    saldo_atual = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    ativa = models.BooleanField(default=True)
    
    # Campos específicos para cartão de crédito
    numero_cartao = models.CharField(max_length=20, blank=True, null=True)
    limite_cartao = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    dia_fechamento_fatura = models.PositiveSmallIntegerField(blank=True, null=True)
    dia_vencimento_fatura = models.PositiveSmallIntegerField(blank=True, null=True)

    class Meta:
        verbose_name = 'Conta Bancária'
        verbose_name_plural = 'Contas Bancárias'
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['proprietario', 'ativa']),
            models.Index(fields=['tipo']),
        ]

    def __str__(self):
        display_name = self.get_nome_banco_display()
        if self.tipo in ['credito', 'debito', 'alimentacao']:
            return f"{display_name} - {self.numero_conta or self.numero_cartao}"
        return f"{display_name} - {self.agencia}/{self.numero_conta}"
    
    def saldo_formatado(self):
        return f"R$ {self.saldo_atual:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    def is_cartao_credito(self):
        return self.tipo == 'credito'

    def clean(self):
        super().clean()
        if self.tipo in ['corrente', 'poupanca']:
            if not self.agencia:
                raise ValidationError({'agencia': 'Agência é obrigatória para contas correntes e poupança.'})
            if not self.numero_conta:
                raise ValidationError({'numero_conta': 'Número da conta é obrigatório para contas correntes e poupança.'})
        elif self.tipo in ['credito', 'debito', 'alimentacao'] and self.agencia:
            raise ValidationError({'agencia': 'Agência não é aplicável para este tipo de conta.'})


class Categoria(BaseModel):
    """
    Representa uma categoria de transação (Entrada ou Saída) criada pelo usuário.
    Ex: Moradia, Alimentação, Salário.
    """
    nome = models.CharField(max_length=100)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    # Se for uma categoria padrão do sistema, usuario será null
    eh_padrao = models.BooleanField(default=False)
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        unique_together = ('nome', 'usuario')
        indexes = [
            models.Index(fields=['usuario', 'nome']),
        ]

    def __str__(self):
        return self.nome


class Subcategoria(BaseModel):
    """
    Representa uma subcategoria dentro de uma Categoria, criada pelo usuário.
    Ex: Aluguel (dentro de Moradia), Supermercado (dentro de Alimentação).
    """
    nome = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='subcategorias')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    eh_padrao = models.BooleanField(default=False)
    class Meta:
        verbose_name = "Subcategoria"
        verbose_name_plural = "Subcategorias"
        unique_together = ('nome', 'categoria', 'usuario')
        indexes = [
            models.Index(fields=['usuario', 'categoria']),
        ]

    def __str__(self):
        return f"{self.nome} ({self.categoria.nome})"


class Entrada(BaseModel):
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='entradas',
        verbose_name="Usuário"
    )
    conta_bancaria = models.ForeignKey(
        ContaBancaria, 
        on_delete=models.CASCADE,
        verbose_name="Conta Bancária"
    )
    nome = models.CharField(
        max_length=255,
        verbose_name="Descrição da Entrada"
    )
    valor = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Valor"
    )
    data = models.DateField(
        default=timezone.now,
        verbose_name="Data de Recebimento"
    )
    
    # Campos de detalhamento
    local = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Local/Origem"
    )
    
    # Campo de forma de recebimento
    forma_recebimento = models.CharField(
        max_length=20,
        choices=FORMA_RECEBIMENTO_CHOICES,
        default='dinheiro',
        verbose_name="Forma de Recebimento"
    )
    
    # Campo de observações
    observacao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações"
    )

    class Meta:
        verbose_name = "Entrada"
        verbose_name_plural = "Entradas"
        ordering = ['-data', '-data_criacao']
        indexes = [
            models.Index(fields=['usuario', 'data']),
            models.Index(fields=['conta_bancaria', 'data']),
        ]

    def __str__(self):
        return f"{self.nome} - R$ {self.valor} ({self.data.strftime('%d/%m/%Y')})"

    def clean(self):
        super().clean()
        # Validação de data futura
        if self.data > timezone.now().date():
            raise ValidationError({
                'data': 'Não é possível registrar uma entrada com data futura.'
            })

    @property
    def valor_formatado(self):
        return f"R$ {self.valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    @property
    def banco_origem(self):
        return self.conta_bancaria.get_nome_banco_display()


class Saida(BaseModel):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    conta_bancaria = models.ForeignKey(ContaBancaria, on_delete=models.CASCADE)
    nome = models.CharField(max_length=255, verbose_name="Nome da Transação")
    valor = models.DecimalField(max_digits=15, decimal_places=2)
    data_lancamento = models.DateField(default=timezone.now, verbose_name="Data de Lançamento")
    data_vencimento = models.DateField(verbose_name="Data de Vencimento")
    local = models.CharField(max_length=100, blank=True, null=True, verbose_name="Local")
    
    # Categorias
    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIA_CHOICES,
        null=True,
        blank=True,
        verbose_name="Categoria"
    )
    
    subcategoria = models.CharField(
        max_length=30,
        choices=SUBCATEGORIA_CHOICES,
        null=True,
        blank=True,
        verbose_name="Subcategoria"
    )
    
    # Forma de pagamento
    forma_pagamento = models.CharField(
        max_length=20,
        choices=FORMA_PAGAMENTO_CHOICES,
        default='dinheiro'
    )
    
    # Detalhes do tipo de pagamento
    tipo_pagamento_detalhe = models.CharField(
        max_length=10,
        choices=TIPO_PAGAMENTO_DETALHE_CHOICES,
        default='avista'
    )
    
    # Situação
    situacao = models.CharField(
        max_length=10,
        choices=SITUACAO_CHOICES,
        default='pendente'
    )
    
    # Campos para parcelamento
    quantidade_parcelas = models.IntegerField(default=1)
    parcela_atual = models.PositiveIntegerField(default=1)
    valor_parcela = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Valor da Parcela"
    )
    
    # Campos para recorrência
    recorrente = models.CharField(
        max_length=10,
        choices=PERIODICIDADE_CHOICES,
        default='unica'
    )
    
    # Relacionamentos para controle de parcelas e recorrência
    despesa_original = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='parcelas_futuras'
    )
    
    # Novo campo para controle de recorrência
    recorrencia_original = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='ocorrencias_futuras'
    )
    
    # Flags para identificar o tipo de registro
    e_parcela = models.BooleanField(default=False)
    e_recorrente = models.BooleanField(default=False)
    
    observacao = models.TextField(blank=True, null=True)

    class Meta: 
        ordering = ['-data_lancamento']
        verbose_name = "Saída"
        verbose_name_plural = "Saídas"
        indexes = [
            models.Index(fields=['usuario', 'data_lancamento']),
            models.Index(fields=['data_vencimento']),
            models.Index(fields=['situacao']),
            models.Index(fields=['e_parcela']),
            models.Index(fields=['e_recorrente']),
        ]

    def __str__(self):
        return f"{self.nome} - R$ {self.valor}"
    
    def save(self, *args, **kwargs):
        # Se for parcelado e quantidade_parcelas > 1, calcular valor da parcela
        if (self.tipo_pagamento_detalhe == 'parcelado' and 
            self.quantidade_parcelas > 1 and 
            self.valor > 0):
            
            # Calcular valor da parcela
            self.valor_parcela = self.valor / self.quantidade_parcelas
            
            # Se esta é a PRIMEIRA parcela (original), ajustar seu próprio valor
            if not self.e_parcela or self.parcela_atual == 1:
                # A primeira parcela também deve ter o valor da parcela, não o total
                self.valor = self.valor_parcela
        
        # Se for à vista, garantir que quantidade_parcelas seja 1
        if self.tipo_pagamento_detalhe == 'avista':
            self.quantidade_parcelas = 1
            self.parcela_atual = 1
            self.valor_parcela = self.valor
        
        super().save(*args, **kwargs)

    @property
    def valor_total(self):
        """
        Retorna o valor total da despesa (valor da parcela * quantidade de parcelas)
        """
        if self.tipo_pagamento_detalhe == 'parcelado' and self.quantidade_parcelas > 1:
            return self.valor_parcela * self.quantidade_parcelas
        return self.valor

    @property
    def tem_parcelas_futuras(self):
        """Verifica se existem parcelas futuras relacionadas"""
        return self.parcelas_futuras.filter(situacao='pendente').exists()
    
    @property
    def tem_ocorrencias_futuras(self):
        """Verifica se existem ocorrências futuras relacionadas"""
        return self.ocorrencias_futuras.filter(situacao='pendente').exists()
    
    @property
    def total_parcelas(self):
        """Retorna o total de parcelas (incluindo a atual)"""
        if self.e_parcela:
            return self.despesa_original.quantidade_parcelas
        return self.quantidade_parcelas
    
    @property
    def descricao_completa(self):
        """Retorna descrição completa com informações de parcelamento/recorrência"""
        descricao = self.nome
        
        if self.e_parcela:
            descricao += f" (Parcela {self.parcela_atual}/{self.total_parcelas})"
        elif self.quantidade_parcelas > 1:
            descricao += f" ({self.parcela_atual}/{self.quantidade_parcelas})"
        
        if self.e_recorrente:
            descricao += f" [Recorrente - {self.get_recorrente_display()}]"
        elif self.recorrente != 'unica':
            descricao += f" [Orig. Recorrente - {self.get_recorrente_display()}]"
        
        return descricao


class Profile(BaseModel):

    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    foto_perfil = models.ImageField(
        default='default.jpg',
        upload_to='profile_pics',
        verbose_name="Foto de Perfil"
    )
    theme = models.CharField(
        max_length=10, 
        choices=THEME_CHOICES, 
        default='light',
        verbose_name="Tema preferido"
    )
    password_updated_at = models.DateTimeField(null=True, blank=True)
    last_login_date = models.DateField(null=True, blank=True)
    login_streak = models.IntegerField(default=0)
    total_logins = models.IntegerField(default=0)

    def __str__(self):
        return f'Perfil de {self.user.username}'

    def save(self, *args, **kwargs):
        # Se está atualizando a foto e já existe uma foto anterior que não é a padrão
        if self.pk and self.foto_perfil and self.foto_perfil.name != 'default.jpg':
            try:
                old_profile = Profile.objects.get(pk=self.pk)
                if (old_profile.foto_perfil and 
                    old_profile.foto_perfil.name != 'default.jpg' and 
                    old_profile.foto_perfil.name != self.foto_perfil.name):
                    old_profile.foto_perfil.delete(save=False)
            except Profile.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Redimensionar imagem se existir e não for a padrão
        if self.foto_perfil and self.foto_perfil.name != 'default.jpg':
            try:
                img_path = self.foto_perfil.path
                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    
                    # Redimensionar se for muito grande
                    if img.height > 300 or img.width > 300:
                        output_size = (300, 300)
                        img.thumbnail(output_size)
                        img.save(img_path)
            except Exception as e:
                print(f"Erro ao processar imagem: {e}")

    def update_login_streak(self):
        today = timezone.now().date()
        
        if self.last_login_date:
            days_since_last_login = (today - self.last_login_date).days
            
            if days_since_last_login == 1:
                self.login_streak += 1
            elif days_since_last_login > 1:
                self.login_streak = 1
        else:
            self.login_streak = 1
        
        self.last_login_date = today
        self.total_logins += 1
        self.save()

    def update_password_timestamp(self):
        self.password_updated_at = timezone.now()
        self.save()

    def get_password_strength(self):
        """Lógica simplificada para avaliar força da senha"""
        # Implemente sua lógica aqui ou remova se não for usada
        return "Forte"

    
        
    def get_profile_completion(self):
        """Calcular percentual de completude do perfil"""
        try:
            user = self.user
            completed_fields = 0
            total_fields = 4
            
            if user.first_name and user.first_name.strip(): 
                completed_fields += 1
            if user.last_name and user.last_name.strip(): 
                completed_fields += 1
            if user.email and user.email.strip(): 
                completed_fields += 1
            if self.foto_perfil and self.foto_perfil.name != 'default.jpg': 
                completed_fields += 1
            
            return int((completed_fields / total_fields) * 100)
        except Exception as e:
            return 0  # Retorna 0 em caso de erro
    


    def get_activity_display(self):
        """Retorna o nome amigável para o tipo de atividade"""
        activity_names = {
            'login': 'Login realizado',
            'password_change': 'Senha alterada',
            'profile_update': 'Perfil atualizado',
            'photo_change': 'Foto alterada',
        }
        return activity_names.get(self.activity_type, 'Atividade desconhecida')

    def get_description(self):
        """Retorna descrição detalhada da atividade"""
        descriptions = {
            'login': 'Acesso ao sistema',
            'password_change': 'Alteração de segurança',
            'profile_update': 'Informações pessoais',
            'photo_change': 'Foto de perfil',
        }
        return descriptions.get(self.activity_type, 'Atividade do usuário')


class UserActivity(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=50)
    details = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Atividade do Usuário'
        verbose_name_plural = 'Atividades dos Usuários'
        indexes = [
            models.Index(fields=['user', 'data_criacao']),
        ]


class UserLogin(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Login do Usuário'
        verbose_name_plural = 'Logins dos Usuários'
        indexes = [
            models.Index(fields=['user', 'data_criacao']),
        ]


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()

# models.py - Atualize o modelo Transferencia
class Transferencia(BaseModel):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transferencias')
    conta_origem = models.ForeignKey(ContaBancaria, related_name='transferencias_origem', on_delete=models.CASCADE)
    conta_destino = models.ForeignKey(ContaBancaria, related_name='transferencias_destino', on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField(default=timezone.now)
    observacao = models.TextField(blank=True, null=True)
    # Removemos as relações com Saida e Entrada

    class Meta:
        ordering = ['-data', '-data_criacao']
        verbose_name = 'Transferência'
        verbose_name_plural = 'Transferências'
        indexes = [
            models.Index(fields=['usuario', 'data']),
        ]

    def __str__(self):
        return f"Transferência de R$ {self.valor} de {self.conta_origem} para {self.conta_destino}"

    def clean(self):
        super().clean()
        
        # Validação: Contas não podem ser iguais
        if self.conta_origem == self.conta_destino:
            raise ValidationError("A conta de origem e a conta de destino não podem ser a mesma.")
        
        # Validação: Saldo suficiente na conta de origem
        if self.conta_origem.saldo_atual < self.valor:
            raise ValidationError(
                f"Saldo insuficiente na conta de origem. "
                f"Saldo atual: R$ {self.conta_origem.saldo_atual:.2f}"
            )
        
        # Validação: Data não pode ser futura
        if self.data > timezone.now().date():
            raise ValidationError("Não é possível registrar transferência com data futura.")

    def save(self, *args, **kwargs):
        # Se é uma nova transferência (não está sendo editada)
        if not self.pk:
            # Atualiza os saldos das contas
            self.conta_origem.saldo_atual -= self.valor
            self.conta_destino.saldo_atual += self.valor
            
            self.conta_origem.save()
            self.conta_destino.save()
        
        super().save(*args, **kwargs)


# models.py
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class OperacaoSaque(models.Model):
 
    proprietario = models.ForeignKey(User, on_delete=models.CASCADE)
    nome_banco = models.CharField(max_length=100, choices=BANCO_CHOICES)  # Agora usa choices
    tipo_operacao = models.CharField(max_length=28, choices=TIPO_OPERACAO_CHOICES)
    data_contratacao = models.DateField()
    valor_saque = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    valor_financiado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    valor_iof = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    valor_liberado_cliente = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    
    # NOVOS CAMPOS
    quantidade_parcelas = models.PositiveIntegerField(null=True, blank=True, verbose_name="Quantidade de Parcelas")
    valor_parcela = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Valor da Parcela"
    )
    data_inicio_parcelas = models.DateField(null=True, blank=True, verbose_name="Início das Parcelas")
    data_termino_parcelas = models.DateField(null=True, blank=True, verbose_name="Término das Parcelas")
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-data_contratacao']
        verbose_name = 'Operação de Saque'
        verbose_name_plural = 'Operações de Saque'
    
    def __str__(self):
        return f"{self.get_nome_banco_display()} - {self.get_tipo_operacao_display()} - {self.valor_saque}"
    
    def save(self, *args, **kwargs):
        # Garante que valor_liberado_cliente não seja maior que valor_saque
        if self.valor_liberado_cliente and self.valor_saque:
            if self.valor_liberado_cliente > self.valor_saque:
                self.valor_liberado_cliente = self.valor_saque
        
        # Calcula automaticamente o término das parcelas se houver início e quantidade
        if self.data_inicio_parcelas and self.quantidade_parcelas:
            from dateutil.relativedelta import relativedelta
            self.data_termino_parcelas = self.data_inicio_parcelas + relativedelta(months=self.quantidade_parcelas)
        
        super().save(*args, **kwargs)




class Lembrete(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    data_limite = models.DateField()
    concluido = models.BooleanField(default=False)

    class Meta:
        ordering = ['data_limite']
        verbose_name = 'Lembrete'
        verbose_name_plural = 'Lembretes'
        indexes = [
            models.Index(fields=['user', 'data_limite']),
        ]

    @property
    def dias_para_vencer(self):
        if self.concluido:
            return 0
        hoje = timezone.now().date()
        return (self.data_limite - hoje).days
    

# core/models.py - Adicione estas classes
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

class RegistroTentativa(models.Model):
    email = models.EmailField(db_index=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    sucesso = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'registro_tentativas'
        indexes = [
            models.Index(fields=['email', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.email} - {self.timestamp}"

class BloqueioCadastro(models.Model):
    email = models.EmailField(db_index=True)
    ip_address = models.GenericIPAddressField(db_index=True)
    motivo = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    expira_em = models.DateTimeField()
    tentativas = models.IntegerField(default=1)
    
    class Meta:
        db_table = 'bloqueio_cadastro'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['ip_address']),
        ]
    
    @property
    def esta_bloqueado(self):
        return timezone.now() < self.expira_em
    
    @classmethod
    def bloquear(cls, email, ip_address, motivo, horas=24):
        # Verifica se já existe um bloqueio
        bloqueio_existente = cls.objects.filter(
            email=email, 
            ip_address=ip_address
        ).first()
        
        if bloqueio_existente:
            # Atualiza bloqueio existente
            bloqueio_existente.tentativas += 1
            bloqueio_existente.expira_em = timezone.now() + timedelta(hours=horas)
            bloqueio_existente.motivo = motivo
            bloqueio_existente.save()
            return bloqueio_existente
        else:
            # Cria novo bloqueio
            return cls.objects.create(
                email=email,
                ip_address=ip_address,
                motivo=motivo,
                expira_em=timezone.now() + timedelta(hours=horas)
            )
    
    def __str__(self):
        return f"{self.email} - {self.motivo}"
