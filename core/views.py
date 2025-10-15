from django.shortcuts import render, redirect, get_object_or_404

from .forms import CustomUserCreationForm, ProfileUpdateForm,LembreteForm

from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ContaBancaria, Entrada, Saida, Transferencia, Lembrete, OperacaoSaque
from .forms import ContaBancariaForm, EntradaForm, SaidaForm, TransferenciaForm, OperacaoSaqueForm
from django.db.models import Sum
from datetime import date, timedelta, datetime,timezone # Mantém datetime para outras partes do código
from django.utils import timezone as dj_timezone # Alias para evitar conflito com datetime.timezone
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db import transaction
from decimal import Decimal, InvalidOperation
import json # Já estava importado, mas é bom garantir
from django.views.decorators.http import require_GET, require_POST
from django.db.models import Q # Importante para combinar querysets
from dateutil.relativedelta import relativedelta
import numpy as np
from sklearn.linear_model import LinearRegression
from .choices import CATEGORIA_CHOICES, SUBCATEGORIA_CHOICES, SUBCATEGORIA_PARA_CATEGORIA
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import datetime
from .models import Entrada, ContaBancaria, Categoria, Subcategoria
from .choices import FORMA_RECEBIMENTO_CHOICES,  BANCO_CHOICES, FORMA_PAGAMENTO_CHOICES, FORMA_RECEBIMENTO_CHOICES, TIPO_PAGAMENTO_DETALHE_CHOICES, SITUACAO_CHOICES, TIPO_OPERACAO_CHOICES
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from decimal import Decimal
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from .models import Entrada, Saida, ContaBancaria
from decimal import Decimal
import numpy as np
from sklearn.linear_model import LinearRegression
import json


# Funções auxiliares (se já existirem, apenas mantenha)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import  Entrada, Saida, BANCO_CHOICES, ContaBancaria# Importe ContaBancaria novamente para acessar choices de tipo
from django.db.models import Sum
from datetime import date, timedelta
from django.http import JsonResponse
import json # Importe para serializar dados para JavaScript

# Adicione esta importação para trabalhar com datas de forma mais robusta
from dateutil.relativedelta import relativedelta
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect


from django.contrib.auth.decorators import login_required
from django.views import View
from .models import CATEGORIA_CHOICES, SUBCATEGORIA_CHOICES, PERIODICIDADE_CHOICES,TIPO_CONTA_CHOICES
from .forms import TransferenciaForm
from datetime import datetime







#  ================================================================
# FUNÇÕES AUXILIARES
# ================================================================


import json
import numpy as np
from sklearn.linear_model import LinearRegression
from dateutil.relativedelta import relativedelta
from datetime import timedelta, datetime, date
from django.utils import timezone as dj_timezone
from decimal import Decimal
from django.db.models import Sum, Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator


def get_sum(queryset):
    """Retorna a soma de 'valor' de um queryset como Decimal, ou 0.00 se vazio."""
    result = queryset.aggregate(total=Sum('valor'))['total']
    return Decimal(str(result)) if result is not None else Decimal('0.00')


def serialize_for_json(obj):
    """
    Função para converter Decimals, Dates e objetos Django para tipos serializáveis em JSON
    """
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if hasattr(obj, '__iter__') and not isinstance(obj, (str, dict, list)):
        return list(obj)
    if isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize_for_json(elem) for elem in obj]
    return obj

def calculate_percentage_change(current, previous):
    """Calcula a variação percentual entre dois valores."""
    if previous == 0:
        return 0 if current == 0 else (100.0 if current > 0 else -100.0)
    change = ((current - previous) / previous) * 100
    return round(change, 2)

def get_month_range(date_obj):
    """Retorna o primeiro e último dia do mês de uma data"""
    primeiro_dia = date_obj.replace(day=1)
    ultimo_dia = (primeiro_dia + relativedelta(months=1)) - timedelta(days=1)
    return primeiro_dia, ultimo_dia

def converter_moeda_para_decimal(valor_str):
    """Converte string de moeda brasileira para Decimal"""
    if not valor_str:
        return None
    try:
        # Remove R$, pontos e converte vírgula para ponto
        valor_limpo = valor_str.replace('R$', '').replace('.', '').replace(',', '.').strip()
        return Decimal(valor_limpo)
    except:
        return None

# ================================================================
# VIEWS DA APLICAÇÃO
# ================================================================

@login_required
def home(request):
    user = request.user
    hoje = dj_timezone.now().date()

    # Calcular estatísticas para os cards
    contas_ativas = ContaBancaria.objects.filter(proprietario=user, ativa=True).count()
    saldo_total = ContaBancaria.objects.filter(proprietario=user, ativa=True).aggregate(total=Sum('saldo_atual'))['total'] or Decimal('0.00')
    lembretes_pendentes = Lembrete.objects.filter(user=user, concluido=False, data_limite__gte=hoje).count()
    
    entradas_hoje = Entrada.objects.filter(usuario=user, data=hoje).count()
    saidas_hoje = Saida.objects.filter(usuario=user, data_lancamento=hoje).count()
    transacoes_hoje = entradas_hoje + saidas_hoje

    context = {
        'contas_ativas': contas_ativas,
        'saldo_total': saldo_total,
        'lembretes_pendentes': lembretes_pendentes,
        'transacoes_hoje': transacoes_hoje,
    }
    return render(request, 'core/home.html', context)

# core/views.py - Atualize a view register
from django.contrib.auth.models import User
import time
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm

def register(request):
    # Sistema de proteção simplificado - sem importação do security.py por enquanto
    if request.method == 'POST':
        # Pequeno delay para dificultar ataques automatizados
        time.sleep(0.5)
        
        form = CustomUserCreationForm(request.POST)
        email = request.POST.get('email', '').lower().strip()
        
        # Verifica se o email já está cadastrado
        if User.objects.filter(email=email).exists():
            messages.error(
                request,
                '❌ Este email já está cadastrado. Use outro email ou recupere sua senha.',
                extra_tags='error'
            )
            return render(request, 'core/register.html', {'form': form})
        
        # Verificação básica de segurança (sem sistema complexo por enquanto)
        if form.is_valid():
            try:
                # Verificação dupla se o email ainda não existe
                if User.objects.filter(email=email).exists():
                    messages.error(
                        request,
                        '❌ Este email já está cadastrado. Tente outro.',
                        extra_tags='error'
                    )
                    return render(request, 'core/register.html', {'form': form})
                
                # Cria o usuário
                user = form.save()
                username = form.cleaned_data.get('username')
                
                messages.success(
                    request, 
                    f'✅ Conta criada com sucesso para {username}! Faça login para continuar.',
                    extra_tags='success'
                )
                
                return redirect('core:login')
                
            except Exception as e:
                messages.error(
                    request,
                    '❌ Erro interno ao criar conta. Tente novamente.',
                    extra_tags='error'
                )
        else:
            # Mensagens de erro específicas
            if 'username' in form.errors:
                for error in form.errors['username']:
                    messages.error(request, f'❌ Usuário: {error}', extra_tags='error')
            if 'email' in form.errors:
                for error in form.errors['email']:
                    messages.error(request, f'❌ Email: {error}', extra_tags='error')
            if 'password2' in form.errors:
                for error in form.errors['password2']:
                    messages.error(request, f'❌ Senha: {error}', extra_tags='error')
            
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'core/register.html', {'form': form})



def custom_logout(request):
    """View personalizada para logout com mensagem"""
    logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('core:login')


# ================================================================
# VIEW DASHBOARD
# ================================================================

@login_required
def dashboard(request):
    user = request.user
    print(f"=== DEBUG DASHBOARD ===")
    print(f"Usuário logado: {user.username}")
    print(f"Entradas totais: {Entrada.objects.filter(usuario=user).count()}")
    print(f"Saídas totais: {Saida.objects.filter(usuario=user).count()}")
    print(f"Contas: {ContaBancaria.objects.filter(proprietario=user).count()}")
    
    # Testar consultas básicas
    entradas_test = Entrada.objects.filter(usuario=user)
    saidas_test = Saida.objects.filter(usuario=user)
    
    print(f"Primeira entrada: {entradas_test.first()}")
    print(f"Primeira saída: {saidas_test.first()}")
    hoje = dj_timezone.now().date()
    
    # ================================================================
    # PROCESSAMENTO DOS FILTROS
    # ================================================================
    
    # Obter parâmetros de filtro
    periodo = request.GET.get('periodo', '30')
    data_inicial = request.GET.get('data_inicial')
    data_final = request.GET.get('data_final')
    tipo_transacao = request.GET.get('tipo_transacao', 'todos')
    conta_id = request.GET.get('conta', 'todas')
    categoria = request.GET.get('categoria', 'todas')
    forma_recebimento = request.GET.get('forma_recebimento', 'todas')
    valor_minimo = request.GET.get('valor_minimo')
    valor_maximo = request.GET.get('valor_maximo')
    status = request.GET.get('status', 'todos')
    recorrencia = request.GET.get('recorrencia', 'todas')
    meses_meta = int(request.GET.get('meses_meta', 6))

    # Processar datas baseadas nos filtros
    if data_inicial and data_final:
        try:
            data_inicio_filtro = datetime.strptime(data_inicial, '%Y-%m-%d').date()
            data_fim_filtro = datetime.strptime(data_final, '%Y-%m-%d').date()
        except ValueError:
            data_fim_filtro = hoje
            data_inicio_filtro = hoje - timedelta(days=int(periodo))
    else:
        # Usar período padrão
        data_fim_filtro = hoje
        if periodo == '30':
            data_inicio_filtro = hoje - timedelta(days=30)
        elif periodo == '90':
            data_inicio_filtro = hoje - timedelta(days=90)
        elif periodo == '180':
            data_inicio_filtro = hoje - timedelta(days=180)
        elif periodo == '365':
            data_inicio_filtro = hoje - timedelta(days=365)
        else:
            data_inicio_filtro = hoje - timedelta(days=30)

    # ================================================================
    # FILTRAGEM DOS DADOS - CORREÇÕES APLICADAS
    # ================================================================

    # Base querysets - CORRIGIDO: usando usuario em vez de conta_bancaria__proprietario
    entradas_base = Entrada.objects.filter(usuario=user)
    saidas_base = Saida.objects.filter(usuario=user)

    # Aplicar filtros de data - CORRIGIDO: campos de data corretos
    entradas_filtradas = entradas_base.filter(data__range=(data_inicio_filtro, data_fim_filtro))
    saidas_filtradas = saidas_base.filter(data_lancamento__range=(data_inicio_filtro, data_fim_filtro))

    # Filtro por tipo de transação
    if tipo_transacao == 'entradas':
        saidas_filtradas = saidas_filtradas.none()
    elif tipo_transacao == 'saidas':
        entradas_filtradas = entradas_filtradas.none()

    # Filtro por conta bancária
    if conta_id != 'todas':
        entradas_filtradas = entradas_filtradas.filter(conta_bancaria_id=conta_id)
        saidas_filtradas = saidas_filtradas.filter(conta_bancaria_id=conta_id)

    # Filtro por categoria
    if categoria != 'todas':
        saidas_filtradas = saidas_filtradas.filter(categoria=categoria)

    # Filtro por forma de recebimento
    if forma_recebimento != 'todas':
        entradas_filtradas = entradas_filtradas.filter(forma_recebimento=forma_recebimento)

    # Filtro por status
    if status != 'todos':
        saidas_filtradas = saidas_filtradas.filter(situacao=status)

    # Filtro por recorrência
    if recorrencia != 'todas':
        saidas_filtradas = saidas_filtradas.filter(recorrente=recorrencia)

    # Filtro por valor mínimo
    if valor_minimo:
        try:
            valor_min = Decimal(valor_minimo.replace('.', '').replace(',', '.'))
            entradas_filtradas = entradas_filtradas.filter(valor__gte=valor_min)
            saidas_filtradas = saidas_filtradas.filter(valor__gte=valor_min)
        except (InvalidOperation, ValueError):
            pass

    # Filtro por valor máximo
    if valor_maximo:
        try:
            valor_max = Decimal(valor_maximo.replace('.', '').replace(',', '.'))
            entradas_filtradas = entradas_filtradas.filter(valor__lte=valor_max)
            saidas_filtradas = saidas_filtradas.filter(valor__lte=valor_max)
        except (InvalidOperation, ValueError):
            pass

    # ================================================================
    # DADOS PRINCIPAIS (COM FILTROS APLICADOS) - CORREÇÕES APLICADAS
    # ================================================================

    # Saldo total (não filtrado por data) - CORRIGIDO: usando proprietario correto
    saldo_total = ContaBancaria.objects.filter(proprietario=user).aggregate(
        Sum('saldo_atual')
    )['saldo_atual__sum'] or Decimal('0.00')

    # Receitas e Despesas do período filtrado
    entradas_periodo = entradas_filtradas.aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')
    saidas_periodo = saidas_filtradas.aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')

    # Cálculo de variação (período anterior)
    dias_periodo = (data_fim_filtro - data_inicio_filtro).days
    periodo_anterior_inicio = data_inicio_filtro - timedelta(days=dias_periodo)
    periodo_anterior_fim = data_inicio_filtro - timedelta(days=1)

    entradas_periodo_anterior = entradas_base.filter(
        data__range=(periodo_anterior_inicio, periodo_anterior_fim)
    ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')

    saidas_periodo_anterior = saidas_base.filter(
        data_lancamento__range=(periodo_anterior_inicio, periodo_anterior_fim)
    ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')

    variacao_receitas = calculate_percentage_change(float(entradas_periodo), float(entradas_periodo_anterior))
    variacao_despesas = calculate_percentage_change(float(saidas_periodo), float(saidas_periodo_anterior))

    # Reserva de Emergência - CORRIGIDO: usando proprietario correto
    saldo_poupancas = ContaBancaria.objects.filter(
        proprietario=user,
        tipo='poupanca',
        ativa=True
    ).aggregate(Sum('saldo_atual'))['saldo_atual__sum'] or Decimal('0.00')

    # Despesa mensal média (últimos 6 meses) - CORRIGIDO: usando usuario
    data_seis_meses_atras = hoje - relativedelta(months=6)
    despesas_ultimos_6_meses = saidas_base.filter(
        data_lancamento__gte=data_seis_meses_atras,
        data_lancamento__lte=hoje
    ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')

    despesa_mensal_media = float(despesas_ultimos_6_meses) / 6 if despesas_ultimos_6_meses else 0

    # ================================================================
    # DADOS PARA GRÁFICOS (Últimos 12 meses) - CORREÇÕES APLICADAS
    # ================================================================
    num_meses_historico = 12
    meses_labels = []
    entradas_por_mes_data = []
    saidas_por_mes_data = []
    saldo_acumulado_data = []
    
    saldo_acumulado = float(saldo_total)  # Começa com o saldo atual

    for i in range(num_meses_historico - 1, -1, -1):
        data_mes = hoje - relativedelta(months=i)
        primeiro_dia, ultimo_dia = get_month_range(data_mes)
        
        entradas_mes = entradas_base.filter(
            data__range=(primeiro_dia, ultimo_dia)
        ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')

        saidas_mes = saidas_base.filter(
            data_lancamento__range=(primeiro_dia, ultimo_dia)
        ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')
        
        meses_labels.append(data_mes.strftime('%b/%y'))
        entradas_por_mes_data.append(float(entradas_mes))
        saidas_por_mes_data.append(float(saidas_mes))

        # Cálculo do saldo acumulado (mais preciso)
        if i == num_meses_historico - 1:
            # Primeiro mês: saldo atual - (entradas - saídas) dos meses seguintes
            saldo_acumulado_data.append(saldo_acumulado - (float(entradas_mes) - float(saidas_mes)))
        else:
            # Meses subsequentes: saldo do mês anterior - (entradas - saídas) do mês atual
            saldo_acumulado = saldo_acumulado_data[-1] - (float(entradas_mes) - float(saidas_mes))
            saldo_acumulado_data.append(saldo_acumulado)
    
    # Ajustar ordem cronológica
    meses_labels.reverse()
    entradas_por_mes_data.reverse()
    saidas_por_mes_data.reverse()
    saldo_acumulado_data.reverse()

    # ================================================================
    # SAZONALIDADE
    # ================================================================
    sazonalidade_labels = meses_labels
    sazonalidade_values = [e - s for e, s in zip(entradas_por_mes_data, saidas_por_mes_data)]

    # ================================================================
    # PROJEÇÃO FUTURA
    # ================================================================
    num_meses_projecao = 6
    projecao_labels = meses_labels.copy()
    projecao_saldo_data = saldo_acumulado_data.copy()

    if len(saldo_acumulado_data) >= 3:
        try:
            X_hist = np.array(range(len(saldo_acumulado_data))).reshape(-1, 1)
            y_hist_saldo = np.array(saldo_acumulado_data)

            model_saldo = LinearRegression().fit(X_hist, y_hist_saldo)

            X_fut = np.array(range(len(saldo_acumulado_data), len(saldo_acumulado_data) + num_meses_projecao)).reshape(-1, 1)
            projecao_saldo_futuro = model_saldo.predict(X_fut)

            for i in range(num_meses_projecao):
                next_month = hoje + relativedelta(months=i+1)
                projecao_labels.append(next_month.strftime('%b/%y'))
                projecao_saldo_data.append(float(projecao_saldo_futuro[i]))
        except Exception as e:
            print(f"Erro na projeção: {e}")

    # ================================================================
    # DESPESAS POR CATEGORIA (período filtrado)
    # ================================================================
    saidas_por_categoria = saidas_filtradas.values('categoria').annotate(
        total=Sum('valor')
    ).order_by('-total')

    mapa_categorias_saida_display = {c[0]: c[1] for c in CATEGORIA_CHOICES}
    categorias_despesas_labels = [
        mapa_categorias_saida_display.get(item['categoria'], item['categoria']) 
        for item in saidas_por_categoria
    ]
    categorias_despesas_data = [float(item['total']) for item in saidas_por_categoria]

    # ================================================================
    # RECEITAS POR FORMA DE RECEBIMENTO (período filtrado)
    # ================================================================
    entradas_por_forma = entradas_filtradas.values('forma_recebimento').annotate(
        total=Sum('valor')
    ).order_by('-total')

    if not entradas_por_forma:
        categorias_receitas_labels = ['Sem receitas']
        categorias_receitas_values = [0.0]
    else:
        mapa_formas_recebimento_display = {fr[0]: fr[1] for fr in FORMA_RECEBIMENTO_CHOICES}
        categorias_receitas_labels = [
            mapa_formas_recebimento_display.get(item['forma_recebimento'], item['forma_recebimento']) 
            for item in entradas_por_forma
        ]
        categorias_receitas_values = [float(item['total']) for item in entradas_por_forma]

    MAX_CATEGORIAS_RECEITAS = 6
    if len(categorias_receitas_labels) > MAX_CATEGORIAS_RECEITAS:
        categorias_receitas_labels = categorias_receitas_labels[:MAX_CATEGORIAS_RECEITAS]
        categorias_receitas_values = categorias_receitas_values[:MAX_CATEGORIAS_RECEITAS]

    # ================================================================
    # SALDOS POR CONTA BANCÁRIA - CORREÇÕES APLICADAS
    # ================================================================
    contas_ativas = ContaBancaria.objects.filter(proprietario=user, ativa=True)
    saldo_contas_labels = []
    saldo_contas_values = []
    
    for conta in contas_ativas:
        saldo_contas_labels.append(f"{conta.get_nome_banco_display()} ({conta.get_tipo_display()})")
        saldo_contas_values.append(float(conta.saldo_atual or Decimal('0.00')))

    # ================================================================
    # DESPESAS FIXAS VS VARIÁVEIS (período filtrado)
    # ================================================================
    despesas_fixas = saidas_filtradas.filter(
        recorrente__in=['mensal', 'anual']
    ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')

    despesas_variaveis = saidas_filtradas.exclude(
        recorrente__in=['mensal', 'anual']
    ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')

    # ================================================================
    # STATUS DE PAGAMENTOS (período filtrado)
    # ================================================================
    pagos_total = saidas_filtradas.filter(situacao='pago').aggregate(
        Sum('valor')
    )['valor__sum'] or Decimal('0.00')

    pendentes_total = saidas_filtradas.filter(situacao='pendente').aggregate(
        Sum('valor')
    )['valor__sum'] or Decimal('0.00')

    # ================================================================
    # ANÁLISE COMPORTAMENTAL - CORREÇÕES APLICADAS
    # ================================================================
    gastos_por_dia_semana_raw = {
        'Seg': Decimal('0.00'), 'Ter': Decimal('0.00'), 'Qua': Decimal('0.00'), 
        'Qui': Decimal('0.00'), 'Sex': Decimal('0.00'), 'Sáb': Decimal('0.00'), 'Dom': Decimal('0.00')
    }
    
    saidas_ultimos_30_dias = saidas_base.filter(
        data_lancamento__range=(hoje - timedelta(days=29), hoje)
    )
    
    dias_da_semana_map = {0: 'Seg', 1: 'Ter', 2: 'Qua', 3: 'Qui', 4: 'Sex', 5: 'Sáb', 6: 'Dom'}
    
    for saida in saidas_ultimos_30_dias:
        dia_semana_idx = saida.data_lancamento.weekday()
        dia_semana_label = dias_da_semana_map[dia_semana_idx]
        gastos_por_dia_semana_raw[dia_semana_label] += saida.valor

    gastos_por_dia_semana = {k: float(v) for k,v in gastos_por_dia_semana_raw.items()}

    # Gastos por hora do dia
    gastos_por_hora_dia_raw = {str(h): Decimal('0.00') for h in range(24)}
    for saida in saidas_ultimos_30_dias:
        if isinstance(saida.data_lancamento, datetime):
            hora = saida.data_lancamento.hour
        else:
            hora = 12  # Hora padrão se não for datetime
        gastos_por_hora_dia_raw[str(hora)] += saida.valor

    gastos_por_hora_dia = {k: float(v) for k,v in gastos_por_hora_dia_raw.items()}

    # Categorias comportamentais (simplificado)
    total_despesas_periodo = float(saidas_periodo)
    if total_despesas_periodo > 0:
        categorias_comportamento_data = {
            'Essenciais': total_despesas_periodo * 0.6,
            'Supérfluos': total_despesas_periodo * 0.3,
            'Investimentos': total_despesas_periodo * 0.1
        }
    else:
        categorias_comportamento_data = {
            'Essenciais': 0,
            'Supérfluos': 0,
            'Investimentos': 0
        }

    # ================================================================
    # INDICADORES DE SAÚDE FINANCEIRA - CORREÇÕES APLICADAS
    # ================================================================
    liquidez_corrente = (float(saldo_total) / float(saidas_periodo) * 100) if saidas_periodo and saidas_periodo > 0 else 0
    margem_seguranca = ((float(entradas_periodo) - float(saidas_periodo)) / float(entradas_periodo) * 100) if entradas_periodo and entradas_periodo > 0 else 0
    
    # Endividamento
    gastos_cartao_periodo = saidas_filtradas.filter(
        conta_bancaria__tipo='credito'
    ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')

    limite_total_credito = ContaBancaria.objects.filter(
        proprietario=user, tipo='credito'
    ).aggregate(Sum('limite_cartao'))['limite_cartao__sum'] or Decimal('0.00')

    endividamento = (float(gastos_cartao_periodo) / float(limite_total_credito) * 100) if limite_total_credito and limite_total_credito > 0 else 0
    
    poupanca_mensal_estimada = float(entradas_periodo) - float(saidas_periodo)
    reserva_emergencia_ideal_indicador = despesa_mensal_media * meses_meta

    nivel_risco_texto = "Baixo"
    if endividamento > 50: 
        nivel_risco_texto = "Alto"
    elif endividamento > 20: 
        nivel_risco_texto = "Moderado"

    # ================================================================
    # SIMULAÇÕES DE CENÁRIOS
    # ================================================================
    aumento_10_despesas = float(saidas_periodo) * 1.10
    reducao_10_despesas = float(saidas_periodo) * 0.90
    aumento_10_receitas = float(entradas_periodo) * 1.10
    reducao_10_receitas = float(entradas_periodo) * 0.90
    impacto_inflacao_5 = float(saidas_periodo) * 1.05

    # ================================================================
    # ANÁLISE DE RISCOS
    # ================================================================
    concentracao_risco = 0  # Simplificado

    # ================================================================
    # OTIMIZAÇÃO DE INVESTIMENTOS
    # ================================================================
    alocacao_investimentos_labels = ['Reserva Emergencial', 'Renda Fixa', 'Renda Variável']
    alocacao_investimentos_values = [70, 20, 10]
    
    sugestao_investimentos = "Priorize a construção da reserva de emergência."
    if float(saldo_poupancas) >= reserva_emergencia_ideal_indicador:
        sugestao_investimentos = "Sua reserva está completa! Considere diversificar seus investimentos."

    # ================================================================
    # ÚLTIMAS TRANSAÇÕES (período filtrado) - CORREÇÕES APLICADAS
    # ================================================================
    ultimas_entradas = entradas_filtradas.select_related('conta_bancaria').order_by('-data')[:5]
    ultimas_saidas = saidas_filtradas.select_related('conta_bancaria').order_by('-data_lancamento')[:5]

    ultimas_transacoes_list = []
    for entrada in ultimas_entradas:
        ultimas_transacoes_list.append({
            'data': entrada.data.isoformat(),
            'descricao': entrada.nome,
            'valor': float(entrada.valor),
            'tipo': 'Entrada',
            'categoria': 'Receita',
            'conta': entrada.conta_bancaria.get_nome_banco_display() if entrada.conta_bancaria else 'N/A'
        })

    for saida in ultimas_saidas:
        ultimas_transacoes_list.append({
            'data': saida.data_lancamento.isoformat(),
            'descricao': saida.nome,
            'valor': float(-saida.valor),
            'tipo': 'Saída',
            'categoria': saida.get_categoria_display() if saida.categoria else 'Sem Categoria',
            'conta': saida.conta_bancaria.get_nome_banco_display() if saida.conta_bancaria else 'N/A'
        })

    ultimas_transacoes_list.sort(key=lambda x: x['data'], reverse=True)
    ultimas_transacoes_list = ultimas_transacoes_list[:10]

    # ================================================================
    # CONSTRUÇÃO DO CONTEXTO JSON
    # ================================================================
    context_data = {
        'saldo_geral': float(saldo_total),
        'entradas_mes': float(entradas_periodo),
        'saidas_mes': float(saidas_periodo),
        'variacao_receitas': variacao_receitas,
        'variacao_despesas': variacao_despesas,
        
        'despesa_mensal_media': despesa_mensal_media,
        'saldo_poupancas': float(saldo_poupancas),
        'meses_meta': meses_meta,

        'indicadores': {
            'liquidez_corrente': liquidez_corrente,
            'margem_seguranca': margem_seguranca,
            'endividamento': endividamento,
            'poupanca_mensal': poupanca_mensal_estimada,
            'reserva_emergencia_ideal': reserva_emergencia_ideal_indicador,
        },

        'analise_comportamental': {
            'gastos_por_dia': gastos_por_dia_semana,
            'gastos_por_hora_dia': gastos_por_hora_dia,
            'categorias_comportamento': categorias_comportamento_data
        },

        'simulacoes': {
            'aumento_10_despesas': aumento_10_despesas,
            'reducao_10_despesas': reducao_10_despesas,
            'aumento_10_receitas': aumento_10_receitas,
            'reducao_10_receitas': reducao_10_receitas,
            'impacto_inflacao_5': impacto_inflacao_5
        },
        
        'analise_riscos': {
            'concentracao_risco': concentracao_risco,
            'reserva_ideal': reserva_emergencia_ideal_indicador,
            'nivel_risco': nivel_risco_texto
        },

        'otimizacao_investimentos': {
            'sugestao': sugestao_investimentos,
            'alocacao_labels': alocacao_investimentos_labels,
            'alocacao_values': alocacao_investimentos_values,
        },

        'ultimas_transacoes': ultimas_transacoes_list,

        'meses_labels': meses_labels,
        'receitas_mensais_data': entradas_por_mes_data,
        'despesas_mensais_data': saidas_por_mes_data,
        'saldo_acumulado_data': saldo_acumulado_data,
        'sazonalidade_labels': sazonalidade_labels,
        'sazonalidade_values': sazonalidade_values,
        
        'projecao_labels': projecao_labels,
        'projecao_saldo': projecao_saldo_data,

        'categorias_despesas_labels': categorias_despesas_labels,
        'categorias_despesas_data': categorias_despesas_data,
        'categorias_receitas_labels': categorias_receitas_labels,
        'categorias_receitas_values': categorias_receitas_values,
        
        'saldo_contas_labels': saldo_contas_labels,
        'saldo_contas_values': saldo_contas_values,
        
        'despesas_fixas': float(despesas_fixas),
        'despesas_variaveis': float(despesas_variaveis),

        'pagos_total': float(pagos_total),
        'pendentes_total': float(pendentes_total),
    }

    # Serializar para JSON
    try:
        dados_graficos_json = json.dumps(context_data, default=serialize_for_json)
    except Exception as e:
        print(f"Erro na serialização JSON: {e}")
        dados_graficos_json = "{}"

    # ================================================================
    # CONTEXTO FINAL
    # ================================================================
    context = {
        'dados_graficos_json': dados_graficos_json,
        'contas_bancarias': ContaBancaria.objects.filter(proprietario=user, ativa=True),
        'categorias_choices': CATEGORIA_CHOICES,
        'FORMA_RECEBIMENTO_CHOICES': FORMA_RECEBIMENTO_CHOICES,
        'filtros_atuais': {
            'periodo': periodo,
            'data_inicial': data_inicial,
            'data_final': data_final,
            'tipo_transacao': tipo_transacao,
            'conta': conta_id,
            'categoria': categoria,
            'forma_recebimento': forma_recebimento,
            'valor_minimo': valor_minimo,
            'valor_maximo': valor_maximo,
            'status': status,
            'recorrencia': recorrencia,
            'meses_meta': meses_meta,
        }
    }
    
    return render(request, 'core/dashboard.html', context)
    
# ===== FUNÇÕES ADICIONAIS =====
def get_contas_bancarias_data(usuario):
    """Retorna dados das contas bancárias para gráficos"""
    contas = ContaBancaria.objects.filter(proprietario=usuario, ativa=True)
    labels = [str(conta) for conta in contas]
    data = []
    
    for conta in contas:
        total_despesas = get_sum(Saida.objects.filter(usuario=usuario, conta_bancaria=conta))
        total_receitas = get_sum(Entrada.objects.filter(usuario=usuario, conta_bancaria=conta))
        saldo = float(total_receitas - total_despesas + (conta.saldo_atual or Decimal('0.00')))
        data.append(saldo)
    
    return {'labels': labels, 'data': data}

def get_saldos_contas(user):
    """
    Retorna os saldos atuais de todas as contas do usuário
    """
    contas = ContaBancaria.objects.filter(proprietario=user, ativa=True)
    saldos = {}
    
    for conta in contas:
        saldos[conta.id] = {
            'nome': str(conta),
            'tipo': conta.get_tipo_display(),
            'saldo': conta.saldo_atual
        }
    
    return saldos

# Opcional: Quebrar em funções auxiliares dentro da mesma view
def _calcular_dados_mensais(usuario, data_inicio, data_fim):
    """Calcula entradas e saídas para um período"""
    entradas = Entrada.objects.filter(
        conta_bancaria__proprietario=usuario,
        data_lancamento__range=(data_inicio, data_fim)
    ).aggregate(Sum('valor'))['valor__sum'] or 0
    
    saidas = Saida.objects.filter(
        conta_bancaria__proprietario=usuario,
        data_lancamento__range=(data_inicio, data_fim)
    ).aggregate(Sum('valor'))['valor__sum'] or 0
    
    return float(entradas), float(saidas)

# ===== VIEWS HTTP =====
@login_required
@require_GET
def get_account_balance(request, pk):  # Mudar account_id para pk
    """Retorna saldo de conta específica via AJAX"""
    try:
        conta = get_object_or_404(ContaBancaria, pk=pk, proprietario=request.user)
        
        # Para cartão de crédito, retornar limite disponível
        if conta.tipo == 'credito':
            saldo = conta.limite_cartao - (conta.saldo_atual or Decimal('0.00'))
        else:
            saldo = conta.saldo_atual or Decimal('0.00')
            
        return JsonResponse({'success': True, 'saldo': float(saldo)})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# ================================================================
# VIEWS DE CONTAS BANCÁRIAS
# ================================================================

@require_GET
def get_banco_code(request):
    nome_banco = request.GET.get('nome_banco')
    # Encontra o código correspondente ao nome do banco
    for bank_code, bank_name in BANCO_CHOICES:
        if bank_code == nome_banco:
            return HttpResponse(bank_code)
    return HttpResponse('')

@login_required
def conta_create(request):
    if request.method == 'POST':
        print("Dados POST recebidos:", request.POST)  # Debug
        form = ContaBancariaForm(request.POST, user=request.user)
        
        if form.is_valid():
            print("Formulário válido")  # Debug
            conta = form.save(commit=False)
            conta.proprietario = request.user
            conta.save()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Conta bancária adicionada com sucesso!'})
            else:
                messages.success(request, 'Conta bancária adicionada com sucesso!')
                return redirect('core:conta_list')
        else:
            print("Erros do formulário:", form.errors)  # Debug
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
            else:
                return render(request, 'core/conta_form.html', {'form': form, 'action': 'Adicionar'})
    else:
        form = ContaBancariaForm(user=request.user)
        return render(request, 'core/conta_form.html', {'form': form, 'action': 'Adicionar'})


@login_required
def conta_list(request):
    # Obter parâmetros de filtro da URL
    tipo_filtro = request.GET.get('tipo', '')
    status_filtro = request.GET.get('status', '')
    titular_filtro = request.GET.get('titular', '')
    banco_filtro = request.GET.get('banco', '')

    # Iniciar queryset base
    contas = ContaBancaria.objects.filter(proprietario=request.user)

    # Aplicar filtros
    if tipo_filtro:
        contas = contas.filter(tipo=tipo_filtro)
    
    if status_filtro == 'ativa':
        contas = contas.filter(ativa=True)
    elif status_filtro == 'inativa':
        contas = contas.filter(ativa=False)
    
    if titular_filtro:
        contas = contas.filter(nome_do_titular__icontains=titular_filtro)
    
    if banco_filtro:
        contas = contas.filter(nome_banco=banco_filtro)

    # Cálculos estatísticos
    contas_ativas = contas.filter(ativa=True).count()
    contas_inativas = contas.filter(ativa=False).count()
    total_contas = contas.count()

    # Calcular percentuais
    percentual_ativas = round((contas_ativas / total_contas * 100), 2) if total_contas > 0 else 0
    percentual_inativas = round((contas_inativas / total_contas * 100), 2) if total_contas > 0 else 0

    # Calcular saldo total
    saldo_total = contas.aggregate(total=Sum('saldo_atual'))['total'] or Decimal('0.00')
    
    # Saldo por tipo de conta
    saldo_por_tipo = contas.values('tipo').annotate(
        total_saldo=Sum('saldo_atual'),
        count=Count('id')
    ).order_by('tipo')

    # Data atual para filtrar transações
    from datetime import date
    hoje = date.today()

    for conta in contas:
        # Saldo Inicial = saldo_atual do modelo (saldo base da conta)
        # Usando nomes diferentes para evitar conflitos
        saldo_inicial_valor = conta.saldo_atual or Decimal('0.00')
        
        # Calcular entradas da conta ATÉ HOJE
        entradas_conta = Entrada.objects.filter(
            conta_bancaria=conta,
            data__lte=hoje
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        # Calcular saídas da conta ATÉ HOJE
        saidas_conta = Saida.objects.filter(
            conta_bancaria=conta,
            data_vencimento__lte=hoje,
            situacao='pago'
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        # Saldo Atual = Saldo Inicial + Entradas - Saídas
        saldo_calculado_valor = saldo_inicial_valor + entradas_conta - saidas_conta
        
        # Atribuir aos objetos de forma explícita
        conta.saldo_inicial_calc = saldo_inicial_valor
        conta.saldo_calculado_calc = saldo_calculado_valor
        
        # DEBUG: Verificar os valores
        print(f"=== CONTA: {conta.nome_banco} ===")
        print(f"Saldo Atual (BD): {conta.saldo_atual}")
        print(f"Saldo Inicial (Calc): {saldo_inicial_valor}")
        print(f"Entradas: {entradas_conta}")
        print(f"Saídas: {saidas_conta}")
        print(f"Saldo Calculado: {saldo_calculado_valor}")
        print("=" * 30)

    # Obter choices dos modelos
    tipos_conta_choices = ContaBancaria._meta.get_field('tipo').choices
    banco_choices = BANCO_CHOICES

    # Contas com titular diferente (para estatísticas)
    contas_com_titular_diferente = contas.exclude(nome_do_titular__isnull=True).exclude(nome_do_titular='').count()
    percentual_titular_diferente = round((contas_com_titular_diferente / total_contas * 100), 2) if total_contas > 0 else 0

    # Preparar contexto
    context = {
        'contas': contas.order_by('nome_banco', 'tipo'),
        'contas_ativas': contas_ativas,
        'contas_inativas': contas_inativas,
        'percentual_ativas': percentual_ativas,
        'percentual_inativas': percentual_inativas,
        'saldo_total': saldo_total,
        'saldo_por_tipo': saldo_por_tipo,
        'contas_com_titular_diferente': contas_com_titular_diferente,
        'percentual_titular_diferente': percentual_titular_diferente,
        
        # Filtros ativos
        'tipo_filtro': tipo_filtro,
        'status_filtro': status_filtro,
        'titular_filtro': titular_filtro,
        'banco_filtro': banco_filtro,
        
        # Choices para formulários
        'tipos_conta': tipos_conta_choices,
        'banco_choices': banco_choices,
        
        # Estatísticas adicionais
        'total_contas': total_contas,
        'contas_corrente': contas.filter(tipo='corrente').count(),
        'contas_poupanca': contas.filter(tipo='poupanca').count(),
        'contas_credito': contas.filter(tipo='credito').count(),
        'contas_investimento': contas.filter(tipo='investimento').count(),
        'contas_outras': contas.exclude(tipo__in=['corrente', 'poupanca', 'credito', 'investimento']).count(),
    }

    # Se for requisição AJAX, retornar JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        from django.core import serializers
        contas_data = []
        for conta in contas:
            contas_data.append({
                'id': conta.id,
                'nome_banco': conta.get_nome_banco_display(),
                'tipo': conta.get_tipo_display(),
                'agencia': conta.agencia,
                'numero_conta': conta.numero_conta,
                'nome_do_titular': conta.nome_do_titular,
                'saldo_atual': float(conta.saldo_atual),
                'saldo_inicial': float(conta.saldo_inicial),
                'saldo_calculado': float(conta.saldo_calculado),
                'ativa': conta.ativa,
                'numero_cartao': conta.numero_cartao,
                'limite_cartao': float(conta.limite_cartao) if conta.limite_cartao else None,
                'dia_fechamento_fatura': conta.dia_fechamento_fatura,
                'dia_vencimento_fatura': conta.dia_vencimento_fatura,
            })
        
        return JsonResponse({
            'success': True,
            'contas': contas_data,
            'estatisticas': {
                'total': total_contas,
                'ativas': contas_ativas,
                'inativas': contas_inativas,
                'saldo_total': float(saldo_total),
                'com_titular_diferente': contas_com_titular_diferente
            }
        })

    return render(request, 'core/conta_list.html', context)



@login_required
def conta_create_modal(request):
    if request.method == 'POST':
        form = ContaBancariaForm(request.POST, user=request.user)
        if form.is_valid():
            conta = form.save(commit=False)
            conta.proprietario = request.user
            conta.save()
            return JsonResponse({'success': True, 'message': 'Conta adicionada com sucesso!'})
        else:
            # Retorna os erros de validação
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = [{'message': error} for error in error_list]
            return JsonResponse({'success': False, 'errors': errors}, status=400)
    else:
        form = ContaBancariaForm(user=request.user)
    return render(request, 'core/includes/conta_form_modal.html', {'form': form})

@login_required
def conta_update(request, pk):
    conta = get_object_or_404(ContaBancaria, pk=pk, proprietario=request.user)
    
    if request.method == 'POST':
        form = ContaBancariaForm(request.POST, instance=conta, user=request.user)
        
        if form.is_valid():
            form.save()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Conta bancária atualizada com sucesso!'})
            else:
                messages.success(request, 'Conta bancária atualizada com sucesso!')
                return redirect('core:conta_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
            else:
                messages.error(request, 'Erro ao atualizar a conta bancária. Verifique os campos.')
                return render(request, 'core/conta_form.html', {'form': form, 'action': 'Atualizar'})
    
    # Para requisições GET, ainda redireciona para a página tradicional
    form = ContaBancariaForm(instance=conta, user=request.user)
    return render(request, 'core/conta_form.html', {'form': form, 'action': 'Atualizar'})

@login_required
def conta_delete(request, pk):
    conta = get_object_or_404(ContaBancaria, pk=pk, proprietario=request.user)
    
    if request.method == 'POST':
        conta.delete()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Conta bancária excluída com sucesso!'})
        
        messages.success(request, 'Conta bancária excluída com sucesso!')
        return redirect('core:conta_list')
    
    # Se for GET, retorna o template tradicional (para navegadores sem JS)
    return render(request, 'core/conta_confirm_delete.html', {'conta': conta})

@login_required
@require_GET
def buscar_contas_por_titular(request):
    """API para buscar contas por nome do titular"""
    termo = request.GET.get('q', '')
    
    if not termo or len(termo) < 2:
        return JsonResponse({'success': False, 'message': 'Termo de busca muito curto'})
    
    contas = ContaBancaria.objects.filter(
        proprietario=request.user,
        nome_do_titular__icontains=termo
    ).values('id', 'nome_do_titular', 'nome_banco', 'tipo')[:10]
    
    resultados = []
    for conta in contas:
        resultados.append({
            'id': conta['id'],
            'text': f"{conta['nome_do_titular']} - {dict(BANCO_CHOICES).get(conta['nome_banco'], conta['nome_banco'])} ({dict(TIPO_CONTA_CHOICES).get(conta['tipo'], conta['tipo'])})"
        })
    
    return JsonResponse({'success': True, 'results': resultados})


@login_required
@require_GET
def estatisticas_contas(request):
    """API para obter estatísticas detalhadas das contas"""
    contas = ContaBancaria.objects.filter(proprietario=request.user)
    
    # Estatísticas básicas
    total_contas = contas.count()
    contas_ativas = contas.filter(ativa=True).count()
    saldo_total = contas.aggregate(total=Sum('saldo_atual'))['total'] or Decimal('0.00')
    
    # Estatísticas por tipo
    por_tipo = contas.values('tipo').annotate(
        count=Count('id'),
        saldo_total=Sum('saldo_atual')
    ).order_by('tipo')
    
    # Estatísticas por titular
    contas_proprias = contas.filter(nome_do_titular__isnull=True) | contas.filter(nome_do_titular='')
    contas_terceiros = contas.exclude(nome_do_titular__isnull=True).exclude(nome_do_titular='')
    
    estatisticas = {
        'total_contas': total_contas,
        'contas_ativas': contas_ativas,
        'contas_inativas': total_contas - contas_ativas,
        'saldo_total': float(saldo_total),
        'contas_proprias': contas_proprias.count(),
        'contas_terceiros': contas_terceiros.count(),
        'por_tipo': list(por_tipo),
        'top_titulares': list(contas_terceiros.values('nome_do_titular')
                              .annotate(count=Count('id'), saldo=Sum('saldo_atual'))
                              .order_by('-count')[:5])
    }
    
    return JsonResponse({'success': True, 'estatisticas': estatisticas})



# ================================================================
# VIEWS DE ENTRADAS
# ================================================================

# core/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from decimal import Decimal
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from .models import Entrada, ContaBancaria, Saida
from .choices import FORMA_RECEBIMENTO_CHOICES

# core/views.py
@login_required
def entrada_list(request):
    user = request.user
    hoje = date.today()
    
    # Definir mês e ano padrão
    mes_atual = hoje.month
    ano_atual = hoje.year
    
    # Obter parâmetros de filtro
    ano_filtro = request.GET.get('ano')
    mes_filtro = request.GET.get('mes')  # Agora será None se não estiver presente
    conta_filter_id = request.GET.get('conta')
    forma_recebimento_filter = request.GET.get('forma_recebimento')
    
    # Validar ano - se não especificado, usar ano atual
    try:
        ano_filtro = int(ano_filtro) if ano_filtro else ano_atual
    except (ValueError, TypeError):
        ano_filtro = ano_atual
    
    # Validar mês - se não especificado ou vazio, mostrar todos os meses
    mes_num = None
    if mes_filtro and mes_filtro.strip():  # Se mes_filtro não é None nem vazio
        try:
            mes_num = int(mes_filtro)
            if mes_num < 1 or mes_num > 12:
                mes_num = None  # Valor inválido, mostrar todos os meses
        except (ValueError, TypeError):
            mes_num = None
    
    # Aplicar filtros às entradas
    entradas = Entrada.objects.filter(conta_bancaria__proprietario=user)
    
    # Sempre filtrar pelo ano (usar ano atual se não especificado)
    entradas = entradas.filter(data__year=ano_filtro)
    
    # Filtrar por mês apenas se um mês específico foi selecionado
    if mes_num:
        entradas = entradas.filter(data__month=mes_num)
        mes_selecionado = str(mes_num)
    else:
        mes_selecionado = ''  # String vazia para "Todos os meses"
    
    # Outros filtros
    if conta_filter_id:
        entradas = entradas.filter(conta_bancaria__id=conta_filter_id)
    
    if forma_recebimento_filter:
        entradas = entradas.filter(forma_recebimento=forma_recebimento_filter)
    
    # Cálculos para os cards (agora considerando o filtro de mês)
    total_entradas = entradas.aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
    
    # CALCULAR SALDO RESIDUAL (saldo anterior ao período atual)
    saldo_residual = Decimal('0.00')
    
    # Para cada conta ativa do usuário
    for conta in ContaBancaria.objects.filter(proprietario=user, ativa=True):
        # 1. Saldo inicial da conta
        saldo_inicial = conta.saldo_atual or Decimal('0.00')
        
        # 2. Entradas anteriores ao período atual
        # Se filtrando por mês específico, considerar até o final do mês anterior
        # Se mostrando todos os meses, considerar até o final do ano anterior
        if mes_num:
            # Filtro por mês específico - saldo residual é tudo antes do mês atual
            primeiro_dia_mes_atual = date(ano_filtro, mes_num, 1)
            entradas_anteriores = Entrada.objects.filter(
                conta_bancaria=conta,
                data__lt=primeiro_dia_mes_atual
            ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        else:
            # Todos os meses - saldo residual é tudo antes do ano atual
            primeiro_dia_ano_atual = date(ano_filtro, 1, 1)
            entradas_anteriores = Entrada.objects.filter(
                conta_bancaria=conta,
                data__lt=primeiro_dia_ano_atual
            ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        # 3. Saídas anteriores ao período atual (mesma lógica)
        if mes_num:
            primeiro_dia_mes_atual = date(ano_filtro, mes_num, 1)
            saidas_anteriores = Saida.objects.filter(
                conta_bancaria=conta,
                data_lancamento__lt=primeiro_dia_mes_atual
            ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        else:
            primeiro_dia_ano_atual = date(ano_filtro, 1, 1)
            saidas_anteriores = Saida.objects.filter(
                conta_bancaria=conta,
                data_lancamento__lt=primeiro_dia_ano_atual
            ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        # Saldo residual = saldo inicial + entradas anteriores - saídas anteriores
        saldo_conta = saldo_inicial + entradas_anteriores - saidas_anteriores
        saldo_residual += saldo_conta
    
    # Saldo total = entradas do período + saldo residual
    saldo_total = total_entradas + saldo_residual
    
    # Cálculo da variação mensal (apenas se estiver filtrando por mês específico)
    variacao_mensal = Decimal('0.00')
    if mes_num:
        # Calcular entradas do mês anterior
        if mes_num == 1:
            mes_anterior = 12
            ano_mes_anterior = ano_filtro - 1
        else:
            mes_anterior = mes_num - 1
            ano_mes_anterior = ano_filtro
        
        entradas_mes_anterior = Entrada.objects.filter(
            conta_bancaria__proprietario=user,
            data__month=mes_anterior,
            data__year=ano_mes_anterior
        )
        
        # Aplicar mesmos filtros de conta e forma de recebimento
        if conta_filter_id:
            entradas_mes_anterior = entradas_mes_anterior.filter(conta_bancaria__id=conta_filter_id)
        
        if forma_recebimento_filter:
            entradas_mes_anterior = entradas_mes_anterior.filter(forma_recebimento=forma_recebimento_filter)
        
        total_mes_anterior = entradas_mes_anterior.aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        # Calcular variação percentual
        if total_mes_anterior > 0:
            variacao_mensal = ((total_entradas - total_mes_anterior) / total_mes_anterior) * 100
        else:
            variacao_mensal = Decimal('100.00') if total_entradas > 0 else Decimal('0.00')
        
        variacao_mensal = round(variacao_mensal, 2)
    
    # Cálculo da média mensal (considera todos os meses com registros)
    total_meses_com_entradas = Entrada.objects.filter(
        conta_bancaria__proprietario=user
    ).dates('data', 'month').count()
    
    total_geral_entradas = Entrada.objects.filter(
        conta_bancaria__proprietario=user
    ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
    
    media_mensal = total_geral_entradas / total_meses_com_entradas if total_meses_com_entradas > 0 else Decimal('0.00')
    media_mensal = round(media_mensal, 2)
    
    # Nome do mês para exibição
    meses_choices = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
        (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
        (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
    ]
    
    if mes_num:
        mes_nome = dict(meses_choices).get(mes_num, '')
    else:
        mes_nome = f'Todos os meses de {ano_filtro}'
    
    # Contas bancárias para filtros
    contas_bancarias = ContaBancaria.objects.filter(proprietario=user, ativa=True)
    
    # Anos disponíveis
    anos_disponiveis = sorted(list(set(
        list(Entrada.objects.filter(conta_bancaria__proprietario=user).values_list('data__year', flat=True)) +
        list(range(ano_atual - 2, ano_atual + 2))
    )), reverse=True)
    
    # Mapeamentos para exibição
    contas_bancarias_display_map = {str(c.id): c.get_nome_banco_display() for c in contas_bancarias}
    meses_disponiveis_display_map = {str(k): v for k, v in meses_choices}
    forma_recebimento_choices_map = {code: name for code, name in FORMA_RECEBIMENTO_CHOICES}
    
    # Paginação
    paginator = Paginator(entradas.order_by('-data'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'entradas': page_obj,
        'total_entradas': total_entradas,
        'saldo_total': saldo_total,
        'saldo_residual': saldo_residual,
        'variacao_mensal': variacao_mensal,
        'media_mensal': media_mensal,
        'mes_atual_nome': mes_nome,
        'ano_atual': ano_filtro,
        
        # Filtros
        'mes_filter': mes_selecionado,  # String vazia para "Todos os meses"
        'ano_filter': str(ano_filtro),
        'conta_filter': conta_filter_id,
        'forma_recebimento_filter': forma_recebimento_filter,
        
        # Opções para selects
        'meses_disponiveis': meses_choices,
        'anos_disponiveis': anos_disponiveis,
        'contas_bancarias': contas_bancarias,
        'contas_bancarias_filter': contas_bancarias,
        'FORMA_RECEBIMENTO_CHOICES': FORMA_RECEBIMENTO_CHOICES,
        
        # Mapeamentos para badges
        'contas_bancarias_display_map': contas_bancarias_display_map,
        'meses_disponiveis_display_map': meses_disponiveis_display_map,
        'FORMA_RECEBIMENTO_CHOICES_MAP': forma_recebimento_choices_map,
        
        # Paginação
        'page_obj': page_obj,
    }
    
    return render(request, 'core/entrada_list.html', context)

@login_required
def entrada_create(request):
    if request.method == 'POST':
        form = EntradaForm(request.POST, user=request.user)
        if form.is_valid():
            entrada = form.save(commit=False)
            entrada.usuario = request.user
            entrada.save()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Entrada criada com sucesso!'})
            else:
                messages.success(request, 'Entrada criada com sucesso!')
                return redirect('core:entrada_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        form = EntradaForm(user=request.user)
    
    # Obter contas bancárias do usuário
    contas_bancarias = ContaBancaria.objects.filter(proprietario=request.user, ativa=True)
    
    # Se for requisição AJAX (modal), retornar JSON com os dados necessários
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        contas_data = [{'id': conta.id, 'nome': conta.get_nome_banco_display()} for conta in contas_bancarias]
        
        return JsonResponse({
            'form_html': render_to_string('core/includes/entrada_form_modal.html', {
                'form': form,
                'FORMA_RECEBIMENTO_CHOICES': FORMA_RECEBIMENTO_CHOICES,
                'contas_bancarias': contas_bancarias
            }, request=request)
        })
    
    # Se for requisição normal, renderizar a página completa
    return render(request, 'core/entrada_form.html', {
        'form': form,
        'action': 'Criar',
        'FORMA_RECEBIMENTO_CHOICES': FORMA_RECEBIMENTO_CHOICES,
        'contas_bancarias': contas_bancarias
    })

@login_required
def entrada_update(request, pk):
    entrada = get_object_or_404(Entrada, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        form = EntradaForm(request.POST, instance=entrada, user=request.user)
        if form.is_valid():
            form.save()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Entrada atualizada com sucesso!'})
            else:
                messages.success(request, 'Entrada atualizada com sucesso!')
                return redirect('core:entrada_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
            else:
                messages.error(request, 'Erro ao atualizar a entrada. Verifique os campos.')
    
    else:
        form = EntradaForm(instance=entrada, user=request.user)
    
    # Obter contas bancárias do usuário
    contas_bancarias = ContaBancaria.objects.filter(proprietario=request.user, ativa=True)
    
    # Se for requisição AJAX (modal), retornar JSON com os dados necessários
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'form_html': render_to_string('core/includes/entrada_form_modal.html', {
                'form': form,
                'FORMA_RECEBIMENTO_CHOICES': FORMA_RECEBIMENTO_CHOICES,
                'contas_bancarias': contas_bancarias
            }, request=request)
        })
    
    return render(request, 'core/entrada_form.html', {
        'form': form,
        'action': 'Atualizar',
        'FORMA_RECEBIMENTO_CHOICES': FORMA_RECEBIMENTO_CHOICES,
        'contas_bancarias': contas_bancarias
    })

@login_required
def entrada_delete(request, pk):
    entrada = get_object_or_404(Entrada, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        entrada.delete()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Entrada excluída com sucesso!'})
        
        messages.success(request, 'Entrada excluída com sucesso!')
        return redirect('core:entrada_list')
    
    # Se for GET e AJAX, retornar informações para o modal de confirmação
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'entrada_nome': entrada.nome,
            'entrada_valor': str(entrada.valor),
            'entrada_data': entrada.data.strftime('%d/%m/%Y')
        })
    
    # Se for GET tradicional, retornar o template de confirmação
    return render(request, 'core/entrada_confirm_delete.html', {'entrada': entrada})


# ================================================================
# VIEWS DE SAÍDAS CORRIGIDAS
# ================================================================
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone as dj_timezone
from django.views import View
from django.db.models import Q
from dateutil.relativedelta import relativedelta
from decimal import Decimal
import json
from .models import Saida, ContaBancaria, Categoria
from .forms import SaidaForm
from .choices import CATEGORIA_CHOICES, SUBCATEGORIA_CHOICES


@login_required
def saida_list(request):
    meses_choices = [
        ('01', 'Janeiro'), ('02', 'Fevereiro'), ('03', 'Março'), ('04', 'Abril'),
        ('05', 'Maio'), ('06', 'Junho'), ('07', 'Julho'), ('08', 'Agosto'),
        ('09', 'Setembro'), ('10', 'Outubro'), ('11', 'Novembro'), ('12', 'Dezembro')
    ]
    
    STATUS_CHOICES_DISPLAY = [
        ('pago', 'Pago'),
        ('pendente', 'Pendente')
    ]

    hoje = dj_timezone.now()
    ano_atual = hoje.year
    mes_atual = hoje.month
    
    # Filtros - CORREÇÃO: Sempre começar com ano e mês atuais quando não especificados
    ano_filter_str = request.GET.get('ano', '')
    mes_filter_str = request.GET.get('mes', '')
    status_filter_code = request.GET.get('status', '')
    
    # Se não há filtros, usar ano e mês atuais
    if not ano_filter_str and not mes_filter_str:
        ano_filter = ano_atual
        mes_num = mes_atual
        mes_selecionado = str(mes_atual).zfill(2)
    else:
        # Validar filtro de ano
        if ano_filter_str:
            try:
                ano_filter = int(ano_filter_str)
            except (ValueError, TypeError):
                ano_filter = ano_atual
        else:
            ano_filter = ano_atual
        
        # Validar filtro de mês
        if mes_filter_str:
            try:
                mes_num = int(mes_filter_str)
                if mes_num < 1 or mes_num > 12:
                    mes_num = mes_atual
                mes_selecionado = str(mes_num).zfill(2)
            except (ValueError, TypeError):
                mes_num = mes_atual
                mes_selecionado = str(mes_atual).zfill(2)
        else:
            mes_num = None
            mes_selecionado = ''
    
    if status_filter_code:
        status_selecionado = status_filter_code
    else:
        status_selecionado = ''
    
    # Aplica os filtros
    saidas_qs = Saida.objects.filter(usuario=request.user)
    saidas_qs = saidas_qs.filter(data_vencimento__year=ano_filter)
    
    if mes_num:
        saidas_qs = saidas_qs.filter(data_vencimento__month=mes_num)
    
    if status_filter_code:
        saidas_qs = saidas_qs.filter(situacao=status_filter_code)
    
    # Processar despesas
    saidas = saidas_qs.order_by('-data_vencimento')
    
    # Cálculos para os cards
    total_despesas = get_sum(saidas_qs)
    despesas_pagas = get_sum(saidas_qs.filter(situacao='pago'))
    despesas_pendentes = get_sum(saidas_qs.filter(situacao='pendente'))
    
    percentual_pago = round((despesas_pagas / total_despesas * 100) if total_despesas > 0 else 0, 2)
    percentual_pendente = round((despesas_pendentes / total_despesas * 100) if total_despesas > 0 else 0, 2)
    
    # Variação mensal
    variacao_mensal = Decimal('0.00')
    variacao_mensal_abs = Decimal('0.00')
    
    if mes_num:
        mes_anterior_date = hoje - relativedelta(months=1)
        primeiro_dia_mes_anterior, ultimo_dia_mes_anterior = get_month_range(mes_anterior_date)
        
        saidas_mes_anterior_qs = Saida.objects.filter(
            usuario=request.user,
            data_vencimento__range=(primeiro_dia_mes_anterior, ultimo_dia_mes_anterior)
        )
        
        if status_filter_code:
            saidas_mes_anterior_qs = saidas_mes_anterior_qs.filter(situacao=status_filter_code)

        total_despesas_mes_anterior = get_sum(saidas_mes_anterior_qs)
        
        if total_despesas_mes_anterior > 0:
            variacao_mensal = round(((total_despesas - total_despesas_mes_anterior) / total_despesas_mes_anterior * 100), 2)
        else:
            variacao_mensal = Decimal('100.00') if total_despesas > 0 else Decimal('0.00')
        
        variacao_mensal_abs = abs(variacao_mensal)
    
    # Nome do mês para o título
    if mes_selecionado:
        mes_nome = dict(meses_choices).get(mes_selecionado, '')
    else:
        mes_nome = 'Todos os meses'

    # Anos disponíveis
    anos_com_registros = set(Saida.objects.filter(usuario=request.user).values_list('data_vencimento__year', flat=True))
    anos_disponiveis = sorted(list(anos_com_registros.union(range(ano_atual - 2, ano_atual + 2))), reverse=True)

    # Mapeamentos
    meses_display_map = {k: v for k, v in meses_choices}
    status_display_map = {k: v for k, v in STATUS_CHOICES_DISPLAY}
    
    # Obter contas bancárias ativas do usuário
    contas_bancarias = ContaBancaria.objects.filter(proprietario=request.user, ativa=True)

 # ====== CONTEXTO CORRIGIDO PARA CATEGORIAS/SUBCATEGORIAS ======
    
    # Choices das categorias
    categorias_choices = CATEGORIA_CHOICES
    
    # Choices das subcategorias (formato correto)
    subcategorias_choices = SUBCATEGORIA_CHOICES
    
    # Mapeamento subcategoria -> categoria (para JavaScript)
    subcategoria_mapping = {
        # Moradia
        'moradia_aluguel': 'moradia',
        'moradia_financiamento': 'moradia',
        'moradia_condominio': 'moradia',
        'moradia_iptu': 'moradia',
        'moradia_energia': 'moradia',
        'moradia_agua': 'moradia',
        'moradia_gas': 'moradia',
        'moradia_internet': 'moradia',
        'moradia_manutencao': 'moradia',
        
        # Alimentação
        'alimentacao_supermercado': 'alimentacao',
        'alimentacao_hortifruti': 'alimentacao',
        'alimentacao_padaria': 'alimentacao',
        'alimentacao_restaurante': 'alimentacao',
        'alimentacao_lanches': 'alimentacao',
        
        # Transporte
        'transporte_combustivel': 'transporte',
        'transporte_manutencao': 'transporte',
        'transporte_seguro': 'transporte',
        'transporte_estacionamento': 'transporte',
        'transporte_publico': 'transporte',
        'transporte_app': 'transporte',
        
        # Saúde
        'saude_plano': 'saude',
        'saude_medicamentos': 'saude',
        'saude_consultas': 'saude',
        'saude_exames': 'saude',
        'saude_odontologia': 'saude',
        
        # Educação
        'educacao_mensalidade': 'educacao',
        'educacao_cursos': 'educacao',
        'educacao_materiais': 'educacao',
        
        # Lazer
        'lazer_cinema': 'lazer',
        'lazer_shows': 'lazer',
        'lazer_viagens': 'lazer',
        'lazer_entretenimento': 'lazer',

        # Seguros
        'seguros_vida': 'seguros',
        'seguros_residencial': 'seguros',
        'seguros_viagem': 'seguros',

        # Despesas Pessoais
        'pessoais_academia': 'pessoais',
        'pessoais_estetica': 'pessoais',
        'pessoais_vestuario': 'pessoais',
        'pessoais_calcados': 'pessoais',
        'pessoais_acessorios': 'pessoais',

        # Família
        'familia_mesada': 'familia',
        'familia_presentes': 'familia',
        'familia_pets': 'familia',

        # Contas e Serviços
        'contas_telefone': 'contas',
        'contas_assinaturas': 'contas',
        'contas_tv': 'contas',

        # Investimentos
        'investimentos_poupanca': 'investimentos',
        'investimentos_fundos': 'investimentos',
        'investimentos_acoes': 'investimentos',
        'investimentos_cripto': 'investimentos',

        # Impostos
        'impostos_irpf': 'impostos',
        'impostos_inss': 'impostos',
        'impostos_taxas': 'impostos',
    }

    context = {
        'saidas': saidas,
        'total_despesas': total_despesas,
        'despesas_pagas': despesas_pagas,
        'despesas_pendentes': despesas_pendentes,
        'percentual_pago': percentual_pago,
        'percentual_pendente': percentual_pendente,
        'variacao_mensal': variacao_mensal,
        'variacao_mensal_abs': variacao_mensal_abs,
        'mes_atual_nome': mes_nome,
        'ano_atual': ano_filter,
        'meses': meses_choices,
        'anos_disponiveis': anos_disponiveis,
        'STATUS_CHOICES': STATUS_CHOICES_DISPLAY,
        'ano_selecionado': str(ano_filter),
        'mes_selecionado': mes_selecionado,
        'status_selecionado': status_selecionado,
        'meses_display_map': meses_display_map,
        'status_display_map': status_display_map,
        'today_date': dj_timezone.now().date().isoformat(),
        'contas_bancarias': contas_bancarias,
        
        # ====== NOVAS VARIÁVEIS PARA CATEGORIAS/SUBCATEGORIAS ======
        'categorias_choices': categorias_choices,
        'subcategorias_choices': subcategorias_choices,
        'subcategoria_mapping': subcategoria_mapping,
    }
    
    context = {
        'saidas': saidas,
        'total_despesas': total_despesas,
        'despesas_pagas': despesas_pagas,
        'despesas_pendentes': despesas_pendentes,
        'percentual_pago': percentual_pago,
        'percentual_pendente': percentual_pendente,
        'variacao_mensal': variacao_mensal,
        'variacao_mensal_abs': variacao_mensal_abs,
        
        # Variáveis para o filtro
        'mes_atual_nome': dict(meses_choices).get(str(mes_atual).zfill(2)),
        'mes_atual_num': mes_atual,
        'ano_atual': ano_atual,
        
        # Filtros atuais
        'ano_selecionado': str(ano_filter),
        'mes_selecionado': mes_selecionado,
        'status_selecionado': status_selecionado,
        
        # Opções disponíveis
        'meses': meses_choices,
        'anos_disponiveis': anos_disponiveis,
        'STATUS_CHOICES': STATUS_CHOICES_DISPLAY,
        'meses_display_map': meses_display_map,
        'status_display_map': status_display_map,
        'today_date': dj_timezone.now().date().isoformat(),
        'contas_bancarias': contas_bancarias,
        
        # Categorias e subcategorias
        'categorias_choices': categorias_choices,
        'subcategorias_choices': subcategorias_choices,
        'subcategoria_mapping': subcategoria_mapping,
    }
    
    return render(request, 'core/saida_list.html', context)

@login_required
@csrf_exempt
def saida_create(request):
    """
    View para criar nova despesa com validações de parcelamento e recorrência
    """
    if request.method == 'POST':
        try:
            data = request.POST.copy()
            
            print("Dados recebidos:", dict(data))
            print("Recorrência selecionada:", data.get('recorrente'))
            
            # Processar valor monetário
            if 'valor' in data and data['valor']:
                try:
                    valorstr = data['valor'].replace("R$", "").replace(".", "").replace(",", ".").strip()
                    datavalor = Decimal(valorstr)
                    print("Valor convertido:", datavalor)
                except (ValueError, InvalidOperation) as e:
                    print("Erro na conversão do valor:", e)
                    return JsonResponse({
                        'success': False,
                        'errors': {'valor': ['Valor inválido. Use o formato: 1234,56']},
                        'message': 'Erro na formatação do valor'
                    }, status=400)
            
            # VALIDAÇÃO: Parcelamento só permitido para cartão de crédito ou boleto
            tipo_pagamento = data.get('tipo_pagamento_detalhe')
            forma_pagamento = data.get('forma_pagamento')
            
            if tipo_pagamento == 'parcelado' and forma_pagamento not in ['cartao_credito', 'boleto']:
                return JsonResponse({
                    'success': False,
                    'errors': {
                        'tipo_pagamento_detalhe': ['Parcelamento só é permitido para Cartão de Crédito ou Boleto.'],
                        'forma_pagamento': ['Forma de pagamento não permite parcelamento.']
                    },
                    'message': 'Parcelamento não permitido para esta forma de pagamento'
                }, status=400)
            
            # VALIDAÇÃO: Não permitir recorrência com parcelamento
            recorrente = data.get('recorrente', 'unica')
            if tipo_pagamento == 'parcelado' and recorrente != 'unica':
                return JsonResponse({
                    'success': False,
                    'errors': {
                        'recorrente': ['Não é possível combinar recorrência com parcelamento.'],
                        'tipo_pagamento_detalhe': ['Parcelamento não pode ser recorrente.']
                    },
                    'message': 'Não é possível combinar recorrência com parcelamento'
                }, status=400)
            
            # Processar valor da parcela se existir
            if 'valor_parcela' in data and data['valor_parcela']:
                try:
                    valor_parcela_str = data['valor_parcela'].replace('R$', '').replace('.', '').replace(',', '.').strip()
                    valor_parcela_str = valor_parcela_str.replace('.', '', valor_parcela_str.count('.') - 1) if valor_parcela_str.count('.') > 1 else valor_parcela_str
                    data['valor_parcela'] = Decimal(valor_parcela_str) if valor_parcela_str else None
                except (ValueError, InvalidOperation):
                    data['valor_parcela'] = None
            
            # Se for à vista, limpar campos de parcelamento
            if data.get('tipo_pagamento_detalhe') == 'avista':
                data['quantidade_parcelas'] = 1
                if 'valor' in data and data['valor']:
                    data['valor_parcela'] = data['valor']
            
            # Criar e validar formulário
            form = SaidaForm(data, user=request.user)
            
            if form.is_valid():
                saida = form.save(commit=False)
                saida.usuario = request.user
                
                # Se for recorrente, garantir que é à vista
                if saida.recorrente != 'unica':
                    saida.tipo_pagamento_detalhe = 'avista'
                    saida.quantidade_parcelas = 1
                    saida.parcela_atual = 1
                    saida.valor_parcela = saida.valor
                
                saida.save()
                
                # SE FOR PARCELADO: Criar parcelas futuras
                if saida.tipo_pagamento_detalhe == 'parcelado' and saida.quantidade_parcelas > 1:
                    criar_parcelas_futuras(saida)
                
                # SE FOR RECORRENTE: Criar ocorrências futuras
                if saida.recorrente != 'unica':
                    print(f"Criando ocorrências futuras para recorrência: {saida.recorrente}")
                    criar_ocorrencias_futuras(saida)
                
                print("Despesa salva com sucesso. ID:", saida.id)
                
                return JsonResponse({
                    'success': True,
                    'message': 'Despesa criada com sucesso!',
                    'saida_id': saida.id
                })
            else:
                print("Erros no formulário:", form.errors)
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = [str(error) for error in error_list]
                
                return JsonResponse({
                    'success': False,
                    'errors': errors,
                    'message': 'Por favor, corrija os erros no formulário.'
                }, status=400)
                
        except Exception as e:
            print("Erro ao criar despesa:", str(e))
            import traceback
            traceback.print_exc()
            
            return JsonResponse({
                'success': False,
                'message': f'Erro interno do servidor: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido'
    }, status=405)




def criar_ocorrencias_futuras(saida_original):
    """
    Cria ocorrências futuras para despesas recorrentes baseado no tipo de recorrência
    Limite máximo: 24 meses a partir da data original
    """
    from dateutil.relativedelta import relativedelta
    from datetime import date
    
    # Mapeamento de recorrência para meses
    recorrencia_meses = {
        'mensal': 1,
        'anual': 12
    }
    
    meses_entre_ocorrencias = recorrencia_meses.get(saida_original.recorrente, 1)
    data_base = saida_original.data_vencimento
    data_limite = data_base + relativedelta(months=24)  # Limite de 24 meses
    
    ocorrencias_criadas = 0
    data_ocorrencia = data_base
    
    # Para a primeira ocorrência futura, já avançamos o período
    data_ocorrencia = data_ocorrencia + relativedelta(months=meses_entre_ocorrencias)
    
    while ocorrencias_criadas < 24 and data_ocorrencia <= data_limite:
        # Cria nova ocorrência
        nova_ocorrencia = Saida.objects.create(
            usuario=saida_original.usuario,
            conta_bancaria=saida_original.conta_bancaria,
            nome=f"{saida_original.nome} ({ocorrencias_criadas + 2})",
            local=saida_original.local,
            categoria=saida_original.categoria,
            subcategoria=saida_original.subcategoria,
            observacao=saida_original.observacao,
            valor=saida_original.valor,
            data_lancamento=data_ocorrencia,
            data_vencimento=data_ocorrencia,
            forma_pagamento=saida_original.forma_pagamento,
            tipo_pagamento_detalhe='avista',  # Recorrência sempre à vista
            quantidade_parcelas=1,
            parcela_atual=1,
            valor_parcela=saida_original.valor,
            recorrente=saida_original.recorrente,
            situacao='pendente',
            recorrencia_original=saida_original,  # Usar o campo correto para recorrência
            e_recorrente=True
        )
        
        ocorrencias_criadas += 1
        print(f"Ocorrência {ocorrencias_criadas} criada para {data_ocorrencia}")
        
        # Avança para a próxima ocorrência
        data_ocorrencia = data_ocorrencia + relativedelta(months=meses_entre_ocorrencias)
    
    print(f"Total de {ocorrencias_criadas} ocorrências futuras criadas para a despesa {saida_original.id}")


def criar_parcelas_futuras(saida_original):
    """
    Cria parcelas futuras para uma despesa parcelada
    """
    from dateutil.relativedelta import relativedelta
    
    # A PRIMEIRA PARCELA JÁ EXISTE (é a saida_original), então começamos da parcela 2
    for numero_parcela in range(2, saida_original.quantidade_parcelas + 1):
        nova_saida = Saida(
            usuario=saida_original.usuario,
            conta_bancaria=saida_original.conta_bancaria,
            nome=f"{saida_original.nome} (Parcela {numero_parcela}/{saida_original.quantidade_parcelas})",
            local=saida_original.local,
            categoria=saida_original.categoria,
            subcategoria=saida_original.subcategoria,
            observacao=saida_original.observacao,
            valor=saida_original.valor_parcela,  # Usar o valor da parcela, não o total
            data_lancamento=saida_original.data_lancamento + relativedelta(months=numero_parcela-1),
            data_vencimento=saida_original.data_vencimento + relativedelta(months=numero_parcela-1),
            forma_pagamento=saida_original.forma_pagamento,
            tipo_pagamento_detalhe=saida_original.tipo_pagamento_detalhe,
            recorrente='unica',  # Parcelas não são recorrentes
            quantidade_parcelas=saida_original.quantidade_parcelas,
            valor_parcela=saida_original.valor_parcela,
            situacao='pendente',
            parcela_atual=numero_parcela,
            despesa_original=saida_original,
            e_parcela=True  # Marcar como parcela (não original)
        )
        nova_saida.save()
    print(f"Total de {saida_original.quantidade_parcelas - 1} parcelas futuras criadas")



def configurar_proxima_ocorrencia(saida_original):
    """
    Configura a próxima ocorrência para uma despesa recorrente
    """
    from dateutil.relativedelta import relativedelta
    
    # Mapeamento de recorrência para intervalo
    intervalos = {
        'mensal': relativedelta(months=1),
        'trimestral': relativedelta(months=3),
        'semestral': relativedelta(months=6),
        'anual': relativedelta(years=1)
    }
    
    if saida_original.recorrente in intervalos:
        intervalo = intervalos[saida_original.recorrente]
        
        nova_saida = Saida(
            usuario=saida_original.usuario,
            conta_bancaria=saida_original.conta_bancaria,
            nome=saida_original.nome,
            local=saida_original.local,
            categoria=saida_original.categoria,
            subcategoria=saida_original.subcategoria,
            observacao=saida_original.observacao,
            valor=saida_original.valor,
            data_lancamento=saida_original.data_lancamento + intervalo,
            data_vencimento=saida_original.data_vencimento + intervalo,
            forma_pagamento=saida_original.forma_pagamento,
            tipo_pagamento_detalhe='avista',  # Recorrência sempre à vista
            recorrente=saida_original.recorrente,
            quantidade_parcelas=1,
            valor_parcela=saida_original.valor,
            situacao='pendente',
            parcela_atual=1,
            despesa_original=saida_original
        )
        nova_saida.save()
        

@login_required
def saida_info(request, pk):
    saida = get_object_or_404(Saida, pk=pk, usuario=request.user)
    
    data = {
        'success': True,
        'despesa': {
            'id': saida.id,
            'nome': saida.nome,
            'tipo_pagamento': saida.tipo_pagamento_detalhe,
            'quantidade_parcelas': saida.quantidade_parcelas,
            'parcela_atual': saida.parcela_atual,
            'recorrente': saida.recorrente,
            'valor': str(saida.valor),
        }
    }
    
    return JsonResponse(data)

@login_required
def saida_update(request, pk):
    from decimal import Decimal, InvalidOperation
    from django.db import transaction
    from dateutil.relativedelta import relativedelta

    saida = get_object_or_404(Saida, pk=pk, usuario=request.user)

    if request.method == 'POST':
        print("=== DEBUG VALORES ===")
        print("Valor recebido:", request.POST.get('valor'))
        print("Valor parcela recebido:", request.POST.get('valor_parcela'))

        # Se for requisição AJAX para carregar o formulário
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.POST.get('action') == 'get_form':
            try:
                form = SaidaForm(instance=saida, user=request.user)

                valor_total = saida.valor
                if saida.tipo_pagamento_detalhe == 'parcelado' and saida.quantidade_parcelas and saida.quantidade_parcelas > 1:
                    # valor armazenado por item pode representar parcela ou total no seu modelo; você já lidava com isso
                    valor_total = saida.valor_parcela * saida.quantidade_parcelas if saida.valor_parcela else saida.valor

                form_html = render_to_string('core/includes/saida_edit_modal.html', {
                    'form': form,
                    'saida': saida,
                    'contas_bancarias': ContaBancaria.objects.filter(proprietario=request.user, ativa=True),
                    'categorias_choices': CATEGORIA_CHOICES,
                    'subcategorias_choices': SUBCATEGORIA_CHOICES,
                    'subcategoria_mapping': {  # mantém seu mapeamento
                        'moradia_aluguel': 'moradia',
                        'moradia_financiamento': 'moradia',
                        'moradia_condominio': 'moradia',
                        'moradia_iptu': 'moradia',
                        'moradia_energia': 'moradia',
                        'moradia_agua': 'moradia',
                        'moradia_gas': 'moradia',
                        'moradia_internet': 'moradia',
                        'moradia_manutencao': 'moradia',
                        'alimentacao_supermercado': 'alimentacao',
                        'alimentacao_hortifruti': 'alimentacao',
                        'alimentacao_padaria': 'alimentacao',
                        'alimentacao_restaurante': 'alimentacao',
                        'alimentacao_lanches': 'alimentacao',
                        'transporte_combustivel': 'transporte',
                        'transporte_manutencao': 'transporte',
                        'transporte_seguro': 'transporte',
                        'transporte_estacionamento': 'transporte',
                        'transporte_publico': 'transporte',
                        'transporte_app': 'transporte',
                        'saude_plano': 'saude',
                        'saude_medicamentos': 'saude',
                        'saude_consultas': 'saude',
                        'saude_exames': 'saude',
                        'saude_odontologia': 'saude',
                        'educacao_mensalidade': 'educacao',
                        'educacao_cursos': 'educacao',
                        'educacao_materiais': 'educacao',
                        'lazer_cinema': 'lazer',
                        'lazer_shows': 'lazer',
                        'lazer_viagens': 'lazer',
                        'lazer_entretenimento': 'lazer',
                        'seguros_vida': 'seguros',
                        'seguros_residencial': 'seguros',
                        'seguros_viagem': 'seguros',
                        'pessoais_academia': 'pessoais',
                        'pessoais_estetica': 'pessoais',
                        'pessoais_vestuario': 'pessoais',
                        'pessoais_calcados': 'pessoais',
                        'pessoais_acessorios': 'pessoais',
                        'familia_mesada': 'familia',
                        'familia_presentes': 'familia',
                        'familia_pets': 'familia',
                        'contas_telefone': 'contas',
                        'contas_assinaturas': 'contas',
                        'contas_tv': 'contas',
                        'investimentos_poupanca': 'investimentos',
                        'investimentos_fundos': 'investimentos',
                        'investimentos_acoes': 'investimentos',
                        'investimentos_cripto': 'investimentos',
                        'impostos_irpf': 'impostos',
                        'impostos_inss': 'impostos',
                        'impostos_taxas': 'impostos',
                    },
                    'today_date': date.today().isoformat(),
                    'valor_total': valor_total,
                }, request=request)

                return JsonResponse({'success': True, 'form_html': form_html})
            except Exception as e:
                print(f"Erro ao carregar formulário de edição: {e}")
                return JsonResponse({'success': False, 'message': f'Erro ao carregar formulário: {str(e)}'}, status=500)

        # Processamento normal do POST (edição)
        print("=== PROCESSANDO EDIÇÃO DE DESPESA ===")
        print("Dados recebidos:", dict(request.POST))

        post_data = request.POST.copy()
        tipo_edicao = post_data.get('tipo_edicao', 'parcela')
        aplicar_todas = post_data.get('aplicar_todas', 'false') == 'true'

        print(f"Tipo de edição: {tipo_edicao}")
        print(f"Aplicar para todas: {aplicar_todas}")

        # Conversão segura de valores para Decimal (aceita formatos '1.234,56' ou '1234.56')
        def parse_decimal(valor_raw):
            if valor_raw is None or valor_raw == '':
                return None
            v = str(valor_raw).strip()
            v = v.replace('R$', '').strip()
            # Sevirá tanto "1.234,56" quanto "1234.56"
            v = v.replace('.', '').replace(',', '.') if ',' in v else v
            try:
                return Decimal(v)
            except (InvalidOperation, ValueError):
                return None

        if 'valor' in post_data and post_data['valor']:
            parsed = parse_decimal(post_data['valor'])
            if parsed is None:
                return JsonResponse({'success': False, 'errors': {'valor': ['Valor inválido. Use 1234,56']}, 'message': 'Erro na formatação do valor'}, status=400)
            post_data['valor'] = parsed

        if 'valor_parcela' in post_data and post_data['valor_parcela']:
            parsed_parc = parse_decimal(post_data['valor_parcela'])
            post_data['valor_parcela'] = parsed_parc

        # Garantir campos padrão se ausentes
        if 'tipo_pagamento_detalhe' not in post_data or not post_data.get('tipo_pagamento_detalhe'):
            post_data['tipo_pagamento_detalhe'] = 'avista'
        if 'recorrente' not in post_data or not post_data.get('recorrente'):
            post_data['recorrente'] = 'unica'
        if 'quantidade_parcelas' not in post_data or not post_data.get('quantidade_parcelas'):
            post_data['quantidade_parcelas'] = saida.quantidade_parcelas or 1
        else:
            try:
                post_data['quantidade_parcelas'] = int(post_data['quantidade_parcelas'])
            except Exception:
                post_data['quantidade_parcelas'] = saida.quantidade_parcelas or 1

        # Se à vista, forçar 1 parcela
        if post_data.get('tipo_pagamento_detalhe') == 'avista':
            post_data['quantidade_parcelas'] = 1
            if 'valor' in post_data:
                post_data['valor_parcela'] = post_data['valor']

        # Construir form com os dados processados
        form = SaidaForm(post_data, instance=saida, user=request.user)

        if not form.is_valid():
            print("=== ERROS DE VALIDAÇÃO ===")
            print(form.errors)
            return JsonResponse({'success': False, 'errors': form.errors, 'message': 'Erro de validação. Verifique os campos.'}, status=400)

        # Tudo validado — agora salvar conforme o tipo de edição
        try:
            with transaction.atomic():
                # ----- EDIÇÃO DE UMA ÚNICA PARCELA (sem aplicar nas demais) -----
                if tipo_edicao == 'parcela' and not aplicar_todas:
                    saida_atual = form.save(commit=False)
                    # mantém data_lancamento original se não foi enviada
                    if 'data_lancamento' not in post_data or not post_data.get('data_lancamento'):
                        saida_atual.data_lancamento = saida.data_lancamento
                    # Se o form trouxe valor_parcela específico, atualiza
                    if post_data.get('valor_parcela') is not None:
                        saida_atual.valor_parcela = post_data['valor_parcela']
                        saida_atual.valor = post_data.get('valor', saida_atual.valor)
                    saida_atual.save()
                    print("Parcela individual atualizada (sem aplicar nas demais).")

                # ----- APLICAR ALTERAÇÃO PARA TODAS AS PARCELAS -----
                elif tipo_edicao == 'parcela' and aplicar_todas:
                    # Pegar a "despesa base" (a original que vincula parcelas) — mantém sua lógica
                    despesa_base = saida.despesa_original if saida.despesa_original else saida
                    parcelas = Saida.objects.filter(Q(despesa_original=despesa_base) | Q(pk=despesa_base.pk)).order_by('parcela_atual')
                    if not parcelas.exists():
                        # fallback: atualiza apenas a atual
                        saida_salva = form.save()
                        print("Nenhuma parcela encontrada vinculada — atualizei apenas a atual.")
                    else:
                        # Determinar novo valor_parcela a aplicar a todas
                        novo_valor_parcela = None
                        if post_data.get('valor_parcela') is not None:
                            novo_valor_parcela = post_data['valor_parcela']
                        elif post_data.get('valor') is not None:
                            qtd = post_data.get('quantidade_parcelas') or parcelas.count()
                            novo_valor_parcela = (Decimal(post_data['valor']) / Decimal(qtd)).quantize(Decimal('0.01'))
                        else:
                            novo_valor_parcela = parcelas.first().valor_parcela or parcelas.first().valor

                        qtd_parcelas = post_data.get('quantidade_parcelas') or parcelas.count()
                        # Atualiza cada parcela
                        primeira_venc = post_data.get('data_vencimento') or parcelas.first().data_vencimento
                        if isinstance(primeira_venc, str):
                            primeira_venc = datetime.strptime(primeira_venc, "%Y-%m-%d").date()
                        for parcela in parcelas:
                            parcela.conta_bancaria = form.cleaned_data['conta_bancaria']
                            parcela.nome = form.cleaned_data['nome']
                            parcela.local = form.cleaned_data['local']
                            parcela.categoria = form.cleaned_data['categoria']
                            parcela.subcategoria = form.cleaned_data['subcategoria']
                            parcela.observacao = form.cleaned_data['observacao']
                            parcela.forma_pagamento = form.cleaned_data['forma_pagamento']
                            parcela.tipo_pagamento_detalhe = form.cleaned_data['tipo_pagamento_detalhe']
                            parcela.recorrente = form.cleaned_data['recorrente']
                            parcela.quantidade_parcelas = qtd_parcelas
                            parcela.valor_parcela = novo_valor_parcela
                            parcela.valor = novo_valor_parcela
                            parcela.situacao = form.cleaned_data['situacao']

                            # Ajusta vencimento relativo à primeira parcela
                            meses_diff = parcela.parcela_atual - 1
                            parcela.data_vencimento = (primeira_venc + relativedelta(months=meses_diff)) if primeira_venc else parcela.data_vencimento
                            parcela.save()
                        print(f"Aplicadas alterações a todas as {parcelas.count()} parcelas.")

                # ----- EDIÇÃO COMPLETA (todas) => redivide/ajusta número de parcelas -----
                elif tipo_edicao == 'todas':
                    # Base para parcelamento (despesa original)
                    despesa_base = saida.despesa_original if saida.despesa_original else saida
                    parcelas = list(Saida.objects.filter(Q(despesa_original=despesa_base) | Q(pk=despesa_base.pk)).order_by('parcela_atual'))

                    valor_total = post_data.get('valor') if post_data.get('valor') is not None else sum((p.valor for p in parcelas)) if parcelas else Decimal('0.00')
                    nova_qtd = int(post_data.get('quantidade_parcelas') or len(parcelas) or 1)
                    if nova_qtd < 1:
                        nova_qtd = 1

                    # calcular valores por parcela distribuindo centavos no final
                    base_amount = (Decimal(valor_total) / Decimal(nova_qtd)).quantize(Decimal('0.01'))
                    amounts = [base_amount] * nova_qtd
                    soma = sum(amounts)
                    diferenca = Decimal(valor_total) - soma
                    # adiciona a diferença (pode ser centavos) na última parcela
                    if diferenca != 0:
                        amounts[-1] = (amounts[-1] + diferenca).quantize(Decimal('0.01'))

                    # Ajustar número de registros: criar ou apagar conforme necessário
                    atual_qtd = len(parcelas)
                    primeira_venc = post_data.get('data_vencimento') or (parcelas[0].data_vencimento if parcelas else None)
                    if isinstance(primeira_venc, str):
                        primeira_venc = datetime.strptime(primeira_venc, "%Y-%m-%d").date()

                    # Se precisar criar parcelas novas
                    if nova_qtd > atual_qtd:
                        # garante que exista um 'base' que será despesa_original
                        base_obj = despesa_base
                        for idx in range(atual_qtd + 1, nova_qtd + 1):
                            new = Saida.objects.create(
                                usuario=request.user,
                                conta_bancaria=parcelas[0].conta_bancaria if parcelas else form.cleaned_data['conta_bancaria'],
                                nome=form.cleaned_data.get('nome') or (parcelas[0].nome if parcelas else ''),
                                local=form.cleaned_data.get('local') or (parcelas[0].local if parcelas else ''),
                                categoria=form.cleaned_data.get('categoria') or (parcelas[0].categoria if parcelas else None),
                                subcategoria=form.cleaned_data.get('subcategoria') or (parcelas[0].subcategoria if parcelas else None),
                                observacao=form.cleaned_data.get('observacao') or '',
                                forma_pagamento=form.cleaned_data.get('forma_pagamento') or (parcelas[0].forma_pagamento if parcelas else 'dinheiro'),
                                tipo_pagamento_detalhe='parcelado',
                                recorrente=form.cleaned_data.get('recorrente') or 'unica',
                                quantidade_parcelas=nova_qtd,
                                valor=amounts[idx - 1],
                                valor_parcela=amounts[idx - 1],
                                situacao=form.cleaned_data.get('situacao') or 'pendente',
                                parcela_atual=idx,
                                despesa_original=None,  # será ajustado corretamente logo abaixo

                                data_lancamento=parcelas[0].data_lancamento if parcelas else date.today(),
                                data_vencimento=(primeira_venc + relativedelta(months=idx - 1)) if primeira_venc else None
                            )
                            # após criar, vincula despesa_original adequadamente
                            # (vamos corrigir todos os despesa_original logo abaixo)
                            parcelas.append(new)

                    # Se precisar remover parcelas
                    elif nova_qtd < atual_qtd:
                        # apagar as últimas parcelas (atenção: pode haver regras específicas no seu app)
                        to_delete = parcelas[nova_qtd:]
                        for p in to_delete:
                            p.delete()
                        parcelas = parcelas[:nova_qtd]

                    # Recarregar parcelas ordenadas novamente
                    parcelas = list(Saida.objects.filter(Q(despesa_original=despesa_base) | Q(pk=despesa_base.pk)).order_by('parcela_atual')[:nova_qtd])

                    # Se não existiam parcelas, talvez despesa_base seja a própria saida — garanta que exista ao menos uma
                    if not parcelas:
                        # salva a saida atual como primeira parcela
                        primeira = form.save(commit=False)
                        primeira.quantidade_parcelas = nova_qtd
                        primeira.valor = amounts[0]
                        primeira.valor_parcela = amounts[0]
                        if primeira_venc:
                            primeira.data_vencimento = primeira_venc
                        primeira.save()
                        parcelas = [primeira]

                    # agora atualizar todas (reajusta parcela_atual consecutivo, valores, vencimentos e despesa_original)
                    base_obj = parcelas[0]  # manter referência ao primeiro como base
                    for idx, parcela in enumerate(parcelas, start=1):
                        parcela.parcela_atual = idx
                        parcela.quantidade_parcelas = nova_qtd
                        parcela.valor = amounts[idx - 1]
                        parcela.valor_parcela = amounts[idx - 1]
                        parcela.conta_bancaria = form.cleaned_data.get('conta_bancaria') or parcela.conta_bancaria
                        parcela.nome = form.cleaned_data.get('nome') or parcela.nome
                        parcela.local = form.cleaned_data.get('local') or parcela.local
                        parcela.categoria = form.cleaned_data.get('categoria') or parcela.categoria
                        parcela.subcategoria = form.cleaned_data.get('subcategoria') or parcela.subcategoria
                        parcela.observacao = form.cleaned_data.get('observacao') or parcela.observacao
                        parcela.forma_pagamento = form.cleaned_data.get('forma_pagamento') or parcela.forma_pagamento
                        parcela.tipo_pagamento_detalhe = 'parcelado'
                        parcela.recorrente = form.cleaned_data.get('recorrente') or parcela.recorrente
                        parcela.situacao = form.cleaned_data.get('situacao') or parcela.situacao
                        parcela.data_vencimento = (primeira_venc + relativedelta(months=idx - 1)) if primeira_venc else parcela.data_vencimento
                        # garantir despesa_original aponta para o primeiro (exceto o próprio primeiro)
                        if idx == 1:
                            # primeira parcela fica como "principal" (não aponta para outra)
                            parcela.despesa_original = None
                        else:
                            parcela.despesa_original = parcelas[0]
                        parcela.save()

                    # se primeira parcela foi atualizada via form, salva seus campos finais também
                    print(f"Reconfiguradas {len(parcelas)} parcelas com novo total {valor_total} e {nova_qtd} parcelas.")

                else:
                    # caso genérico: salvar o form na instância atual
                    saida_salva = form.save(commit=False)
                    # Garantir campos essenciais
                    if 'data_lancamento' not in post_data or not post_data.get('data_lancamento'):
                        saida_salva.data_lancamento = saida.data_lancamento
                    saida_salva.save()
                    print("Alteração genérica aplicada na saída atual.")

            # fim do transaction.atomic
            print("Despesa atualizada com sucesso!")
            return JsonResponse({'success': True, 'message': 'Despesa atualizada com sucesso!'})

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Erro ao salvar despesa: {e}")
            return JsonResponse({'success': False, 'message': f'Erro ao atualizar despesa: {str(e)}', 'error_details': str(e)}, status=500)

    return redirect('core:saida_list')




@login_required
def debug_saida_update(request, pk):
    """View temporária para debug"""
    saida = get_object_or_404(Saida, pk=pk, usuario=request.user)
    
    print("=== DEBUG SAIDA UPDATE ===")
    print(f"Method: {request.method}")
    print(f"Headers: {dict(request.headers)}")
    print(f"POST data: {dict(request.POST)}")
    print(f"is_ajax: {request.headers.get('x-requested-with') == 'XMLHttpRequest'}")
    
    return JsonResponse({
        'debug': True,
        'method': request.method,
        'is_ajax': request.headers.get('x-requested-with') == 'XMLHttpRequest',
        'action': request.POST.get('action'),
        'saida_id': saida.id
    })


def formatar_valor_para_formulario(valor):
    """
    Formata valor decimal para o formato usado no formulário (com vírgula)
    """
    if valor is None:
        return ''
    
    try:
        # Converte para string e substitui ponto por vírgula
        valor_str = str(valor)
        if '.' in valor_str:
            partes = valor_str.split('.')
            if len(partes) == 2:
                # Formata com 2 casas decimais
                return f"{partes[0]},{partes[1].ljust(2, '0')}"
        return valor_str.replace('.', ',')
    except:
        return str(valor)

@login_required
def marcar_como_pago(request, pk):
    """
    View para marcar despesa como paga
    """
    try:
        saida = Saida.objects.get(pk=pk, usuario=request.user)
        
        if saida.situacao != 'pago':
            saida.situacao = 'pago'
            saida.data_lancamento = dj_timezone.now().date()
            
            # Se for à vista, ajustar data de vencimento
            if saida.tipo_pagamento_detalhe == 'avista':
                saida.data_vencimento = saida.data_lancamento
            
            saida.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'Despesa marcada como paga com sucesso!'
            })
        else:
            return JsonResponse({
                'success': False, 
                'message': 'Esta despesa já está paga.'
            })
            
    except Saida.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'message': 'Despesa não encontrada.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao marcar despesa como paga: {str(e)}'
        }, status=500)


@login_required
def saida_delete(request, pk):
    """
    View para excluir despesa com opções para parcelas e recorrências
    """
    try:
        saida = get_object_or_404(Saida, pk=pk, usuario=request.user)

        if request.method == 'POST':
            delete_option = request.POST.get('delete_option', 'esta')
            nome_despesa = saida.nome
            count = 1  # Contador padrão para uma despesa
            
            print(f"Excluindo despesa {pk} com opção: {delete_option}")
            
            if delete_option == 'esta':
                # Excluir apenas esta despesa
                saida.delete()
                message = f'Despesa "{nome_despesa}" excluída com sucesso!'
                
            elif delete_option == 'todas_parcelas' and saida.despesa_original:
                # Excluir todas as parcelas (esta é uma parcela)
                despesa_original = saida.despesa_original
                parcelas = Saida.objects.filter(
                    Q(despesa_original=despesa_original) | Q(pk=despesa_original.pk)
                )
                count = parcelas.count()
                parcelas.delete()
                message = f'Todas as {count} parcelas da despesa "{despesa_original.nome}" foram excluídas!'
                
            elif delete_option == 'todas_parcelas_futuras' and saida.parcela_atual == 1:
                # Excluir apenas parcelas futuras (esta é a primeira parcela)
                parcelas_futuras = Saida.objects.filter(
                    despesa_original=saida,
                    parcela_atual__gt=1
                )
                count = parcelas_futuras.count()
                parcelas_futuras.delete()
                # Mantém a primeira parcela (esta)
                message = f'{count} parcelas futuras da despesa "{nome_despesa}" foram excluídas!'
                
            elif delete_option == 'todas_ocorrencias' and saida.despesa_original:
                # Excluir todas as ocorrências recorrentes
                despesa_original = saida.despesa_original
                ocorrencias = Saida.objects.filter(
                    Q(despesa_original=despesa_original) | Q(pk=despesa_original.pk)
                )
                count = ocorrencias.count()
                ocorrencias.delete()
                message = f'Todas as {count} ocorrências da despesa "{despesa_original.nome}" foram excluídas!'
                
            elif delete_option == 'futuras_ocorrencias' and saida.despesa_original:
                # Excluir apenas ocorrências futuras
                ocorrencias_futuras = Saida.objects.filter(
                    despesa_original=saida.despesa_original,
                    data_vencimento__gt=saida.data_vencimento
                )
                count = ocorrencias_futuras.count()
                ocorrencias_futuras.delete()
                message = f'{count} ocorrências futuras da despesa "{saida.despesa_original.nome}" foram excluídas!'
                
            else:
                # Fallback: excluir apenas esta despesa
                saida.delete()
                message = f'Despesa "{nome_despesa}" excluída com sucesso!'

            print(f"Exclusão concluída: {message}")

            # Para requisições AJAX
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'message': message
                })

            messages.success(request, message)
            return redirect('saida_list')

        # GET request - Retornar informações sobre a despesa para o modal
        elif request.method == 'GET':
            print(f"Buscando informações da despesa {pk}")
            
            despesa_info = {
                'id': saida.id,
                'nome': saida.nome,
                'valor': str(saida.valor),
                'data_vencimento': saida.data_vencimento.strftime('%d/%m/%Y'),
                'tipo_pagamento': saida.tipo_pagamento_detalhe,
                'parcela_atual': saida.parcela_atual,
                'quantidade_parcelas': saida.quantidade_parcelas,
                'recorrente': saida.recorrente,
                'tem_parcelas': False,
                'tem_recorrencias': False,
                'e_parcela': saida.despesa_original is not None,
                'e_original': saida.parcela_atual == 1 and saida.quantidade_parcelas > 1,
                'e_recorrente': saida.recorrente != 'unica',
            }
            
            # Verificar se existem parcelas
            if saida.despesa_original:
                print("Esta despesa é uma parcela")
                # Esta é uma parcela - ver quantas parcelas existem no total
                despesa_original = saida.despesa_original
                total_parcelas = Saida.objects.filter(
                    Q(despesa_original=despesa_original) | Q(pk=despesa_original.pk)
                ).count()
                despesa_info['total_parcelas'] = total_parcelas
                despesa_info['tem_parcelas'] = total_parcelas > 1
                print(f"Total de parcelas encontradas: {total_parcelas}")
                
            elif saida.parcela_atual == 1 and saida.quantidade_parcelas > 1:
                print("Esta despesa é a primeira parcela")
                # Esta é a primeira parcela - ver se existem parcelas futuras
                parcelas_futuras = Saida.objects.filter(
                    despesa_original=saida,
                    parcela_atual__gt=1
                ).count()
                despesa_info['parcelas_futuras'] = parcelas_futuras
                despesa_info['tem_parcelas'] = parcelas_futuras > 0
                print(f"Parcelas futuras encontradas: {parcelas_futuras}")
            
            # Verificar se existem ocorrências recorrentes
            if saida.despesa_original and saida.recorrente != 'unica':
                print("Esta despesa tem ocorrências recorrentes")
                ocorrencias = Saida.objects.filter(
                    despesa_original=saida.despesa_original
                ).count()
                despesa_info['total_ocorrencias'] = ocorrencias
                despesa_info['tem_recorrencias'] = ocorrencias > 1
                print(f"Total de ocorrências: {ocorrencias}")
                
            elif saida.recorrente != 'unica':
                print("Esta despesa é recorrente")
                ocorrencias_futuras = Saida.objects.filter(
                    despesa_original=saida,
                    data_vencimento__gt=saida.data_vencimento
                ).count()
                despesa_info['ocorrencias_futuras'] = ocorrencias_futuras
                despesa_info['tem_recorrencias'] = ocorrencias_futuras > 0
                print(f"Ocorrências futuras: {ocorrencias_futuras}")

            print(f"Informações da despesa: {despesa_info}")

            return JsonResponse({
                'success': True,
                'despesa': despesa_info
            })

        return JsonResponse({
            'success': False,
            'message': 'Método não permitido'
        }, status=405)
        
    except Saida.DoesNotExist:
        print(f"Despesa {pk} não encontrada")
        # Despesa já foi excluída ou não existe
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Despesa não encontrada ou já foi excluída.'
            }, status=404)
        
        messages.error(request, 'Despesa não encontrada ou já foi excluída.')
        return redirect('saida_list')
        
    except Exception as e:
        # Log do erro para debug
        print(f"Erro ao excluir despesa {pk}: {str(e)}")
        import traceback
        traceback.print_exc()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Erro ao excluir despesa: {str(e)}'
            }, status=500)
        
        messages.error(request, 'Erro ao excluir despesa.')
        return redirect('saida_list')

def get_month_range(date):
    """Retorna o primeiro e último dia do mês"""
    from calendar import monthrange
    year = date.year
    month = date.month
    first_day = dj_timezone.datetime(year, month, 1).date()
    last_day = dj_timezone.datetime(year, month, monthrange(year, month)[1]).date()
    return first_day, last_day


class GetSubcategoriasView(View):
    def get(self, request, *args, **kwargs):
        categoria = request.GET.get('categoria')
        subcategorias = [
            {'id': sc[0], 'nome': sc[1]} 
            for sc in SUBCATEGORIA_CHOICES 
            if sc[2] == categoria
        ]
        return JsonResponse(subcategorias, safe=False)
# ================================================================
# VIEWS DE EXTRATO COMPLETO
# ================================================================

@login_required
def extrato_completo(request):
    meses = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
        (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
        (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
    ]
    
    hoje = datetime.now()
    ano_atual = hoje.year
    mes_atual = hoje.month
    
    # Obter parâmetros de filtro
    ano_filtro = request.GET.get('ano', str(ano_atual))
    mes_filtro = request.GET.get('mes', str(mes_atual))
    tipo_filtro = request.GET.get('tipo')
    conta_filtro = request.GET.get('conta')
    
    # Obter todas as contas do usuário para o filtro
    contas_usuario = ContaBancaria.objects.filter(proprietario=request.user)

        
    # ADICIONE ESTA LINHA - contas bancárias para o modal
    contas_bancarias = ContaBancaria.objects.filter(proprietario=request.user, ativa=True)
    
    # Filtrar entradas e saídas
    entradas = Entrada.objects.filter(usuario=request.user)
    saidas = Saida.objects.filter(usuario=request.user)
    
    # Aplicar filtros
    if mes_filtro and mes_filtro != 'todos':
        entradas = entradas.filter(data__month=mes_filtro)
        saidas = saidas.filter(data_vencimento__month=mes_filtro)
    
    if ano_filtro and ano_filtro != 'todos':
        entradas = entradas.filter(data__year=ano_filtro)
        saidas = saidas.filter(data_vencimento__year=ano_filtro)
    
    if tipo_filtro == 'entrada':
        saidas = saidas.none()
    elif tipo_filtro == 'saida':
        entradas = entradas.none()
    
    if conta_filtro and conta_filtro != 'todas':
        entradas = entradas.filter(conta_bancaria_id=conta_filtro)
        saidas = saidas.filter(conta_bancaria_id=conta_filtro)
    
    # Paginação
    todas_transacoes = sorted(
        list(entradas) + list(saidas),
        key=lambda x: x.data if hasattr(x, 'data') else x.data_vencimento,
        reverse=True
    )
    
    paginator = Paginator(todas_transacoes, 25)
    page_number = request.GET.get('page')
    transacoes_paginadas = paginator.get_page(page_number)
    
    # Cálculos totais
    total_entradas = entradas.aggregate(total=Sum('valor'))['total'] or 0
    total_saidas = saidas.aggregate(total=Sum('valor'))['total'] or 0
    saldo_mes = total_entradas - total_saidas
    
    # Cálculo da variação mensal
    mes_para_calculo = int(mes_filtro) if mes_filtro and mes_filtro != 'todos' else mes_atual
    ano_para_calculo = int(ano_filtro) if ano_filtro and ano_filtro != 'todos' else ano_atual
    
    if mes_filtro and mes_filtro != 'todos':
        mes_anterior = mes_para_calculo - 1 if mes_para_calculo > 1 else 12
        ano_mes_anterior = ano_para_calculo if mes_para_calculo > 1 else ano_para_calculo - 1
        
        entradas_mes_anterior = Entrada.objects.filter(
            usuario=request.user,
            data__month=mes_anterior,
            data__year=ano_mes_anterior
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        saidas_mes_anterior = Saida.objects.filter(
            usuario=request.user,
            data_vencimento__month=mes_anterior,
            data_vencimento__year=ano_mes_anterior
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        saldo_mes_anterior = entradas_mes_anterior - saidas_mes_anterior
        
        if saldo_mes_anterior != 0:
            variacao_mensal = round((saldo_mes - saldo_mes_anterior) / abs(saldo_mes_anterior) * 100, 2)
        else:
            variacao_mensal = 100 if saldo_mes > 0 else 0
    else:
        variacao_mensal = 0
    
    mes_nome = dict(meses).get(int(mes_filtro) if mes_filtro and mes_filtro != 'todos' else mes_atual, 'Todos os meses' if mes_filtro == 'todos' else '')
    
    # Obter anos disponíveis a partir das transações
    anos_entradas = Entrada.objects.filter(usuario=request.user).dates('data', 'year')
    anos_saidas = Saida.objects.filter(usuario=request.user).dates('data_vencimento', 'year')
    anos_disponiveis = sorted(set([d.year for d in anos_entradas] + [d.year for d in anos_saidas]), reverse=True)
    
    if not anos_disponiveis:
        anos_disponiveis = [ano_atual]
    
    return render(request, 'core/extrato_completo.html', {
        'transacoes': transacoes_paginadas,
        'meses': meses,
        'anos_disponiveis': anos_disponiveis,
        'contas_usuario': contas_usuario,
        'contas_bancarias': contas_bancarias,  # ADICIONE ESTA LINHA
        'ano_selecionado': ano_filtro,
        'mes_selecionado': mes_filtro,
        'conta_selecionada': conta_filtro,
        'tipo_filtro': tipo_filtro,
        'total_entradas': total_entradas,
        'total_saidas': total_saidas,
        'saldo_mes': saldo_mes,
        'variacao_mensal': variacao_mensal,
        'mes_atual_nome': mes_nome,
        'ano_atual': ano_para_calculo,
    })

# core/views_extrato.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q, Sum
from datetime import datetime, timedelta
from decimal import Decimal
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .models import ContaBancaria, Entrada, Saida
from dateutil.relativedelta import relativedelta
from datetime import date
from decimal import Decimal


@login_required
def modal_selecao_extrato(request):
    """Retorna o modal de seleção para extrato bancário"""
    contas_bancarias = ContaBancaria.objects.filter(proprietario=request.user, ativa=True)
    
    context = {
        'contas_bancarias': contas_bancarias
    }
    
    return render(request, 'core/modal_extrato_bancario.html', context)




from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import ContaBancaria, Entrada, Saida
from django.db.models import Sum
import json

@login_required
def gerar_extrato_bancario_pdf(request):
    """Gera extrato bancário em PDF usando template HTML + xhtml2pdf"""
    print("DEBUG: View acessada - Método:", request.method)
    
    if request.method == 'GET':
        conta_id = request.GET.get('conta')
        periodo = request.GET.get('periodo', '30')
        
        print(f"DEBUG: Parâmetros - Conta ID: {conta_id}, Período: {periodo}")
        
        if not conta_id:
            print("DEBUG: Nenhuma conta selecionada")
            return JsonResponse({'success': False, 'error': 'Nenhuma conta selecionada'})
        
        try:
            conta = get_object_or_404(ContaBancaria, id=conta_id, proprietario=request.user)
            print(f"DEBUG: Conta encontrada: {conta}")
        except Exception as e:
            print(f"DEBUG: Erro ao buscar conta: {e}")
            return JsonResponse({'success': False, 'error': 'Conta não encontrada'})
        
        # Calcular datas baseadas no período selecionado
        data_fim = timezone.now().date()
        dias = int(periodo)
        data_inicio = data_fim - timedelta(days=dias)
        
        print(f"DEBUG: Período: {data_inicio} a {data_fim}")
        
        # Buscar transações do período
        entradas = Entrada.objects.filter(
            conta_bancaria__proprietario=request.user,
            conta_bancaria=conta,
            data__range=[data_inicio, data_fim]
        ).order_by('data')
        
        saidas = Saida.objects.filter(
            usuario=request.user,
            conta_bancaria=conta,
            data_vencimento__range=[data_inicio, data_fim]
        ).order_by('data_vencimento')
        
        print(f"DEBUG: {entradas.count()} entradas, {saidas.count()} saídas encontradas")
        
        # Calcular totais do período
        total_entradas = entradas.aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        total_saidas = saidas.aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        # CORREÇÃO: Calcular saldo inicial (saldo na data de início do período)
        # 1. Saldo inicial da conta (quando foi criada)
        saldo_inicial_conta = conta.saldo_atual or Decimal('0.00')
        
        # 2. Entradas que ocorreram ANTES do período do extrato
        entradas_anteriores = Entrada.objects.filter(
            conta_bancaria__proprietario=request.user,
            conta_bancaria=conta,
            data__lt=data_inicio  # APENAS transações anteriores à data de início
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        # 3. Saídas que ocorreram ANTES do período do extrato
        saidas_anteriores = Saida.objects.filter(
            usuario=request.user,
            conta_bancaria=conta,
            data_vencimento__lt=data_inicio  # APENAS transações anteriores à data de início
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        # 4. Saldo na data de início = saldo inicial + entradas anteriores - saídas anteriores
        saldo_inicial = saldo_inicial_conta + entradas_anteriores - saidas_anteriores
        
        print(f"DEBUG: Saldo inicial da conta: {saldo_inicial_conta}")
        print(f"DEBUG: Entradas anteriores ao período: {entradas_anteriores}")
        print(f"DEBUG: Saídas anteriores ao período: {saidas_anteriores}")
        print(f"DEBUG: Saldo na data de início: {saldo_inicial}")
        
        # Preparar dados para o template
        transacoes = []
        saldo_acumulado = float(saldo_inicial)
        
        # Combinar e ordenar todas as transações
        todas_transacoes = []
        
        for entrada in entradas:
            todas_transacoes.append({
                'data': entrada.data,
                'nome': entrada.nome,
                'valor': float(entrada.valor),
                'tipo': 'Entrada',
                'categoria': entrada.forma_recebimento,
                'saldo_acumulado': None
            })
        
        for saida in saidas:
            todas_transacoes.append({
                'data': saida.data_vencimento,
                'nome': saida.nome,
                'valor': float(saida.valor),
                'tipo': 'Saida',
                'categoria': saida.categoria if saida.categoria else 'Outros',
                'saldo_acumulado': None
            })
        
        # Ordenar por data e calcular saldo acumulado
        todas_transacoes.sort(key=lambda x: x['data'])
        
        for transacao in todas_transacoes:
            if transacao['tipo'] == 'Entrada':
                saldo_acumulado += transacao['valor']
            else:
                saldo_acumulado -= transacao['valor']
            
            transacao['saldo_acumulado'] = saldo_acumulado
            transacoes.append(transacao)
        
        # Saldo final deve ser o último saldo acumulado
        saldo_final = saldo_acumulado
        
        context = {
            'usuario': request.user,
            'conta': conta,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'periodo': f"{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}",
            'transacoes': transacoes,
            'total_entradas': float(total_entradas),
            'total_saidas': float(total_saidas),
            'saldo_inicial': float(saldo_inicial),
            'saldo_final': float(saldo_final),
            'data_geracao': timezone.now(),
        }
        
        try:
            # Renderizar template HTML
            html_string = render_to_string('core/extrato_pdf.html', context)
            
            # Criar buffer para o PDF
            result = BytesIO()
            
            # Converter HTML para PDF
            pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
            
            if not pdf.err:
                # Retornar PDF como resposta
                response = HttpResponse(result.getvalue(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="extrato_{conta.get_nome_banco_display()}_{data_inicio}_{data_fim}.pdf"'
                return response
            else:
                return JsonResponse({'success': False, 'error': 'Erro ao gerar PDF'})
            
        except Exception as e:
            print(f"DEBUG: Erro ao gerar PDF: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': f'Erro ao gerar PDF: {str(e)}'})
    
    print("DEBUG: Método não permitido")
    return JsonResponse({'success': False, 'error': 'Método não permitido'})


def get_saldo_historico(usuario, meses=12):
    historico_saldo = []
    labels = []
    today = date.today()

    for i in range(meses -1, -1, -1):
        target_date = today - relativedelta(months=i)
        
        first_day_of_month = target_date.replace(day=1)
        last_day_of_month = (first_day_of_month + relativedelta(months=1)) - timedelta(days=1)

        entradas_ate_mes = get_sum(
            Entrada.objects.filter(
                usuario=usuario,
                data__lte=last_day_of_month
            )
        )
        
        saidas_ate_mes = get_sum(
            Saida.objects.filter(
                usuario=usuario,
                data_vencimento__lte=last_day_of_month
            )
        )
        
        saldo_mensal = entradas_ate_mes - saidas_ate_mes
        historico_saldo.append(float(saldo_mensal))
        labels.append(f"{target_date.month:02d}/{target_date.year}")
    
    return labels, historico_saldo

def get_transacoes_recentes(usuario, limite=5):
    ultimas_entradas = Entrada.objects.filter(usuario=usuario).order_by('-data')[:limite]
    ultimas_saidas = Saida.objects.filter(usuario=usuario).order_by('-data_vencimento')[:limite]

    transacoes = sorted(
        list(ultimas_entradas) + list(ultimas_saidas),
        key=lambda x: x.data if hasattr(x, 'data') else x.data_vencimento,
        reverse=True
    )[:limite]

    formatted_transacoes = []
    for t in transacoes:
        if hasattr(t, 'data'):
            formatted_transacoes.append({
                'tipo': 'Entrada',
                'nome': t.nome,
                'valor': float(t.valor),
                'data': t.data.strftime('%d/%m/%Y'),
                'conta': t.conta_bancaria.get_nome_banco_display(),
            })
        else:
            formatted_transacoes.append({
                'tipo': 'Saída',
                'nome': t.nome,
                'valor': float(t.valor),
                'data': t.data_vencimento.strftime('%d/%m/%Y'),
                'conta': t.conta_bancaria.get_nome_banco_display(),
            })
    return formatted_transacoes

def get_saldo_por_tipo_conta(usuario):
    saldo_por_tipo = {}
    
    for tipo_code, tipo_display in ContaBancaria.TIPO_CONTA_CHOICES:
        contas_desse_tipo = ContaBancaria.objects.filter(proprietario=usuario, tipo=tipo_code)
        
        saldo_total_tipo = Decimal('0.00')
        for conta in contas_desse_tipo:
            entradas_conta = get_sum(Entrada.objects.filter(usuario=usuario, conta_bancaria=conta))
            saidas_conta = get_sum(Saida.objects.filter(usuario=usuario, conta_bancaria=conta))
            
            if tipo_code == 'credito':
                saldo_conta = -saidas_conta
            else:
                saldo_conta = (conta.saldo_atual or Decimal('0.00')) + entradas_conta - saidas_conta
            
            saldo_total_tipo += saldo_conta
        
        if saldo_total_tipo != Decimal('0.00'):
            saldo_por_tipo[tipo_display] = float(saldo_total_tipo)
            
    return saldo_por_tipo


def get_entradas_por_forma_recebimento(usuario):
    entradas_por_forma = Entrada.objects.filter(usuario=usuario).values('forma_recebimento').annotate(total=Sum('valor'))

    labels = []
    values = []
    
    for item in entradas_por_forma:
        display_name = next((name for code, name in Entrada.FORMA_RECEBIMENTO_CHOICES if code == item['forma_recebimento']), item['forma_recebimento'])
        labels.append(display_name)
        values.append(float(item['total']))

    return {'labels': labels, 'data': values}


# views.py
from django.http import JsonResponse
from django.template.loader import render_to_string

@login_required
def transacao_detalhes(request, pk):
    try:
        # Tenta encontrar como Entrada primeiro
        try:
            transacao = Entrada.objects.get(pk=pk, usuario=request.user)
            tipo = 'Entrada'
        except Entrada.DoesNotExist:
            transacao = Saida.objects.get(pk=pk, usuario=request.user)
            tipo = 'Saida'
        
        context = {
            'transacao': transacao,
            'tipo': tipo
        }
        
        html = render_to_string('core/includes/transacao_detalhes_modal.html', context, request=request)
        return JsonResponse({'success': True, 'html': html})
        
    except (Entrada.DoesNotExist, Saida.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'Transação não encontrada'})

@login_required
def marcar_como_pago(request, pk):
    try:
        saida = Saida.objects.get(pk=pk, usuario=request.user)
        
        if saida.situacao != 'pago':
            saida.situacao = 'pago'
            saida.data_lancamento = timezone.now().date()
            saida.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'Transação marcada como paga com sucesso!'
            })
        else:
            return JsonResponse({
                'success': False, 
                'message': 'Esta transação já está paga'
            })
            
    except Saida.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Transação não encontrada'})



# ================================================================
# VIEWS DE SALDO ATUAL
# ================================================================


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import json
from decimal import Decimal

from .choices import TIPO_CONTA_CHOICES, BANCO_CHOICES  # Importar do choices.py

@login_required
def saldo_atual(request):
    try:
        user = request.user
        hoje = date.today()
        
        # Obter contas do usuário
        contas = ContaBancaria.objects.filter(proprietario=user)
        
        # Inicializar variáveis de saldo
        saldo_geral = Decimal('0.00')
        saldo_disponivel = Decimal('0.00')
        saldo_total_cartoes_credito = Decimal('0.00')
        saldo_total_contas_corrente = Decimal('0.00')
        saldo_total_contas_poupanca = Decimal('0.00')
        saldo_total_investimento = Decimal('0.00')
        total_ativos = Decimal('0.00')
        total_dividas = Decimal('0.00')
        
        # Calcular saldos por conta e agregar totais
        for conta in contas:
            saldo_conta = conta.saldo_atual or Decimal('0.00')
            saldo_geral += saldo_conta
            
            if conta.ativa:
                saldo_disponivel += saldo_conta
                
                if conta.tipo == 'credito':
                    saldo_total_cartoes_credito += saldo_conta
                    if saldo_conta < 0:
                        total_dividas += abs(saldo_conta)
                elif conta.tipo == 'corrente':
                    saldo_total_contas_corrente += saldo_conta
                    if saldo_conta > 0:
                        total_ativos += saldo_conta
                elif conta.tipo == 'poupanca':
                    saldo_total_contas_poupanca += saldo_conta
                    if saldo_conta > 0:
                        total_ativos += saldo_conta
                elif conta.tipo == 'investimento':
                    saldo_total_investimento += saldo_conta
                    if saldo_conta > 0:
                        total_ativos += saldo_conta
        
        # Calcular entradas e saídas do mês atual
        primeiro_dia_mes = hoje.replace(day=1)
        proximo_mes = primeiro_dia_mes + relativedelta(months=1)
        ultimo_dia_mes = proximo_mes - timedelta(days=1)
        
        entradas_mes_atual = Entrada.objects.filter(
            conta_bancaria__proprietario=user,
            data__range=(primeiro_dia_mes, ultimo_dia_mes)
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        saidas_mes_atual = Saida.objects.filter(
            conta_bancaria__proprietario=user,
            data_vencimento__range=(primeiro_dia_mes, ultimo_dia_mes)
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        fluxo_mensal = entradas_mes_atual - saidas_mes_atual
        
        # Calcular médias dos últimos 3 meses para uma visão mais realista
        tres_meses_atras = hoje - relativedelta(months=3)
        
        # Despesas médias mensais (últimos 3 meses)
        despesas_ultimos_tres_meses = Saida.objects.filter(
            conta_bancaria__proprietario=user,
            data_vencimento__range=(tres_meses_atras, hoje)
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        despesas_mensais_medias = despesas_ultimos_tres_meses / Decimal('3.00')
        
        # Receitas médias mensais (últimos 3 meses)
        receitas_ultimos_tres_meses = Entrada.objects.filter(
            conta_bancaria__proprietario=user,
            data__range=(tres_meses_atras, hoje)
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        receitas_mensais_medias = receitas_ultimos_tres_meses / Decimal('3.00')
        
        # Calcular taxa de economia
        if receitas_mensais_medias > 0:
            taxa_economia = (fluxo_mensal / receitas_mensais_medias * 100)
        else:
            taxa_economia = Decimal('0.00')
        
        # Calcular reserva de emergência e meses de cobertura
        reserva_emergencia = saldo_total_contas_corrente + saldo_total_contas_poupanca
        
        if despesas_mensais_medias > 0:
            meses_reserva = reserva_emergencia / despesas_mensais_medias
        else:
            meses_reserva = Decimal('0.00')
        
        patrimonio_liquido = saldo_geral
        
        # Preparar dados para gráficos
        distribuicao_labels = []
        distribuicao_values = []
        
        if saldo_total_contas_corrente > 0:
            distribuicao_labels.append('Conta Corrente')
            distribuicao_values.append(float(saldo_total_contas_corrente))
        
        if saldo_total_contas_poupanca > 0:
            distribuicao_labels.append('Poupança')
            distribuicao_values.append(float(saldo_total_contas_poupanca))

        if saldo_total_investimento > 0:
            distribuicao_labels.append('Investimentos')
            distribuicao_values.append(float(saldo_total_investimento))
        
        if saldo_total_cartoes_credito < 0:
            distribuicao_labels.append('Dívidas Cartão')
            distribuicao_values.append(float(abs(saldo_total_cartoes_credito)))
        
        # Dados para evolução do patrimônio (6 meses - simulado)
        evolucao_patrimonio = []
        patrimonio_base = float(patrimonio_liquido)
        
        for i in range(6):
            mes_anterior = hoje - relativedelta(months=5 - i)
            # Simular crescimento/queda baseado no fluxo mensal
            crescimento_mensal = float(fluxo_mensal) * 0.8  # 80% do fluxo vira patrimônio
            valor_mes = patrimonio_base + (crescimento_mensal * (5 - i))
            evolucao_patrimonio.append({
                'mes': mes_anterior.strftime('%b/%y'),
                'valor': round(max(valor_mes, 0), 2)  # Não deixar negativo
            })
        
        # Contexto
        context = {
            'saldo_geral': saldo_geral,
            'saldo_disponivel': saldo_disponivel,
            'entradas_mes': entradas_mes_atual,
            'saidas_mes': saidas_mes_atual,
            'fluxo_mensal': fluxo_mensal,
            'patrimonio_liquido': patrimonio_liquido,
            'reserva_emergencia': reserva_emergencia,
            'meses_reserva': float(meses_reserva),
            'despesas_mensais_medias': float(despesas_mensais_medias),
            'receitas_mensais_medias': float(receitas_mensais_medias),
            'taxa_economia': float(taxa_economia),
            'total_dividas': float(total_dividas),
            'total_ativos': float(total_ativos),
            'contas': contas,
            'tipos_conta': TIPO_CONTA_CHOICES,  # Usar a importação correta
            'evolucao_patrimonio': json.dumps(evolucao_patrimonio),
            'distribuicao_labels': json.dumps(distribuicao_labels),
            'distribuicao_values': json.dumps(distribuicao_values),
        }
        
        return render(request, 'core/saldo_atual.html', context)
        
    except Exception as e:
        print(f"Erro em saldo_atual: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Contexto de fallback
        context = {
            'saldo_geral': Decimal('0.00'),
            'saldo_disponivel': Decimal('0.00'),
            'entradas_mes': Decimal('0.00'),
            'saidas_mes': Decimal('0.00'),
            'fluxo_mensal': Decimal('0.00'),
            'patrimonio_liquido': Decimal('0.00'),
            'reserva_emergencia': Decimal('0.00'),
            'meses_reserva': 0.0,
            'despesas_mensais_medias': 0.0,
            'receitas_mensais_medias': 0.0,
            'taxa_economia': 0.0,
            'total_dividas': 0.0,
            'total_ativos': 0.0,
            'contas': ContaBancaria.objects.filter(proprietario=request.user),
            'tipos_conta': TIPO_CONTA_CHOICES,  # Usar a importação correta aqui também
            'evolucao_patrimonio': json.dumps([]),
            'distribuicao_labels': json.dumps([]),
            'distribuicao_values': json.dumps([]),
        }
        
        return render(request, 'core/saldo_atual.html', context)



@login_required
@require_GET
def financial_insights_api(request):
    try:
        user = request.user
        hoje = date.today()
        
        # Obter contas do usuário
        contas = ContaBancaria.objects.filter(proprietario=user)
        
        # Calcular saldos
        saldo_geral = sum((conta.saldo_atual or Decimal('0.00') for conta in contas))
        
        # Calcular entradas e saídas do mês
        primeiro_dia_mes = hoje.replace(day=1)
        ultimo_dia_mes = (primeiro_dia_mes + relativedelta(months=1)) - timedelta(days=1)
        
        entradas_mes = Entrada.objects.filter(
            conta_bancaria__proprietario=user,
            data__range=(primeiro_dia_mes, ultimo_dia_mes)
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        saidas_mes = Saida.objects.filter(
            conta_bancaria__proprietario=user,
            data_vencimento__range=(primeiro_dia_mes, ultimo_dia_mes)
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        fluxo_mensal = entradas_mes - saidas_mes
        
        # Calcular despesas médias dos últimos 3 meses para reserva mais realista
        tres_meses_atras = hoje - relativedelta(months=3)
        despesas_ultimos_tres_meses = Saida.objects.filter(
            conta_bancaria__proprietario=user,
            data_vencimento__range=(tres_meses_atras, hoje)
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        despesas_mensais_medias = despesas_ultimos_tres_meses / Decimal('3.00')
        
        # Calcular reserva de emergência (contas corrente + poupança)
        reserva_emergencia = sum((conta.saldo_atual or Decimal('0.00') 
                                 for conta in contas 
                                 if conta.tipo in ['corrente', 'poupanca'] and conta.ativa))
        
        # Calcular meses de reserva com base nas despesas médias
        if despesas_mensais_medias > 0:
            meses_reserva = reserva_emergencia / despesas_mensais_medias
        else:
            meses_reserva = Decimal('0.00')
        
        # Calcular taxa de economia
        if entradas_mes > 0:
            taxa_economia = (fluxo_mensal / entradas_mes * 100)
        else:
            taxa_economia = Decimal('0.00')
        
        # Gerar insights
        insights = []
        tags = []
        
        # Insight 1: Reserva de emergência
        if meses_reserva < 3:
            insights.append(f"⚠️ Sua reserva de emergência cobre apenas {meses_reserva:.1f} meses de despesas. A meta recomendada é 3-6 meses.")
            tags.append("Reserva Baixa")
        elif meses_reserva >= 6:
            insights.append(f"✅ Excelente! Sua reserva de emergência cobre {meses_reserva:.1f} meses de despesas.")
            tags.append("Reserva OK")
        else:
            insights.append(f"📈 Sua reserva cobre {meses_reserva:.1f} meses. Continue construindo para atingir 6 meses.")
            tags.append("Reserva em Construção")
        
        # Insight 2: Taxa de economia
        if taxa_economia < 10:
            insights.append(f"📉 Sua taxa de economia é de {taxa_economia:.1f}%. Tente economizar pelo menos 10-15% da sua renda.")
            tags.append("Economia Baixa")
        elif taxa_economia >= 20:
            insights.append(f"🚀 Parabéns! Sua taxa de economia é de {taxa_economia:.1f}%, acima da média.")
            tags.append("Economia Alta")
        else:
            insights.append(f"📊 Sua taxa de economia é de {taxa_economia:.1f}%. Continue assim!")
            tags.append("Economia Boa")
        
        # Insight 3: Fluxo mensal
        if fluxo_mensal < 0:
            insights.append(f"🔴 Atenção: Seu fluxo mensal é negativo (-R$ {abs(float(fluxo_mensal)):.2f}). Reveja suas despesas.")
            tags.append("Fluxo Negativo")
        else:
            insights.append(f"🟢 Seu fluxo mensal é positivo (+R$ {float(fluxo_mensal):.2f}). Bom trabalho!")
            tags.append("Fluxo Positivo")
        
        # Meta do mês (15% da renda)
        meta_mensal = entradas_mes * Decimal('0.15')
        progresso_meta = min((fluxo_mensal / meta_mensal * 100) if meta_mensal > 0 else 0, 100)
        
        return JsonResponse({
            'success': True,
            'insights': insights,
            'tags': tags[:3],
            'monthly_goal': float(meta_mensal),
            'goal_progress': float(progresso_meta),
            'emergency_months': float(meses_reserva),
            'savings_rate': float(taxa_economia)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao gerar insights: {str(e)}'
        })
# ================================================================
# VIEWS DA PARTE DE TRANSFERÊNCIAS
# ================================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal
import json

from .models import  Transferencia
from .forms import TransferenciaForm


# views.py - Atualize a view transferencia_list

# views.py - Views atualizadas
@login_required
def transferencia_list(request):
    # Obter parâmetros de filtro da URL
    ano_selecionado = request.GET.get('ano', '')
    mes_selecionado = request.GET.get('mes', '')
    
    # Definir data atual como padrão se não houver filtros
    today = date.today()
    year = int(ano_selecionado) if ano_selecionado and ano_selecionado.isdigit() else today.year
    month = int(mes_selecionado) if mes_selecionado and mes_selecionado.isdigit() else today.month

    try:
        start_date = date(year, month, 1)
        end_date = start_date + relativedelta(months=1) - timedelta(days=1)
    except ValueError:
        start_date = date(today.year, today.month, 1)
        end_date = start_date + relativedelta(months=1) - timedelta(days=1)

    user = request.user
    
    # Aplicar filtros
    transferencias_qs = Transferencia.objects.filter(usuario=user)
    
    if ano_selecionado:
        transferencias_qs = transferencias_qs.filter(data__year=year)
    if mes_selecionado:
        transferencias_qs = transferencias_qs.filter(data__month=month)
    
    transferencias = transferencias_qs.order_by('-data', '-data_criacao')
    
    contas = ContaBancaria.objects.filter(proprietario=user, ativa=True)

    # Cálculos totais
    total_transferencias = transferencias.aggregate(total_valor=Sum('valor'))['total_valor'] or Decimal('0.00')
    
    count_transferencias = transferencias.count()
    media_transferencias = total_transferencias / count_transferencias if count_transferencias > 0 else Decimal('0.00')

    maior_transferencia = transferencias.order_by('-valor').first()
    
    # Calcular saldos das contas
    saldos_contas = get_saldos_contas(user)
    
    # Preparar dados para os filtros
    meses_choices = [
        ('01', 'Janeiro'), ('02', 'Fevereiro'), ('03', 'Março'), ('04', 'Abril'),
        ('05', 'Maio'), ('06', 'Junho'), ('07', 'Julho'), ('08', 'Agosto'),
        ('09', 'Setembro'), ('10', 'Outubro'), ('11', 'Novembro'), ('12', 'Dezembro')
    ]
    
    # Anos disponíveis (baseados nas transferências existentes)
    anos_disponiveis = list(Transferencia.objects.filter(
        usuario=user
    ).dates('data', 'year').values_list('data__year', flat=True).distinct())
    
    # Se não houver anos, adicionar o ano atual
    if not anos_disponiveis:
        anos_disponiveis = [today.year]
    else:
        anos_disponiveis = sorted(anos_disponiveis, reverse=True)
    
    # Mapeamento para exibição dos badges
    meses_display_map = {k: v for k, v in meses_choices}
    
    context = {
        'transfers': transferencias,
        'contas': contas,
        'mes_atual_nome': start_date.strftime('%B').capitalize(),
        'ano_atual': start_date.year,
        'total_transferencias': total_transferencias,
        'media_transferencias': media_transferencias,
        'maior_transferencia': maior_transferencia,
        'saldos_contas': saldos_contas,
        'meses': meses_choices,
        'anos_disponiveis': anos_disponiveis,
        'mes_selecionado': mes_selecionado,
        'ano_selecionado': ano_selecionado,
        'meses_display_map': meses_display_map,
    }
    
    return render(request, 'core/transferencia_list.html', context)

@login_required
@transaction.atomic
def transferencia_create(request):
    if request.method == 'POST':
        form = TransferenciaForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                # Criar a transferência (o save() já atualiza os saldos)
                transferencia = form.save(commit=False)
                transferencia.usuario = request.user
                transferencia.save()
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'message': 'Transferência criada com sucesso!'})
                else:
                    messages.success(request, 'Transferência criada com sucesso!')
                    return redirect('core:transferencia_list')
                    
            except ValidationError as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'errors': {'__all__': [str(e)]}})
                else:
                    messages.error(request, str(e))
                    return redirect('core:transferencia_list')
                    
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
            else:
                messages.error(request, 'Ocorreu um erro ao criar a transferência. Verifique os dados.')
                return redirect('core:transferencia_list')

    return redirect('core:transferencia_list')

@login_required
@transaction.atomic
def transferencia_update(request, pk):
    transferencia = get_object_or_404(Transferencia, pk=pk, usuario=request.user)

    if request.method == 'POST':
        form = TransferenciaForm(request.POST, user=request.user, instance=transferencia)
        if form.is_valid():
            try:
                # Obter dados antigos ANTES de modificar
                conta_origem_antiga = transferencia.conta_origem
                conta_destino_antiga = transferencia.conta_destino
                valor_antigo = transferencia.valor

                # Obter novos dados
                conta_origem_nova = form.cleaned_data['conta_origem']
                conta_destino_nova = form.cleaned_data['conta_destino']
                valor_novo = form.cleaned_data['valor']

                # REVERTER: Adicionar valor antigo às contas originais
                conta_origem_antiga.saldo_atual += valor_antigo
                conta_destino_antiga.saldo_atual -= valor_antigo
                
                # Verificar saldo suficiente na nova conta
                if conta_origem_nova.saldo_atual < valor_novo:
                    raise ValidationError('Saldo insuficiente na conta de origem.')
                
                # APLICAR NOVO: Subtrair novo valor da nova conta de origem
                conta_origem_nova.saldo_atual -= valor_novo
                conta_destino_nova.saldo_atual += valor_novo
                
                # Salvar todas as contas
                conta_origem_antiga.save()
                conta_destino_antiga.save()
                conta_origem_nova.save()
                conta_destino_nova.save()

                # Atualizar a transferência
                transferencia = form.save()

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'message': 'Transferência atualizada com sucesso!'})
                else:
                    messages.success(request, 'Transferência atualizada com sucesso!')
                    return redirect('core:transferencia_list')
                    
            except ValidationError as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'errors': {'__all__': [str(e)]}})
                else:
                    messages.error(request, str(e))
                    return redirect('core:transferencia_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
            else:
                messages.error(request, 'Ocorreu um erro ao atualizar a transferência.')
                return redirect('core:transferencia_list')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)
    
    form = TransferenciaForm(user=request.user, instance=transferencia)
    context = {
        'form': form,
        'transferencia': transferencia,
        'page_title': 'Editar Transferência'
    }
    return render(request, 'core/transferencia_form.html', context)

@login_required
@transaction.atomic
def transferencia_delete(request, pk):
    transferencia = get_object_or_404(Transferencia, pk=pk, usuario=request.user)

    if request.method == 'POST':
        try:
            # Reverter os saldos ANTES de deletar
            conta_origem = transferencia.conta_origem
            conta_destino = transferencia.conta_destino
            valor = transferencia.valor

            conta_origem.saldo_atual += valor
            conta_destino.saldo_atual -= valor
            
            # Salvar as contas primeiro
            conta_origem.save()
            conta_destino.save()
            
            # Depois deletar a transferência
            transferencia.delete()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Transferência excluída com sucesso!'})
            else:
                messages.success(request, 'Transferência excluída com sucesso!')
                return redirect('core:transferencia_list')

        except Exception as e:
            error_message = f'Erro ao excluir: {e}'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': error_message}, status=500)
            else:
                messages.error(request, error_message)
                return redirect('core:transferencia_list')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)
    
    return render(request, 'core/transferencia_confirm_delete.html', {'transferencia': transferencia})

def custom_logout(request):
    """View personalizada para logout com mensagem"""
    logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('core:login')

# ================================================================
# VIEWS DA PROFILE (CORRIGIDAS)
# ================================================================

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile, UserActivity, UserLogin  # Importações corrigidas

import os
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST


@login_required
@transaction.atomic
def profile_update_view(request):
    # Obter ou criar o perfil do usuário
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        
        if u_form.is_valid() and p_form.is_valid():
            # Verificar se uma nova foto foi enviada
            if 'foto_perfil' in request.FILES:
                # Deletar a imagem antiga se existir
                if profile.foto_perfil and profile.foto_perfil.name != 'default.jpg':
                    try:
                        old_profile = Profile.objects.get(pk=profile.pk)
                        if (old_profile.foto_perfil and 
                            old_profile.foto_perfil.name != 'default.jpg' and 
                            old_profile.foto_perfil.name != profile.foto_perfil.name):
                            if os.path.isfile(old_profile.foto_perfil.path):
                                os.remove(old_profile.foto_perfil.path)
                    except Exception as e:
                        print(f"Erro ao deletar imagem antiga: {e}")
            
            u_form.save()
            p_form.save()
            
            # Processar tema se enviado via AJAX
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                theme = request.POST.get('theme')
                if theme in ['light', 'dark', 'auto']:
                    profile.theme = theme
                    profile.save()
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Preferências salvas com sucesso!'
                })
            
            messages.success(request, 'Seu perfil foi atualizado com sucesso!')
            return redirect('core:profile_update_view')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors = {}
                if u_form.errors:
                    errors.update(u_form.errors.get_json_data())
                if p_form.errors:
                    errors.update(p_form.errors.get_json_data())
                return JsonResponse({
                    'success': False, 
                    'errors': errors
                }, status=400)
            
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)
    
    return render(request, 'core/profile_update.html', {
        'u_form': u_form,
        'p_form': p_form,
        'profile': profile  # Adicionar profile ao contexto
    })

@login_required
@require_POST
def password_change_view(request):
    """View para alteração de senha"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Atualizar a data da última alteração de senha
            request.user.profile.password_updated_at = timezone.now()
            request.user.profile.save()
            
            update_session_auth_hash(request, user)  # Manter o usuário logado
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'message': 'Senha alterada com sucesso!',
                    'password_updated_at': request.user.profile.password_updated_at.strftime('%d/%m/%Y %H:%M') if request.user.profile.password_updated_at else 'Nunca'
                })
            messages.success(request, 'Senha alterada com sucesso!')
            return redirect('core:profile_update_view')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors.get_json_data()}, status=400)
            messages.error(request, 'Erro ao alterar a senha.')
    return redirect('core:profile_update_view')


@login_required
def delete_account(request):
    if request.method == 'POST':
        confirm_text = request.POST.get('confirm_text', '')
        
        if confirm_text.upper() != 'EXCLUIR':
            messages.error(request, 'Confirmação incorreta. Digite "EXCLUIR" para confirmar.')
            return redirect('core:delete_account')
        
        try:
            user = request.user
            # Logout antes de deletar
            from django.contrib.auth import logout
            logout(request)
            user.delete()
            messages.success(request, 'Sua conta foi excluída com sucesso.')
            return redirect('core:home')
        except Exception as e:
            messages.error(request, f'Erro ao excluir conta: {str(e)}')
            return redirect('core:profile_update_view')
    
    return render(request, 'core/confirm_delete_account.html')


@login_required
@require_POST
def remove_profile_photo(request):
    """View para remover foto de perfil"""
    try:
        profile = request.user.profile
        if profile.foto_perfil and profile.foto_perfil.name != 'default.jpg':
            # Deleta o arquivo físico
            if os.path.isfile(profile.foto_perfil.path):
                os.remove(profile.foto_perfil.path)
            # Reseta para a imagem padrão
            profile.foto_perfil = 'default.jpg'
            profile.save()
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Foto de perfil removida com sucesso.'})
            messages.success(request, 'Foto de perfil removida com sucesso.')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Você já está usando a foto padrão.'})
            messages.info(request, 'Você já está usando a foto padrão.')
            
    except Exception as e:
        error_msg = f'Erro ao remover foto: {str(e)}'
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': error_msg})
        messages.error(request, error_msg)
    
    return redirect('core:profile_update_view')


@login_required
def track_login(request):
    """Registrar login do usuário"""
    try:
        user_profile = request.user.profile
        user_profile.update_login_streak()
        
        # Registrar login
        UserLogin.objects.create(
            user=request.user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Registrar atividade
        UserActivity.objects.create(
            user=request.user,
            activity_type='login',
            details={'ip': request.META.get('REMOTE_ADDR')}
        )
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
@require_POST
def update_profile_info(request):
    """View para atualizar informações do perfil"""
    user_form = UserUpdateForm(request.POST, instance=request.user)
    
    if user_form.is_valid():
        user_form.save()
        
        # Registrar atividade
        UserActivity.objects.create(
            user=request.user,
            activity_type='profile_update',
            details={'fields_updated': list(request.POST.keys())}
        )
        
        return JsonResponse({
            'success': True, 
            'message': 'Informações atualizadas com sucesso!',
            'profile_completion': request.user.profile.get_profile_completion()
        })
    
    return JsonResponse({'success': False, 'errors': user_form.errors.get_json_data()}, status=400)


@login_required
@require_POST
def update_profile_photo(request):
    """View para atualizar apenas a foto de perfil"""
    form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
    
    if form.is_valid():
        # Processar a imagem se fornecida
        if 'foto_perfil' in request.FILES:
            # Deletar a imagem antiga se existir
            if request.user.profile.foto_perfil and request.user.profile.foto_perfil.name != 'default.jpg':
                try:
                    if os.path.isfile(request.user.profile.foto_perfil.path):
                        os.remove(request.user.profile.foto_perfil.path)
                except Exception as e:
                    print(f"Erro ao deletar imagem antiga: {e}")
        
        form.save()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Foto de perfil atualizada com sucesso!'})
        messages.success(request, 'Foto de perfil atualizada com sucesso!')
    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors.get_json_data()}, status=400)
        messages.error(request, 'Erro ao atualizar a foto de perfil.')
    
    return redirect('core:profile_update_view')

from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

@login_required
def user_statistics(request):
    """API para fornecer dados de estatísticas do usuário"""
    try:
        user = request.user
        profile = user.profile
        
        logger.info(f"Processando estatísticas para usuário: {user.username}")
        
        # Estatísticas básicas
        statistics = {
            'total_logins': profile.total_logins or 0,
            'login_streak': profile.login_streak or 0,
            'last_login': user.last_login.strftime('%d/%m/%Y %H:%M') if user.last_login else 'Nunca',
            'account_age_days': (timezone.now().date() - user.date_joined.date()).days,
            'profile_completion': profile.get_profile_completion(),
            'last_password_change': profile.password_updated_at.strftime('%d/%m/%Y %H:%M') if profile.password_updated_at else 'Nunca',
            'weekly_logins': 0,  # Será calculado abaixo
        }
        
        # Atividade semanal (últimos 7 dias)
        weekly_activity = []
        today = timezone.now().date()
        
        # Se o modelo UserLogin não existir, use dados simulados
        try:
            from .models import UserLogin
            for i in range(6, -1, -1):  # Últimos 7 dias
                date = today - timedelta(days=i)
                login_count = UserLogin.objects.filter(
                    user=user,
                    login_time__date=date
                ).count()
                weekly_activity.append({
                    'day': date.strftime('%d/%m'),
                    'count': login_count
                })
                statistics['weekly_logins'] += login_count
        except Exception as e:
            logger.warning(f"Modelo UserLogin não disponível, usando dados simulados: {e}")
            # Dados simulados para demonstração
            for i in range(6, -1, -1):
                date = today - timedelta(days=i)
                weekly_activity.append({
                    'day': date.strftime('%d/%m'),
                    'count': i + 1  # Dados de exemplo
                })
                statistics['weekly_logins'] += (i + 1)
        
        # Atividades recentes
        recent_activities = []
        try:
            from .models import UserActivity
            activities = UserActivity.objects.filter(user=user).order_by('-timestamp')[:5]
            for activity in activities:
                recent_activities.append({
                    'type': activity.activity_type,
                    'title': get_activity_display(activity.activity_type),
                    'description': get_activity_description(activity.activity_type),
                    'time': activity.timestamp.strftime('%d/%m/%Y %H:%M'),
                    'icon': get_activity_icon(activity.activity_type),
                    'color': get_activity_color(activity.activity_type)
                })
        except Exception as e:
            logger.warning(f"Modelo UserActivity não disponível: {e}")
            # Atividades de exemplo
            recent_activities = [
                {
                    'type': 'login',
                    'title': 'Login realizado',
                    'description': 'Acesso ao sistema',
                    'time': timezone.now().strftime('%d/%m/%Y %H:%M'),
                    'icon': 'fas fa-sign-in-alt',
                    'color': 'blue'
                }
            ]
        
        # Conquistas
        achievements = [
            {
                'title': 'Primeira Semana',
                'description': '7 dias consecutivos de acesso',
                'icon': 'fas fa-calendar-check',
                'icon_bg': 'bg-green-100',
                'icon_color': 'text-green-600',
                'achieved': (profile.login_streak or 0) >= 7,
                'progress': min(100, ((profile.login_streak or 0) / 7) * 100)
            },
            {
                'title': 'Perfil Completo',
                'description': '100% do perfil preenchido',
                'icon': 'fas fa-user-check',
                'icon_bg': 'bg-blue-100',
                'icon_color': 'text-blue-600',
                'achieved': profile.get_profile_completion() == 100,
                'progress': profile.get_profile_completion()
            },
            {
                'title': 'Segurança Máxima',
                'description': 'Senha forte configurada',
                'icon': 'fas fa-shield-alt',
                'icon_bg': 'bg-purple-100',
                'icon_color': 'text-purple-600',
                'achieved': profile.password_updated_at is not None,
                'progress': 100 if profile.password_updated_at else 0
            },
        ]
        
        logger.info(f"Estatísticas processadas com sucesso para {user.username}")
        
        return JsonResponse({
            'success': True,
            'statistics': statistics,
            'weekly_activity': weekly_activity,
            'recent_activities': recent_activities,
            'achievements': achievements
        })
        
    except Exception as e:
        logger.error(f"Erro ao processar estatísticas: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': f'Erro ao obter estatísticas: {str(e)}'
        })

# Funções auxiliares para atividades
def get_activity_display(activity_type):
    activity_names = {
        'login': 'Login realizado',
        'password_change': 'Senha alterada',
        'profile_update': 'Perfil atualizado',
        'photo_change': 'Foto alterada',
    }
    return activity_names.get(activity_type, 'Atividade do sistema')

def get_activity_description(activity_type):
    descriptions = {
        'login': 'Acesso ao sistema',
        'password_change': 'Alteração de segurança',
        'profile_update': 'Informações pessoais atualizadas',
        'photo_change': 'Foto de perfil modificada',
    }
    return descriptions.get(activity_type, 'Atividade do usuário')

def get_activity_icon(activity_type):
    icons = {
        'login': 'fas fa-sign-in-alt',
        'password_change': 'fas fa-key',
        'profile_update': 'fas fa-user-edit',
        'photo_change': 'fas fa-camera',
    }
    return icons.get(activity_type, 'fas fa-history')

def get_activity_color(activity_type):
    colors = {
        'login': 'blue',
        'password_change': 'green',
        'profile_update': 'purple',
        'photo_change': 'yellow',
    }
    return colors.get(activity_type, 'gray')



# ================================================================
# VIEWS DA Lembrete
# ================================================================
   
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, Sum, Count, Case, When, Value, IntegerField
from django.db.models.functions import Coalesce
from datetime import datetime, timedelta
import json
from decimal import Decimal

from .models import Lembrete, Entrada, Saida
from .forms import LembreteForm


def get_mes_portugues(data):
    """Retorna o nome do mês em português"""
    meses = {
        1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
        5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
        9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
    }
    return meses.get(data.month, data.strftime('%B'))


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from datetime import datetime, timedelta, date
from decimal import Decimal
import json

from .models import Lembrete, Entrada, Saida

def get_mes_portugues(data):
    """Retorna o nome do mês em português"""
    meses = {
        1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
        5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
        9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
    }
    return meses.get(data.month, data.strftime('%B'))

@login_required
def lembrete_list(request):
    # Obter todos os parâmetros de filtro da URL
    status_filtro = request.GET.get('status', '')
    tipo_filtro = request.GET.get('tipo', '')
    periodo_filtro = request.GET.get('periodo', '30')
    order_filtro = request.GET.get('order', 'data_limite')
    data_inicial = request.GET.get('data_inicial', '')
    data_final = request.GET.get('data_final', '')
    search_query = request.GET.get('search', '')
    
    # Data atual para cálculos
    hoje = timezone.now().date()
    mes_atual_ptbr = f"{get_mes_portugues(hoje)} {hoje.year}"
    
    # BASE QUERYSETS
    # Lembretes do usuário
    lembretes = Lembrete.objects.filter(user=request.user)
    
    # Entradas do usuário
    entradas = Entrada.objects.filter(conta_bancaria__proprietario=request.user)
    
    # Saídas do usuário
    saidas = Saida.objects.filter(usuario=request.user)
    
    # APLICAR FILTROS NOS LEMBRETES
    if status_filtro:
        if status_filtro == 'pendente':
            lembretes = lembretes.filter(concluido=False)
        elif status_filtro == 'concluido':
            lembretes = lembretes.filter(concluido=True)
        elif status_filtro == 'urgente':
            data_limite_urgente = hoje + timedelta(days=2)
            lembretes = lembretes.filter(
                concluido=False,
                data_limite__lte=data_limite_urgente,
                data_limite__gte=hoje
            )
    
    if tipo_filtro and hasattr(Lembrete, 'tipo'):
        lembretes = lembretes.filter(tipo=tipo_filtro)
    
    if periodo_filtro != 'todos':
        if periodo_filtro == 'custom' and data_inicial and data_final:
            try:
                data_inicial_obj = datetime.strptime(data_inicial, '%Y-%m-%d').date()
                data_final_obj = datetime.strptime(data_final, '%Y-%m-%d').date()
                lembretes = lembretes.filter(data_limite__range=[data_inicial_obj, data_final_obj])
            except (ValueError, TypeError):
                data_inicio_periodo = hoje - timedelta(days=30)
                lembretes = lembretes.filter(data_limite__gte=data_inicio_periodo)
        else:
            try:
                dias = int(periodo_filtro)
                data_inicio_periodo = hoje - timedelta(days=dias)
                lembretes = lembretes.filter(data_limite__gte=data_inicio_periodo)
            except (ValueError, TypeError):
                data_inicio_periodo = hoje - timedelta(days=30)
                lembretes = lembretes.filter(data_limite__gte=data_inicio_periodo)
    
    if search_query:
        lembretes = lembretes.filter(
            Q(titulo__icontains=search_query) |
            Q(descricao__icontains=search_query)
        )
    
    # ORDENAÇÃO
    order_mapping = {
        'data_limite': 'data_limite',
        '-data_limite': '-data_limite',
        'data_criacao': 'data_criacao',
        '-data_criacao': '-data_criacao',
        'titulo': 'titulo',
        '-titulo': '-titulo',
        'concluido': 'concluido',
        '-concluido': '-concluido',
        'prioridade': 'prioridade',
        '-prioridade': '-prioridade',
        'urgente': 'data_limite',
    }
    
    campo_ordenacao = order_mapping.get(order_filtro, 'data_limite')
    lembretes = lembretes.order_by(campo_ordenacao)
    
    # ESTATÍSTICAS DOS LEMBRETES
    total_lembretes = lembretes.count()
    lembretes_pendentes = lembretes.filter(concluido=False).count()
    lembretes_concluidos = lembretes.filter(concluido=True).count()
    
    # Lembretes urgentes (≤ 2 dias)
    data_limite_urgente = hoje + timedelta(days=2)
    lembretes_urgentes = lembretes.filter(
        concluido=False,
        data_limite__lte=data_limite_urgente,
        data_limite__gte=hoje
    ).count()
    
    # Lembretes próximos (3-7 dias)
    data_limite_proximo_inicio = hoje + timedelta(days=3)
    data_limite_proximo_fim = hoje + timedelta(days=7)
    lembretes_proximos = lembretes.filter(
        concluido=False,
        data_limite__range=[data_limite_proximo_inicio, data_limite_proximo_fim]
    ).count()
    
    # CÁLCULOS FINANCEIROS PARA O MÊS ATUAL
    primeiro_dia_mes = hoje.replace(day=1)
    ultimo_dia_mes = (primeiro_dia_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    # Entradas do mês
    entradas_mes_query = entradas.filter(
        data__range=[primeiro_dia_mes, ultimo_dia_mes]
    )
    entradas_mes = entradas_mes_query.aggregate(
        total=Coalesce(Sum('valor'), Decimal('0.00'))
    )['total'] or Decimal('0.00')
    
    # Contagem de entradas
    entradas_count = entradas_mes_query.count()
    
    # Saídas do mês
    saidas_mes_query = saidas.filter(
        data_vencimento__range=[primeiro_dia_mes, ultimo_dia_mes]
    )
    saidas_mes = saidas_mes_query.aggregate(
        total=Coalesce(Sum('valor'), Decimal('0.00'))
    )['total'] or Decimal('0.00')
    
    # Contagem total de saídas
    saidas_count = saidas_mes_query.count()
    
    # Saídas pagas e pendentes
    saidas_pagas_mes = saidas.filter(
        data_vencimento__range=[primeiro_dia_mes, ultimo_dia_mes],
        situacao='paga'
    ).count()
    
    saidas_pendentes_mes = saidas.filter(
        data_vencimento__range=[primeiro_dia_mes, ultimo_dia_mes],
        situacao='pendente'
    ).count()
    
    # Saldo mensal
    saldo_mensal = entradas_mes - saidas_mes
    
    # CONTAS A VENCER (todas as saídas pendentes que ainda não venceram)
    contas_a_vencer = saidas.filter(
        situacao='pendente',
        data_vencimento__gte=hoje  # Apenas as que ainda não venceram
    ).count()
    
    # DADOS PARA O CALENDÁRIO (período mais amplo: 12 meses)
    data_inicio_calendario = hoje - timedelta(days=365)
    data_fim_calendario = hoje + timedelta(days=365)

    # Eventos do calendário
    eventos_calendario = []

    # Adicionar lembretes ao calendário
    lembretes_calendario = Lembrete.objects.filter(
        user=request.user,
        data_limite__range=[data_inicio_calendario, data_fim_calendario]
    )

    for lembrete in lembretes_calendario:
        dias_restantes = (lembrete.data_limite - hoje).days
        evento = {
            'id': f"lembrete_{lembrete.id}",
            'title': f"📋 {lembrete.titulo}",
            'start': lembrete.data_limite.isoformat(),
            'color': '#3B82F6',
            'extendedProps': {
                'type': 'lembrete',
                'dias_restantes': dias_restantes,
                'concluido': lembrete.concluido,
                'descricao': lembrete.descricao or '',
                'url': f'/lembretes/editar/{lembrete.id}/',
                'fullTitle': f"📋 {lembrete.titulo}"
            }
        }
        eventos_calendario.append(evento)

    # Adicionar entradas ao calendário
    entradas_calendario = entradas.filter(
        data__range=[data_inicio_calendario, data_fim_calendario]
    )

    for entrada in entradas_calendario:
        evento = {
            'id': f"entrada_{entrada.id}",
            'title': f"💰 {entrada.nome}",
            'start': entrada.data.isoformat(),
            'color': '#10B981',
            'extendedProps': {
                'type': 'entrada',
                'descricao': f"Valor: R$ {entrada.valor:.2f}",
                'valor': float(entrada.valor),
                'url': f'/entradas/editar/{entrada.id}/',
                'fullTitle': f"💰 {entrada.nome} - R$ {entrada.valor:.2f}"
            }
        }
        eventos_calendario.append(evento)

    # Adicionar saídas ao calendário
    saidas_calendario = saidas.filter(
        data_vencimento__range=[data_inicio_calendario, data_fim_calendario]
    )

    for saida in saidas_calendario:
        dias_restantes = (saida.data_vencimento - hoje).days
        evento = {
            'id': f"saida_{saida.id}",
            'title': f"💸 {saida.nome}",
            'start': saida.data_vencimento.isoformat(),
            'color': '#EF4444' if saida.situacao == 'pendente' else '#8B5CF6',
            'extendedProps': {
                'type': 'saida_pendente' if saida.situacao == 'pendente' else 'saida_paga',
                'dias_restantes': dias_restantes,
                'situacao': saida.situacao,
                'descricao': f"Valor: R$ {saida.valor:.2f}\nStatus: {saida.get_situacao_display()}",
                'valor': float(saida.valor),
                'url': f'/saidas/editar/{saida.id}/',
                'fullTitle': f"💸 {saida.nome} - R$ {saida.valor:.2f}"
            }
        }
        eventos_calendario.append(evento)
    
    # Garantir que todas as datas sejam strings serializáveis
    for evento in eventos_calendario:
        if isinstance(evento['start'], date):
            evento['start'] = evento['start'].isoformat()
    
    # Serializar para JSON seguro
    eventos_json = json.dumps(eventos_calendario, default=str, ensure_ascii=False)
    
    # CONTEXT DATA
    context = {
        # Filtros atuais
        'status_filtro': status_filtro,
        'tipo_filtro': tipo_filtro,
        'periodo_filtro': periodo_filtro,
        'order_filtro': order_filtro,
        'data_inicial': data_inicial,
        'data_final': data_final,
        'search_query': search_query,
        'mes_atual': mes_atual_ptbr,
        
        # Dados principais
        'lembretes': lembretes,
        'total_lembretes': total_lembretes,
        'lembretes_pendentes': lembretes_pendentes,
        'lembretes_concluidos': lembretes_concluidos,
        'lembretes_urgentes': lembretes_urgentes,
        'lembretes_proximos': lembretes_proximos,
        
        # Estatísticas financeiras
        'entradas_count': entradas_count,
        'saidas_count': saidas_count,
        'entradas_mes': entradas_mes,
        'saidas_mes': saidas_mes,
        'saidas_pagas_mes': saidas_pagas_mes,
        'saidas_pendentes_mes': saidas_pendentes_mes,
        'saldo_mensal': saldo_mensal,
        'contas_a_vencer': contas_a_vencer,
        
        # Dados do calendário
        'eventos_calendario': eventos_json,
        'mes_atual': f"{get_mes_portugues(hoje)} {hoje.year}",
        'hoje': hoje.isoformat(),
        
        # Datas para referência
        'primeiro_dia_mes': primeiro_dia_mes.isoformat(),
        'ultimo_dia_mes': ultimo_dia_mes.isoformat(),
        
        # Opções para templates
        'periodo_options': [
            {'value': '7', 'label': 'Últimos 7 dias'},
            {'value': '30', 'label': 'Últimos 30 dias'},
            {'value': '90', 'label': 'Últimos 3 meses'},
            {'value': '365', 'label': 'Último ano'},
            {'value': 'custom', 'label': 'Personalizado'},
            {'value': 'todos', 'label': 'Todos os períodos'},
        ],
        
        'status_options': [
            {'value': '', 'label': 'Todos os status'},
            {'value': 'pendente', 'label': 'Pendentes'},
            {'value': 'concluido', 'label': 'Concluídos'},
            {'value': 'urgente', 'label': 'Urgentes (≤ 2 dias)'},
        ],
        
        'order_options': [
            {'value': 'data_limite', 'label': 'Data Limite (Recente)'},
            {'value': '-data_limite', 'label': 'Data Limite (Antigo)'},
            {'value': 'data_criacao', 'label': 'Data Criação (Recente)'},
            {'value': '-data_criacao', 'label': 'Data Criação (Antigo)'},
            {'value': 'titulo', 'label': 'Nome (A-Z)'},
            {'value': '-titulo', 'label': 'Nome (Z-A)'},
            {'value': 'concluido', 'label': 'Status (Concluído)'},
            {'value': '-concluido', 'label': 'Status (Pendente)'},
        ]
    }
    
    return render(request, 'core/lembrete_list.html', context)



# VIEWS PARA OPERAÇÕES CRUD (mantenha estas também)
@login_required
@csrf_exempt
@require_http_methods(["POST"])
def lembrete_create(request):
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.dict()
        
        form = LembreteForm(data)
        
        if form.is_valid():
            lembrete = form.save(commit=False)
            lembrete.user = request.user
            lembrete.save()
            
            return JsonResponse({
                'success': True, 
                'message': 'Lembrete criado com sucesso!',
                'lembrete_id': lembrete.id
            })
        else:
            errors = {field: [str(error) for error in error_list] for field, error_list in form.errors.items()}
            return JsonResponse({
                'success': False, 
                'errors': errors
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao criar lembrete: {str(e)}'
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def lembrete_update(request, pk):
    try:
        lembrete = get_object_or_404(Lembrete, pk=pk, user=request.user)
        
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.dict()
        
        form = LembreteForm(data, instance=lembrete)
        
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True, 
                'message': 'Lembrete atualizado com sucesso!'
            })
        else:
            errors = {field: [str(error) for error in error_list] for field, error_list in form.errors.items()}
            return JsonResponse({
                'success': False, 
                'errors': errors
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao atualizar lembrete: {str(e)}'
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST", "DELETE"])
def lembrete_delete(request, pk):
    try:
        lembrete = get_object_or_404(Lembrete, pk=pk, user=request.user)
        lembrete.delete()
        
        return JsonResponse({
            'success': True, 
            'message': 'Lembrete excluído com sucesso.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao excluir lembrete: {str(e)}'
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def lembrete_toggle(request, pk):
    try:
        lembrete = get_object_or_404(Lembrete, pk=pk, user=request.user)
        
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            concluido = data.get('concluido', False)
        else:
            concluido = request.POST.get('concluido') == 'true'
        
        lembrete.concluido = concluido
        lembrete.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Status do lembrete atualizado com sucesso!',
            'concluido': lembrete.concluido
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao atualizar status: {str(e)}'
        }, status=500)
    
@login_required
@csrf_exempt
@require_http_methods(["POST"])
def alternar_status_lembrete(request):
    try:
        data = json.loads(request.body)
        lembrete_id = data.get('lembrete_id')
        concluido = data.get('concluido')
        
        lembrete = Lembrete.objects.get(id=lembrete_id, user=request.user)
        lembrete.concluido = concluido
        lembrete.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Status do lembrete atualizado com sucesso!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao atualizar status: {str(e)}'
        }, status=500)

@login_required
@csrf_exempt
@require_POST
def alternar_status_lembrete(request):
    try:
        data = json.loads(request.body)
        lembrete_id = data.get('lembrete_id')
        concluido = data.get('concluido')
        
        lembrete = Lembrete.objects.get(id=lembrete_id, user=request.user)
        
        with transaction.atomic():
            lembrete.concluido = concluido
            lembrete.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Status do lembrete atualizado com sucesso!'
        })
        
    except Lembrete.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Lembrete não encontrado.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao atualizar status: {str(e)}'
        }, status=500)
    



# views.py
import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.db.models import Sum
from decimal import Decimal
from .models import OperacaoSaque
from .forms import OperacaoSaqueForm
from .choices import TIPO_OPERACAO_CHOICES, INSTITUICOES_FINANCEIRAS  # Importe do choices.py

@login_required
def operacao_saque_list(request):
    # Filtros
    ano_selecionado = request.GET.get('ano', '')
    mes_selecionado = request.GET.get('mes', '')
    tipo_selecionado = request.GET.get('tipo', '')
    
    operacoes = OperacaoSaque.objects.filter(proprietario=request.user)
    
    # Aplicar filtros
    if ano_selecionado:
        operacoes = operacoes.filter(data_contratacao__year=ano_selecionado)
    if mes_selecionado:
        operacoes = operacoes.filter(data_contratacao__month=mes_selecionado)
    if tipo_selecionado:
        operacoes = operacoes.filter(tipo_operacao=tipo_selecionado)
    
    # Obter anos disponíveis para filtro
    anos_disponiveis = OperacaoSaque.objects.filter(
        proprietario=request.user
    ).dates('data_contratacao', 'year').order_by('-data_contratacao__year')
    
    # Meses para filtro
    meses = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
        (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
        (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
    ]
    
    # Cálculos para os cards
    total_saques = operacoes.aggregate(total=Sum('valor_saque'))['total'] or Decimal('0.00')
    valor_medio_saque = total_saques / len(operacoes) if operacoes else Decimal('0.00')
    total_liberado = operacoes.aggregate(total=Sum('valor_liberado_cliente'))['total'] or Decimal('0.00')
    percentual_liberado = (total_liberado / total_saques * 100) if total_saques > 0 else 0
    
    context = {
        'operacoes': operacoes,
        'form': OperacaoSaqueForm(),
        'total_saques': total_saques,
        'valor_medio_saque': valor_medio_saque,
        'total_liberado': total_liberado,
        'percentual_liberado': round(percentual_liberado, 2),
        'anos_disponiveis': [ano.year for ano in anos_disponiveis],
        'meses': meses,
        'TIPO_OPERACAO_CHOICES': TIPO_OPERACAO_CHOICES,  # Agora vem do choices.py
        'INSTITUICOES_FINANCEIRAS': INSTITUICOES_FINANCEIRAS,  # Também importado
        'ano_selecionado': ano_selecionado,
        'mes_selecionado': mes_selecionado,
        'tipo_selecionado': tipo_selecionado,
        'meses_display_map': dict(meses),
        'tipo_display_map': dict(TIPO_OPERACAO_CHOICES),  # Agora usa a variável importada
    }
    return render(request, 'core/operacao_saque_list.html', context)

@login_required
@require_POST
def operacao_saque_create(request):
    form = OperacaoSaqueForm(request.POST)
    if form.is_valid():
        operacao = form.save(commit=False)
        operacao.proprietario = request.user
        operacao.save()
        return JsonResponse({
            'success': True, 
            'message': 'Operação de saque criada com sucesso!'
        })
    else:
        errors = {field: [str(error) for error in errors] for field, errors in form.errors.items()}
        return JsonResponse({
            'success': False, 
            'errors': errors
        }, status=400)

@login_required
@require_http_methods(["GET", "POST"])
def operacao_saque_detail(request, pk):
    try:
        operacao = get_object_or_404(OperacaoSaque, pk=pk, proprietario=request.user)
        
        if request.method == 'GET':
            # Retorna dados para edição - AGORA INCLUI OS NOVOS CAMPOS
            return JsonResponse({
                'success': True,
                'operacao': {
                    'nome_banco': operacao.nome_banco,
                    'tipo_operacao': operacao.tipo_operacao,
                    'data_contratacao': operacao.data_contratacao.strftime('%Y-%m-%d'),
                    'valor_saque': str(operacao.valor_saque),
                    'valor_financiado': str(operacao.valor_financiado),
                    'valor_iof': str(operacao.valor_iof),
                    'valor_liberado_cliente': str(operacao.valor_liberado_cliente),
                    # NOVOS CAMPOS
                    'quantidade_parcelas': operacao.quantidade_parcelas,
                    'valor_parcela': str(operacao.valor_parcela) if operacao.valor_parcela else None,
                    'data_inicio_parcelas': operacao.data_inicio_parcelas.strftime('%Y-%m-%d') if operacao.data_inicio_parcelas else None,
                    'data_termino_parcelas': operacao.data_termino_parcelas.strftime('%Y-%m-%d') if operacao.data_termino_parcelas else None,
                }
            })
            
        elif request.method == 'POST':
            # Atualização
            form = OperacaoSaqueForm(request.POST, instance=operacao)
            if form.is_valid():
                form.save()
                return JsonResponse({
                    'success': True, 
                    'message': 'Operação de saque atualizada com sucesso!'
                })
            else:
                errors = {field: [str(error) for error in errors] for field, errors in form.errors.items()}
                return JsonResponse({
                    'success': False, 
                    'errors': errors
                }, status=400)
                
    except OperacaoSaque.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'message': 'Operação não encontrada.'
        }, status=404)

@login_required
@require_POST
def operacao_saque_delete(request, pk):
    try:
        operacao = get_object_or_404(OperacaoSaque, pk=pk, proprietario=request.user)
        operacao_nome = operacao.nome_banco
        operacao.delete()
        return JsonResponse({
            'success': True, 
            'message': f'Operação do banco {operacao_nome} excluída com sucesso!'
        })
    except OperacaoSaque.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'message': 'Operação não encontrada.'
        }, status=404)











        # ================================================================
# VIEWS DA ORACULO
# ================================================================
   
@login_required
def oraculo_financeiro(request):
    """
    Página de oráculo financeiro - análise inteligente das finanças
    """
    user = request.user
    hoje = date.today()
    
    # Dados básicos para análise
    saldo_total = ContaBancaria.objects.filter(proprietario=user).aggregate(Sum('saldo_atual'))['saldo_atual__sum'] or Decimal('0.00')
    
    # Entradas e saídas dos últimos 6 meses
    seis_meses_atras = hoje - relativedelta(months=6)
    primeiro_dia_seis_meses = seis_meses_atras.replace(day=1)
    
    entradas_ultimos_6_meses = Entrada.objects.filter(
        conta_bancaria__proprietario=user,
        data__gte=primeiro_dia_seis_meses
    ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')
    
    saidas_ultimos_6_meses = Saida.objects.filter(
        conta_bancaria__proprietario=user,
        data_vencimento__gte=primeiro_dia_seis_meses
    ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')
    
    # Média mensal
    media_entradas_mensal = entradas_ultimos_6_meses / Decimal('6.00')
    media_saidas_mensal = saidas_ultimos_6_meses / Decimal('6.00')
    
    # Reserva de emergência
    saldo_poupancas = ContaBancaria.objects.filter(
        proprietario=user,
        tipo='poupanca',
        ativa=True
    ).aggregate(Sum('saldo_atual'))['saldo_atual__sum'] or Decimal('0.00')
    
    meses_reserva = saldo_poupancas / media_saidas_mensal if media_saidas_mensal > 0 else 0
    
    # Análise de dívidas
    dividas_cartao = Saida.objects.filter(
        conta_bancaria__proprietario=user,
        conta_bancaria__tipo='credito',
        situacao='pendente'
    ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')
    
    # Fluxo mensal e taxa de economia
    fluxo_mensal = media_entradas_mensal - media_saidas_mensal
    taxa_economia = (fluxo_mensal / media_entradas_mensal * 100) if media_entradas_mensal > 0 else 0
    
    # MELHORIA 1: Análise de hábitos de gastos por dia da semana
    from django.db.models.functions import ExtractWeekDay
    
    gastos_por_dia = Saida.objects.filter(
        conta_bancaria__proprietario=user,
        data_vencimento__gte=primeiro_dia_seis_meses
    ).annotate(
        dia_semana=ExtractWeekDay('data_vencimento')
    ).values('dia_semana').annotate(
        total=Sum('valor')
    ).order_by('dia_semana')
    
    # Mapear números dos dias para nomes
    dias_semana_map = {
        1: 'Domingo',
        2: 'Segunda',
        3: 'Terça', 
        4: 'Quarta',
        5: 'Quinta',
        6: 'Sexta',
        7: 'Sábado'
    }
    
    gastos_por_dia_formatado = []
    for gasto in gastos_por_dia:
        gastos_por_dia_formatado.append({
            'dia': dias_semana_map.get(gasto['dia_semana'], 'Desconhecido'),
            'total': float(gasto['total'] or 0)
        })
    
    # MELHORIA 2: Dados comparativos com média nacional (fictícios)
    media_brasileira = {
        'economia': Decimal('5.2'),  # % da renda
        'reserva': Decimal('1.8'),   # meses
        'endividamento': Decimal('68.3')  # % das famílias
    }
    
    # MELHORIA 3: Sistema de metas
    metas_usuario = [
        {'nome': 'Reserva de 6 meses', 'atingida': meses_reserva >= 6, 'valor': meses_reserva, 'meta': 6},
        {'nome': 'Economizar 20%', 'atingida': taxa_economia >= 20, 'valor': taxa_economia, 'meta': 20},
        {'nome': 'Zerar dívidas', 'atingida': dividas_cartao == 0, 'valor': float(dividas_cartao), 'meta': 0}
    ]
    
    # Insights baseados nos dados
    insights = []
    
    # Insight 1: Reserva de emergência
    if meses_reserva < 3:
        insights.append({
            'tipo': 'alerta',
            'titulo': 'Reserva de Emergência Insuficiente',
            'descricao': f'Sua reserva cobre apenas {meses_reserva:.1f} meses de despesas. O ideal é ter 3-6 meses.',
            'acao': 'Aumente suas economias mensalmente.'
        })
    elif meses_reserva >= 6:
        insights.append({
            'tipo': 'sucesso',
            'titulo': 'Reserva de Emergência Adequada',
            'descricao': f'Parabéns! Sua reserva cobre {meses_reserva:.1f} meses de despesas.',
            'acao': 'Considere investir o excedente.'
        })
    
    # Insight 2: Comparativo com média brasileira
    if meses_reserva < media_brasileira['reserva']:
        insights.append({
            'tipo': 'alerta',
            'titulo': 'Abaixo da Média Nacional',
            'descricao': f'Sua reserva de {meses_reserva:.1f} meses está abaixo da média brasileira de {media_brasileira["reserva"]} meses.',
            'acao': 'Busque acompanhar ou superar a média nacional.'
        })
    
    # Insight 3: Fluxo mensal
    if fluxo_mensal < 0:
        insights.append({
            'tipo': 'perigo',
            'titulo': 'Fluxo de Caixa Negativo',
            'descricao': f'Seu fluxo mensal está negativo em R$ {abs(fluxo_mensal):.2f}.',
            'acao': 'Revise suas despesas e identifique onde cortar gastos.'
        })
    else:
        if taxa_economia < 10:
            insights.append({
                'tipo': 'alerta',
                'titulo': 'Baixa Taxa de Economia',
                'descricao': f'Você está economizando apenas {taxa_economia:.1f}% da sua renda.',
                'acao': 'Tente economizar pelo menos 15-20% da sua renda.'
            })
        elif taxa_economia > media_brasileira['economia']:
            insights.append({
                'tipo': 'sucesso',
                'titulo': 'Acima da Média Nacional',
                'descricao': f'Parabéns! Sua taxa de economia de {taxa_economia:.1f}% está acima da média brasileira de {media_brasileira["economia"]}%.',
                'acao': 'Continue mantendo essa disciplina financeira.'
            })
    
    # Insight 4: Dívidas
    if dividas_cartao > Decimal('0.00'):
        insights.append({
            'tipo': 'perigo',
            'titulo': 'Dívidas em Aberto',
            'descricao': f'Você tem R$ {dividas_cartao:.2f} em dívidas de cartão de crédito.',
            'acao': 'Priorize o pagamento dessas dívidas para evitar juros altos.'
        })
    
    # Insight 5: Gastos por categoria
    saidas_por_categoria = Saida.objects.filter(
        conta_bancaria__proprietario=user,
        data_vencimento__gte=primeiro_dia_seis_meses
    ).values('categoria').annotate(total=Sum('valor')).order_by('-total')[:5]
    
    if saidas_por_categoria:
        maior_categoria = saidas_por_categoria[0]
        insights.append({
            'tipo': 'info',
            'titulo': 'Maior Gasto por Categoria',
            'descricao': f'Sua maior categoria de gastos é {maior_categoria["categoria"]} com R$ {maior_categoria["total"]:.2f}.',
            'acao': 'Analise se esses gastos estão alinhados com suas prioridades.'
        })
    
    # Insight 6: Hábitos de gastos por dia
    if gastos_por_dia_formatado:
        dia_mais_gasto = max(gastos_por_dia_formatado, key=lambda x: x['total'])
        insights.append({
            'tipo': 'info',
            'titulo': 'Dia de Maior Gasto',
            'descricao': f'Você gasta mais às {dia_mais_gasto["dia"]}s (R$ {dia_mais_gasto["total"]:.2f}).',
            'acao': 'Planeje melhor seus gastos neste dia da semana.'
        })
    
    # Previsão para os próximos 3 meses
    previsao_3_meses = []
    saldo_projetado = float(saldo_total)
    
    for i in range(1, 4):
        mes_projetado = hoje + relativedelta(months=i)
        saldo_projetado += float(fluxo_mensal)
        previsao_3_meses.append({
            'mes': mes_projetado.strftime('%B/%Y'),
            'saldo_projetado': saldo_projetado
        })
    
    context = {
        'saldo_total': saldo_total,
        'media_entradas_mensal': media_entradas_mensal,
        'media_saidas_mensal': media_saidas_mensal,
        'fluxo_mensal': fluxo_mensal,
        'taxa_economia': taxa_economia,
        'meses_reserva': meses_reserva,
        'dividas_cartao': dividas_cartao,
        'insights': insights,
        'previsao_3_meses': previsao_3_meses,
        'gastos_por_dia': gastos_por_dia_formatado,
        'media_brasileira': media_brasileira,
        'metas_usuario': metas_usuario,
        'hoje': hoje.strftime('%d/%m/%Y')
    }
    
    return render(request, 'core/oraculo_financeiro.html', context)




# ================================================================
# VIEWS DE CATEGORIA E SUBCATEGORIA
# ================================================================
# 
# 
#  
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from datetime import date, timedelta, datetime
from django.utils import timezone as dj_timezone
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db import transaction
from decimal import Decimal
import json
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from dateutil.relativedelta import relativedelta
import numpy as np
from sklearn.linear_model import LinearRegression

# Importações dos seus modelos, formas e choices
from .models import ContaBancaria, Entrada, Saida, Transferencia, Lembrete, OperacaoSaque, Categoria, Subcategoria, Profile
from .forms import ContaBancariaForm, EntradaForm, SaidaForm, TransferenciaForm, OperacaoSaqueForm, CustomUserCreationForm, ProfileUpdateForm, LembreteForm
from .choices import FORMA_RECEBIMENTO_CHOICES, BANCO_CHOICES, FORMA_PAGAMENTO_CHOICES


@login_required
def get_categorias_and_subcategorias(request):
    """
    API que retorna categorias e subcategorias para o usuário logado
    ou categorias padrão.
    """
    try:
        # Busca todas as categorias do usuário logado e as categorias padrão.
        categorias = Categoria.objects.filter(
            Q(usuario=request.user) | Q(eh_padrao=True)
        ).distinct()
        
        # Busca todas as subcategorias do usuário logado e as padrão.
        subcategorias_todas = Subcategoria.objects.filter(
            Q(usuario=request.user) | Q(eh_padrao=True)
        ).distinct().order_by('nome')

        # Cria uma estrutura de dados aninhada para as categorias e subcategorias
        data = []
        for cat in categorias:
            subcats = [
                {'id': sub.id, 'nome': sub.nome, 'categoria_id': sub.categoria.id}
                for sub in subcategorias_todas if sub.categoria == cat
            ]
            data.append({
                'id': cat.id,
                'nome': cat.nome,
                'subcategorias': subcats
            })

        return JsonResponse({'success': True, 'data': data})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)



@require_POST
def criar_categoria_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Autenticação necessária.'}, status=401)
    
    try:
        data = json.loads(request.body)
        nome = data.get('nome', '').strip()

        if not nome:
            return JsonResponse({'success': False, 'message': 'O nome da categoria é obrigatório.'}, status=400)
        
        if Categoria.objects.filter(Q(usuario=request.user) | Q(eh_padrao=True), nome__iexact=nome).exists():
            return JsonResponse({'success': False, 'message': 'Já existe uma categoria com este nome.'}, status=400)
            
        nova_categoria = Categoria.objects.create(
            nome=nome,
            usuario=request.user,
            eh_padrao=False
        )
        return JsonResponse({'success': True, 'message': 'Categoria criada com sucesso!', 'categoria': {'id': nova_categoria.id, 'nome': nova_categoria.nome}})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Requisição JSON inválida.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Ocorreu um erro: {str(e)}'}, status=500)

@require_POST
def criar_subcategoria_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Autenticação necessária.'}, status=401)
        
    try:
        data = json.loads(request.body)
        nome = data.get('nome', '').strip()
        categoria_id = data.get('categoria_id')

        if not nome or not categoria_id:
            return JsonResponse({
                'success': False,
                'message': 'Nome e categoria são obrigatórios.'
            }, status=400)
        
        categoria = get_object_or_404(
            Categoria, 
            Q(usuario=request.user) | Q(eh_padrao=True),
            id=categoria_id
        )
        
        if Subcategoria.objects.filter(
            Q(usuario=request.user) | Q(eh_padrao=True),
            nome__iexact=nome,
            categoria=categoria
        ).exists():
            return JsonResponse({
                'success': False,
                'message': 'Já existe uma subcategoria com este nome para esta categoria.'
            }, status=400)
        
        subcategoria = Subcategoria.objects.create(
            nome=nome,
            categoria=categoria,
            usuario=request.user,
            eh_padrao=False
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Subcategoria criada com sucesso!',
            'subcategoria': {
                'id': subcategoria.id,
                'nome': subcategoria.nome,
                'categoria_id': categoria.id
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ocorreu um erro: {str(e)}'
        }, status=500)



# APIs para Categorias e Subcategorias
@login_required
@require_http_methods(["GET"])
def api_categorias(request):
    """
    Retorna todas as categorias do usuário e as categorias padrão como um JSON.
    """
    try:
        categorias = Categoria.objects.filter(
            Q(usuario=request.user) | Q(eh_padrao=True)
        ).distinct().order_by('nome')

        categorias_data = [{'id': cat.id, 'nome': cat.nome} for cat in categorias]
        
        return JsonResponse({'success': True, 'categorias': categorias_data})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erro ao listar categorias: {str(e)}'}, status=500)



@login_required
@require_http_methods(["GET"])
def api_subcategorias_por_categoria(request, categoria_id):
    """
    Retorna subcategorias de uma categoria específica como um JSON.
    """
    try:
        subcategorias = Subcategoria.objects.filter(
            categoria_id=categoria_id
        ).order_by('nome')
        
        subcategorias_data = [{'id': sub.id, 'nome': sub.nome} for sub in subcategorias]
        
        return JsonResponse({'success': True, 'subcategorias': subcategorias_data})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erro ao listar subcategorias: {str(e)}'}, status=500)

@login_required
@require_http_methods(["POST"])
def api_criar_categoria(request):
    """
    Cria uma nova categoria via AJAX.
    """
    try:
        data = json.loads(request.body)
        nome = data.get('nome', '').strip()
        
        if not nome:
            return JsonResponse({'success': False, 'message': 'Nome da categoria é obrigatório.'}, status=400)
        
        if Categoria.objects.filter(
            Q(usuario=request.user) | Q(eh_padrao=True),
            nome__iexact=nome
        ).exists():
            return JsonResponse({'success': False, 'message': 'Já existe uma categoria com este nome.'}, status=400)
        
        categoria = Categoria.objects.create(
            nome=nome,
            usuario=request.user,
            eh_padrao=False
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Categoria criada com sucesso!',
            'categoria': {'id': categoria.id, 'nome': categoria.nome}
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erro ao criar categoria: {str(e)}'}, status=500)

@login_required
@require_http_methods(["POST"])
def api_criar_subcategoria(request):
    """
    Cria uma nova subcategoria via AJAX.
    """
    try:
        data = json.loads(request.body)
        nome = data.get('nome', '').strip()
        categoria_id = data.get('categoria_id')
        
        if not nome or not categoria_id:
            return JsonResponse({'success': False, 'message': 'Nome e categoria são obrigatórios.'}, status=400)
        
        categoria = get_object_or_404(
            Categoria, 
            Q(usuario=request.user) | Q(eh_padrao=True),
            id=categoria_id
        )
        
        if Subcategoria.objects.filter(
            Q(usuario=request.user) | Q(eh_padrao=True),
            nome__iexact=nome,
            categoria=categoria
        ).exists():
            return JsonResponse({'success': False, 'message': 'Já existe uma subcategoria com este nome para esta categoria.'}, status=400)
        
        subcategoria = Subcategoria.objects.create(
            nome=nome,
            categoria=categoria,
            usuario=request.user,
            eh_padrao=False
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Subcategoria criada com sucesso!',
            'subcategoria': {
                'id': subcategoria.id,
                'nome': subcategoria.nome,
                'categoria_id': categoria.id
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erro ao criar subcategoria: {str(e)}'}, status=500)
