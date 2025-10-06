from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum
from datetime import datetime, timedelta

from .models import (
    ContaBancaria, Entrada, Saida, Transferencia, 
    Profile, Lembrete, OperacaoSaque, Categoria, Subcategoria,
    UserActivity, UserLogin
)

# -----------------------------------------------------------------------------
# Configurações de Inlines
# -----------------------------------------------------------------------------

class ContaBancariaInline(admin.TabularInline):
    model = ContaBancaria
    extra = 1
    fields = ('nome_banco', 'tipo', 'saldo_atual', 'ativa')
    readonly_fields = ('saldo_atual',)
    can_delete = True

# -----------------------------------------------------------------------------
# Classes de Administração Personalizadas
# -----------------------------------------------------------------------------

class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name', 
        'is_active', 'total_contas', 'total_saldo_contas', 'date_joined'
    )
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    readonly_fields = ('date_joined', 'last_login')
    actions = ['ativar_usuarios', 'desativar_usuarios']
    
    inlines = [ContaBancariaInline]

    def total_contas(self, obj):
        return obj.contabancaria_set.count()
    total_contas.short_description = 'Total de Contas'

    def total_saldo_contas(self, obj):
        saldo_total = obj.contabancaria_set.aggregate(Sum('saldo_atual'))['saldo_atual__sum']
        return format_html(f'<b>R$ {saldo_total:,.2f}</b>') if saldo_total else 'R$ 0,00'
    total_saldo_contas.short_description = 'Saldo Total'

    @admin.action(description="Ativar usuários selecionados")
    def ativar_usuarios(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} usuários ativados com sucesso.')

    @admin.action(description="Desativar usuários selecionados")
    def desativar_usuarios(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} usuários desativados com sucesso.')

# Removendo o registro padrão para usar o CustomUserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(ContaBancaria)
class ContaBancariaAdmin(admin.ModelAdmin):
    list_display = ('proprietario', 'nome_banco', 'tipo', 'saldo_atual', 'ativa', 'data_criacao')
    list_filter = ('nome_banco', 'tipo', 'ativa', 'proprietario__username')
    search_fields = ('proprietario__username', 'nome_banco', 'nome_do_titular')
    date_hierarchy = 'data_criacao'
    readonly_fields = ('saldo_atual', 'data_criacao', 'data_atualizacao')
    fieldsets = (
        (None, {
            'fields': ('proprietario', 'nome_banco', 'nome_do_titular', 'tipo', 'ativa')
        }),
        ('Detalhes da Conta', {
            'fields': ('agencia', 'numero_conta', 'saldo_inicial', 'saldo_atual')
        }),
        ('Informações do Cartão de Crédito', {
            'fields': ('numero_cartao', 'limite_cartao', 'dia_fechamento_fatura', 'dia_vencimento_fatura'),
            'classes': ('collapse',)
        }),
    )
    raw_id_fields = ('proprietario',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(proprietario=request.user)
        return queryset

@admin.register(Entrada)
class EntradaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'valor', 'nome', 'data', 'conta_bancaria', 'forma_recebimento', 'data_criacao')
    list_filter = ('forma_recebimento', 'data', 'conta_bancaria')
    search_fields = ('usuario__username', 'nome', 'conta_bancaria__nome_banco')
    date_hierarchy = 'data'
    readonly_fields = ('data_criacao', 'data_atualizacao')
    raw_id_fields = ('usuario', 'conta_bancaria')

    fieldsets = (
        (None, {
            'fields': ('usuario', 'valor', 'nome')
        }),
        ('Detalhes da Entrada', {
            'fields': ('data', 'conta_bancaria', 'forma_recebimento', 'local')
        }),
        ('Informações Adicionais', {
            'fields': ('observacao',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(usuario=request.user)
        return queryset

@admin.register(Saida)
class SaidaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'valor', 'nome', 'data_vencimento', 'conta_bancaria', 'situacao', 'data_criacao')
    list_filter = ('situacao', 'data_vencimento', 'conta_bancaria', 'forma_pagamento')
    search_fields = ('usuario__username', 'nome', 'conta_bancaria__nome_banco')
    date_hierarchy = 'data_vencimento'
    readonly_fields = ('data_criacao', 'data_atualizacao')
    raw_id_fields = ('usuario', 'conta_bancaria')
    list_editable = ('situacao',)
    
    fieldsets = (
        (None, {
            'fields': ('usuario', 'valor', 'nome')
        }),
        ('Detalhes da Saída', {
            'fields': ('data_lancamento', 'data_vencimento', 'conta_bancaria', 'situacao', 'forma_pagamento')
        }),
        ('Categorização', {
            'fields': ('categoria', 'subcategoria', 'local')
        }),
        ('Parcelamento', {
            'fields': ('quantidade_parcelas', 'valor_parcela', 'tipo_pagamento_detalhe', 'recorrente'),
            'classes': ('collapse',)
        }),
        ('Observações', {
            'fields': ('observacao',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(usuario=request.user)
        return queryset

@admin.register(Transferencia)
class TransferenciaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'valor', 'conta_origem', 'conta_destino', 'data', 'data_criacao')
    list_filter = ('data',)
    search_fields = ('usuario__username', 'conta_origem__nome_banco', 'conta_destino__nome_banco')
    date_hierarchy = 'data'
    readonly_fields = ('data_criacao', 'data_atualizacao')
    raw_id_fields = ('usuario', 'conta_origem', 'conta_destino')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(usuario=request.user)
        return queryset

@admin.register(Lembrete)
class LembreteAdmin(admin.ModelAdmin):
    list_display = ('user', 'titulo', 'data_limite', 'concluido', 'data_criacao')
    list_filter = ('concluido', 'data_limite')
    search_fields = ('user__username', 'titulo')
    list_editable = ('concluido',)
    date_hierarchy = 'data_limite'
    readonly_fields = ('data_criacao', 'data_atualizacao')
    raw_id_fields = ('user',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(user=request.user)
        return queryset

@admin.register(OperacaoSaque)
class OperacaoSaqueAdmin(admin.ModelAdmin):
    list_display = ('proprietario', 'nome_banco', 'tipo_operacao', 'valor_saque', 'data_contratacao', 'quantidade_parcelas', 'valor_liberado_cliente')
    list_filter = ('nome_banco', 'tipo_operacao', 'data_contratacao')
    search_fields = ('proprietario__username', 'nome_banco')
    date_hierarchy = 'data_contratacao'
    readonly_fields = ('data_criacao', 'data_atualizacao')
    raw_id_fields = ('proprietario',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(proprietario=request.user)
        return queryset

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'usuario', 'data_criacao')
    list_filter = ('usuario',)
    search_fields = ('nome', 'usuario__username')
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(usuario=request.user)
        return queryset

@admin.register(Subcategoria)
class SubcategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'usuario', 'data_criacao')
    list_filter = ('categoria', 'usuario')
    search_fields = ('nome', 'categoria__nome', 'usuario__username')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(usuario=request.user)
        return queryset

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'data_criacao')
    list_filter = ('theme',)
    search_fields = ('user__username',)
    readonly_fields = ('data_criacao', 'data_atualizacao')
    raw_id_fields = ('user',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(user=request.user)
        return queryset

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'data_criacao')
    list_filter = ('activity_type', 'data_criacao')
    search_fields = ('user__username', 'activity_type')
    readonly_fields = ('data_criacao', 'data_atualizacao', 'user', 'activity_type', 'details')
    date_hierarchy = 'data_criacao'
    raw_id_fields = ('user',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(user=request.user)
        return queryset

@admin.register(UserLogin)
class UserLoginAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'data_criacao')
    list_filter = ('data_criacao',)
    search_fields = ('user__username', 'ip_address')
    readonly_fields = ('user', 'ip_address', 'user_agent', 'data_criacao', 'data_atualizacao')
    date_hierarchy = 'data_criacao'
    raw_id_fields = ('user',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(user=request.user)
        return queryset