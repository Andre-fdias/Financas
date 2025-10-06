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
from decimal import Decimal
import json # Já estava importado, mas é bom garantir
from django.views.decorators.http import require_GET, require_POST
from django.db.models import Q # Importante para combinar querysets
from dateutil.relativedelta import relativedelta
import numpy as np
from sklearn.linear_model import LinearRegression

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import datetime
from .models import Entrada, ContaBancaria
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

def get_month_range(date_obj):
    """Retorna o primeiro e último dia do mês para uma dada data."""
    first_day = date_obj.replace(day=1)
    last_day = (first_day + relativedelta(months=1)) - timedelta(days=1)
    return first_day, last_day

def calculate_percentage_change(current, previous):
    """Calcula a variação percentual entre dois valores."""
    if previous == 0:
        return 0 if current == 0 else 100
    return ((current - previous) / previous) * 100

def get_sum(queryset):
    """Retorna a soma de 'valor' de um queryset como Decimal, ou 0.00 se vazio."""
    result = queryset.aggregate(total=Sum('valor'))['total']
    return Decimal(str(result)) if result is not None else Decimal('0.00')

# Função para converter Decimals e Dates para tipos serializáveis em JSON
def serialize_for_json(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize_for_json(elem) for elem in obj]
    return obj

@login_required
def get_financial_insights(request):
    user = request.user
    hoje = date.today()
    num_meses_historico = 12
    num_meses_projecao = 6

    # ... (Copie toda a lógica de cálculo de dados do dashboard,
    #       incluindo o loop para `meses_labels`, `entradas_por_mes_data`,
    #       `saidas_por_mes_data` e a seção de "PROJEÇÃO FUTURA".)

    # A parte de cálculo da projeção com LinearRegression já existe na sua view dashboard.
    # Copie-a para cá.
    projecao_labels = meses_labels.copy()
    projecao_saldo_data = saldo_acumulado_data.copy()
    # Lógica de regressão linear para saldo, receitas e despesas
    if len(data_para_regressao_saldo) >= 3:
        try:
            X_hist = np.array(range(len(data_para_regressao_saldo))).reshape(-1, 1)
            y_hist_saldo = np.array(data_para_regressao_saldo)
            model_saldo = LinearRegression().fit(X_hist, y_hist_saldo)
            X_fut = np.array(range(len(data_para_regressao_saldo), len(data_para_regressao_saldo) + num_meses_projecao)).reshape(-1, 1)
            projecao_saldo_futuro = model_saldo.predict(X_fut)

            for i in range(num_meses_projecao):
                next_month = hoje + relativedelta(months=i+1)
                projecao_labels.append(next_month.strftime('%b/%y'))
                projecao_saldo_data.append(float(projecao_saldo_futuro[i]))

        except Exception as e:
            pass
    
    # Exemplo simples de insights baseados na projeção
    proximo_mes_saldo_projetado = projecao_saldo_data[-num_meses_projecao] if projecao_saldo_data else 0
    insight_text = f"Com base nos seus gastos e receitas, o saldo projetado para o próximo mês é de R$ {proximo_mes_saldo_projetado:,.2f}."

    # Retorna os dados como JSON
    return JsonResponse({
        'success': True,
        'insight_text': insight_text,
        'projecao_labels': projecao_labels,
        'projecao_saldo_data': projecao_saldo_data
    })

# ================================================================
# VIEWS DA APLICAÇÃO
# ================================================================

@login_required
def home(request):
    return render(request, 'core/home.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Conta criada para {username}! Faça login para continuar.')
            return redirect('core:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})


def custom_logout(request):
    """View personalizada para logout com mensagem"""
    logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('core:login')

# ================================================================
# VIEWS DE DASHBOARD
# ================================================================
@login_required
def dashboard(request):
    user = request.user
    hoje = dj_timezone.now().date() 
    primeiro_dia_mes_atual, ultimo_dia_mes_atual = get_month_range(hoje)

    # Obter o período de filtro e meses meta (para reserva de emergência)
    # Por agora, não estamos usando o 'periodo' para filtrar os dados gerais,
    # mas é mantido para extensibilidade futura.
    periodo = request.GET.get('periodo', '30')
    meses_meta = int(request.GET.get('meses_meta', 6))

    # Definir a data de início para os dados agregados (usado para últimas transações e alguns gráficos)
    # Para consistência, usaremos um período maior para gráficos de histórico.
    data_inicio_filtro = hoje - timedelta(days=365) # Exemplo: buscar dados do último ano para histórico

    # ================================================================
    # 1. DADOS PRINCIPAIS PARA OS CARDS
    # ================================================================

    saldo_total = ContaBancaria.objects.filter(proprietario=user).aggregate(Sum('saldo_atual'))['saldo_atual__sum'] or Decimal('0.00')

    # Receitas e Despesas do Mês Atual
    entradas_mes_atual = Entrada.objects.filter(
        conta_bancaria__proprietario=user,
        data__range=(primeiro_dia_mes_atual, ultimo_dia_mes_atual)
    ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')

    saidas_mes_atual = Saida.objects.filter(
        conta_bancaria__proprietario=user,
        data_lancamento__range=(primeiro_dia_mes_atual, ultimo_dia_mes_atual)
    ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')

    # Receitas e Despesas do Mês Anterior para Variação
    primeiro_dia_mes_anterior = primeiro_dia_mes_atual - relativedelta(months=1)
    ultimo_dia_mes_anterior = (primeiro_dia_mes_anterior + relativedelta(months=1)) - timedelta(days=1)

    entradas_mes_anterior = Entrada.objects.filter(
        conta_bancaria__proprietario=user,
        data__range=(primeiro_dia_mes_anterior, ultimo_dia_mes_anterior)
    ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')

    saidas_mes_anterior = Saida.objects.filter(
        conta_bancaria__proprietario=user,
        data_lancamento__range=(primeiro_dia_mes_anterior, ultimo_dia_mes_anterior)
    ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')

    variacao_receitas = calculate_percentage_change(float(entradas_mes_atual), float(entradas_mes_anterior))
    variacao_despesas = calculate_percentage_change(float(saidas_mes_atual), float(saidas_mes_anterior))

    # Reserva de Emergência (Saldo em contas tipo 'poupanca')
    saldo_poupancas = ContaBancaria.objects.filter(
        proprietario=user,
        tipo='poupanca',
        ativa=True
    ).aggregate(Sum('saldo_atual'))['saldo_atual__sum'] or Decimal('0.00')

    # Despesa mensal média (calcula média dos últimos 6 meses para reserva)
    data_seis_meses_atras = hoje - relativedelta(months=6)
    despesas_ultimos_6_meses = Saida.objects.filter(
        conta_bancaria__proprietario=user,
        data_lancamento__gte=data_seis_meses_atras,
        data_lancamento__lte=hoje
    ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')

    despesa_mensal_media = float(despesas_ultimos_6_meses) / 6 if despesas_ultimos_6_meses else 0

    # ================================================================
    # 2. DADOS PARA GRÁFICOS (Últimos 12 meses para histórico mais completo)
    # ================================================================
    num_meses_historico = 12
    meses_labels = []
    entradas_por_mes_data = []
    saidas_por_mes_data = []
    saldo_acumulado_data = []
    
    # Calcular saldo acumulado histórico
    temp_saldo_acumulado_base = float(saldo_total) # Saldo atual como base
    
    # Para calcular o saldo inicial do período, somamos as saídas e subtraímos as entradas do período para trás
    # Este é um cálculo mais complexo para um saldo "real" no início de cada mês no histórico
    # Para simplificar e focar nos gráficos, vamos pegar o saldo_total e ajustar para trás para cada mês

    for i in range(num_meses_historico - 1, -1, -1): # Começa do mês mais antigo para o atual
        data_mes = hoje - relativedelta(months=i)
        primeiro_dia, ultimo_dia = get_month_range(data_mes)
        
        entradas_mes = Entrada.objects.filter(
            conta_bancaria__proprietario=user,
            data__range=(primeiro_dia, ultimo_dia)
        ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')

        saidas_mes = Saida.objects.filter(
            conta_bancaria__proprietario=user,
            data_lancamento__range=(primeiro_dia, ultimo_dia)
        ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')
        
        meses_labels.append(data_mes.strftime('%b/%y'))
        entradas_por_mes_data.append(float(entradas_mes))
        saidas_por_mes_data.append(float(saidas_mes))

        # Calcula o saldo para este mês (saldo do fim do mês anterior + entradas - saídas)
        # Para o saldo acumulado, vamos simular começando com o saldo atual e ajustando para trás
        if i == 0: # Mês atual
            saldo_acumulado_data.append(float(saldo_total))
        else:
            # Saldo acumulado do mês anterior = Saldo acumulado do mês atual - (entradas do mês atual - saídas do mês atual)
            # Ao construir de trás para frente, o primeiro elemento adicionado será o mais antigo, então o append está ok
            # No final, faremos um reverse
            saldo_para_este_mes = temp_saldo_acumulado_base - (float(entradas_mes) - float(saidas_mes))
            saldo_acumulado_data.append(saldo_para_este_mes)
            temp_saldo_acumulado_base = saldo_para_este_mes
    
    # Ajusta os dados para ordem cronológica (do mês mais antigo para o mais novo)
    meses_labels.reverse()
    entradas_por_mes_data.reverse()
    saidas_por_mes_data.reverse()
    saldo_acumulado_data.reverse()

    # ================================================================
    # 3. SAZONALIDADE (Saldo Líquido Mensal)
    # ================================================================
    sazonalidade_labels = meses_labels
    sazonalidade_values = [e - s for e, s in zip(entradas_por_mes_data, saidas_por_mes_data)]

    # ================================================================
    # 4. PROJEÇÃO FUTURA (Regressão Linear Simples)
    # Considera os últimos 6 meses para a projeção, ou menos se não houver dados.
    # ================================================================
    num_meses_projecao = 6 # Projeta 6 meses à frente
    
    # Usar os últimos N meses de dados para a regressão
    data_para_regressao_saldo = saldo_acumulado_data[-num_meses_historico:]
    data_para_regressao_receitas = entradas_por_mes_data[-num_meses_historico:]
    data_para_regressao_despesas = saidas_por_mes_data[-num_meses_historico:]
    
    projecao_labels = meses_labels.copy()
    projecao_saldo_data = saldo_acumulado_data.copy()
    projecao_receitas_data = entradas_por_mes_data.copy()
    projecao_despesas_data = saidas_por_mes_data.copy()

    if len(data_para_regressao_saldo) >= 3: # Mínimo de 3 pontos para regressão significativa
        try:
            X_hist = np.array(range(len(data_para_regressao_saldo))).reshape(-1, 1)
            y_hist_saldo = np.array(data_para_regressao_saldo)
            y_hist_receitas = np.array(data_para_regressao_receitas)
            y_hist_despesas = np.array(data_para_regressao_despesas)

            model_saldo = LinearRegression().fit(X_hist, y_hist_saldo)
            model_receitas = LinearRegression().fit(X_hist, y_hist_receitas)
            model_despesas = LinearRegression().fit(X_hist, y_hist_despesas)

            # Projeta 'num_meses_projecao' meses à frente
            X_fut = np.array(range(len(data_para_regressao_saldo), len(data_para_regressao_saldo) + num_meses_projecao)).reshape(-1, 1)
            
            projecao_saldo_futuro = model_saldo.predict(X_fut)
            projecao_receitas_futuro = model_receitas.predict(X_fut)
            projecao_despesas_futuro = model_despesas.predict(X_fut)

            for i in range(num_meses_projecao):
                next_month = hoje + relativedelta(months=i+1)
                projecao_labels.append(next_month.strftime('%b/%y'))
                projecao_saldo_data.append(float(projecao_saldo_futuro[i]))
                projecao_receitas_data.append(float(projecao_receitas_futuro[i]))
                projecao_despesas_data.append(float(projecao_despesas_futuro[i]))
        except Exception as e:
            # Fallback se a regressão falhar (e.g., dados insuficientes, erro matemático)
            print(f"Erro na projeção de regressão linear: {e}")
            pass # Continua sem projeção se houver erro

    # ================================================================
    # 5. DESPESAS POR CATEGORIA (Mês atual)
    # ================================================================
    saidas_por_categoria = Saida.objects.filter(
        conta_bancaria__proprietario=user,
        data_lancamento__range=(primeiro_dia_mes_atual, ultimo_dia_mes_atual)
    ).values('categoria').annotate(total=Sum('valor')).order_by('categoria')

    # Mapeia os códigos das categorias para seus nomes de exibição
    mapa_categorias_saida_display = {c[0]: c[1] for c in CATEGORIA_CHOICES}
    categorias_despesas_labels = [mapa_categorias_saida_display.get(item['categoria'], item['categoria']) for item in saidas_por_categoria]
    categorias_despesas_data = [float(item['total']) for item in saidas_por_categoria]

    # ================================================================
    # 6. RECEITAS POR CATEGORIA/TIPO (Considera 'forma_recebimento' como categoria para fins de gráfico)
    # ================================================================
    entradas_por_forma = Entrada.objects.filter(
        conta_bancaria__proprietario=user,
        data__range=(primeiro_dia_mes_atual, ultimo_dia_mes_atual)
    ).values('forma_recebimento').annotate(total=Sum('valor')).order_by('forma_recebimento')

    mapa_formas_recebimento_display = {fr[0]: fr[1] for fr in FORMA_RECEBIMENTO_CHOICES}
    categorias_receitas_labels = [mapa_formas_recebimento_display.get(item['forma_recebimento'], item['forma_recebimento']) for item in entradas_por_forma]
    categorias_receitas_values = [float(item['total']) for item in entradas_por_forma]


    # ================================================================
    # 7. SALDOS POR CONTA BANCÁRIA
    # ================================================================
    contas_ativas = ContaBancaria.objects.filter(proprietario=user, ativa=True)
    saldo_contas_labels = []
    saldo_contas_values = []
    
    for conta in contas_ativas:
        # Calcular o saldo "real" da conta (saldo inicial + entradas - saídas)
        entradas_na_conta = Entrada.objects.filter(
            conta_bancaria=conta,
            data__range=(hoje.replace(day=1), hoje) # Entradas do mês atual
        ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')

        saidas_na_conta = Saida.objects.filter(
            conta_bancaria=conta,
            data_lancamento__range=(hoje.replace(day=1), hoje) # Saídas do mês atual
        ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')

        saldo_atual_conta = (conta.saldo_atual or Decimal('0.00')) + entradas_na_conta - saidas_na_conta
        
        # Ajuste para cartão de crédito: o saldo_atual da conta de crédito é o limite disponível
        # Se for cartão de crédito, o valor na tela deve ser a fatura atual (ou o que foi gasto)
        if conta.tipo == 'credito':
            # Considerando que 'saldo_atual' para cartões de crédito pode representar o limite
            # Ou, se for '0.00' representa que ainda não foi usado.
            # Para o dashboard, talvez o mais interessante seja o "uso do limite" ou "dívida"
            # Aqui, vou mostrar o saldo atual da conta (que deve ser o limite disponível)
            # ou o gasto se `saldo_atual` for usado para isso
            saldo_contas_values.append(float(conta.limite_cartao - saidas_na_conta) if conta.limite_cartao else float(-saidas_na_conta))
        else:
            saldo_contas_values.append(float(saldo_atual_conta))
        
        saldo_contas_labels.append(f"{conta.get_nome_banco_display()} ({conta.get_tipo_display()})")

    # ================================================================
    # 8. DESPESAS FIXAS VS VARIÁVEIS (Mês atual)
    # ================================================================
    despesas_fixas = Saida.objects.filter(
        conta_bancaria__proprietario=user,
        data_lancamento__range=(primeiro_dia_mes_atual, ultimo_dia_mes_atual),
        recorrente__in=['mensal', 'anual']
    ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')

    despesas_variaveis = Saida.objects.filter(
        conta_bancaria__proprietario=user,
        data_lancamento__range=(primeiro_dia_mes_atual, ultimo_dia_mes_atual)
    ).exclude(recorrente__in=['mensal', 'anual']).aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')

    # ================================================================
    # 9. STATUS DE PAGAMENTOS (Mês atual)
    # ================================================================
    pagos_total = Saida.objects.filter(
        conta_bancaria__proprietario=user,
        data_vencimento__range=(primeiro_dia_mes_atual, ultimo_dia_mes_atual),
        situacao='pago'
    ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')

    pendentes_total = Saida.objects.filter(
        conta_bancaria__proprietario=user,
        data_vencimento__range=(primeiro_dia_mes_atual, ultimo_dia_mes_atual),
        situacao='pendente'
    ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')

    # ================================================================
    # 10. ANÁLISE COMPORTAMENTAL
    # ================================================================
    gastos_por_dia_semana_raw = {'Seg': Decimal('0.00'), 'Ter': Decimal('0.00'), 'Qua': Decimal('0.00'), 'Qui': Decimal('0.00'), 'Sex': Decimal('0.00'), 'Sáb': Decimal('0.00'), 'Dom': Decimal('0.00')}
    data_30_dias_atras = hoje - timedelta(days=29)
    saidas_ultimos_30_dias = Saida.objects.filter(
        conta_bancaria__proprietario=user,
        data_lancamento__range=(data_30_dias_atras, hoje)
    )
    
    dias_da_semana_map = {0: 'Seg', 1: 'Ter', 2: 'Qua', 3: 'Qui', 4: 'Sex', 5: 'Sáb', 6: 'Dom'}
    
    for saida in saidas_ultimos_30_dias:
        dia_semana_idx = saida.data_lancamento.weekday() # 0 para Segunda, 6 para Domingo
        dia_semana_label = dias_da_semana_map[dia_semana_idx]
        gastos_por_dia_semana_raw[dia_semana_label] += saida.valor

    gastos_por_dia_semana = {k: float(v) for k,v in gastos_por_dia_semana_raw.items()}

    # Gastos por hora do dia (simplificado para demonstração)
    gastos_por_hora_dia_raw = {str(h): Decimal('0.00') for h in range(24)}
    for saida in saidas_ultimos_30_dias:
        # Apenas se a data_lancamento for um datetime, ou usar um valor padrão para hora
        if isinstance(saida.data_lancamento, datetime):
            hora = saida.data_lancamento.hour
        else:
            # Se data_lancamento é um date, vamos usar uma hora arbitrária para agregação ou ignorar
            # Para este exemplo, vou simular uma distribuição uniforme
            hora = saida.data_lancamento.day % 24 # Apenas para ter uma distribuição
        gastos_por_hora_dia_raw[str(hora)] += saida.valor

    gastos_por_hora_dia = {k: float(v) for k,v in gastos_por_hora_dia_raw.items()}


    # Categorias comportamentais simplificadas (necessita de categorização no modelo Saida para ser mais preciso)
    # Para este exemplo, usaremos uma divisão arbitrária.
    total_despesas_mes = float(saidas_mes_atual)
    categorias_comportamento_data = {
        'Essenciais': total_despesas_mes * 0.6,  # Estimativa
        'Supérfluos': total_despesas_mes * 0.3,  # Estimativa
        'Investimentos': total_despesas_mes * 0.1 # Estimativa (ou 0 se não houver investimento direto)
    }

    # ================================================================
    # 11. INDICADORES DE SAÚDE FINANCEIRA
    # ================================================================
    liquidez_corrente = (float(saldo_total) / float(saidas_mes_atual) * 100) if saidas_mes_atual else 0
    margem_seguranca = ((float(entradas_mes_atual) - float(saidas_mes_atual)) / float(entradas_mes_atual) * 100) if entradas_mes_atual else 0
    
    # Dívidas (ex: saldo negativo de cartões de crédito, empréstimos)
    # Assumindo que o saldo_atual negativo em contas de crédito representa dívida
    dividas = ContaBancaria.objects.filter(
        proprietario=user,
        tipo='credito',
    ).aggregate(Sum('saldo_atual'))['saldo_atual__sum'] or Decimal('0.00')
    
    # Soma de todas as despesas a pagar no cartão para o mês atual
    gastos_cartao_mes_atual = Saida.objects.filter(
        conta_bancaria__proprietario=user,
        conta_bancaria__tipo='credito',
        data_vencimento__range=(primeiro_dia_mes_atual, ultimo_dia_mes_atual)
    ).aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')

    limite_total_credito = ContaBancaria.objects.filter(
        proprietario=user,
        tipo='credito'
    ).aggregate(Sum('limite_cartao'))['limite_cartao__sum'] or Decimal('0.00')

    # Endividamento: % de gastos_cartao_mes_atual em relação ao limite_total_credito
    endividamento = (float(gastos_cartao_mes_atual) / float(limite_total_credito) * 100) if limite_total_credito > 0 else 0
    
    poupanca_mensal_estimada = float(entradas_mes_atual) - float(saidas_mes_atual)
    reserva_emergencia_ideal_indicador = despesa_mensal_media * meses_meta

    nivel_risco_texto = "Baixo"
    if endividamento > 50: 
        nivel_risco_texto = "Alto"
    elif endividamento > 20: 
        nivel_risco_texto = "Moderado"

    # ================================================================
    # 12. SIMULAÇÕES DE CENÁRIOS
    # ================================================================
    aumento_10_despesas = float(saidas_mes_atual) * 1.10
    reducao_10_despesas = float(saidas_mes_atual) * 0.90
    aumento_10_receitas = float(entradas_mes_atual) * 1.10
    reducao_10_receitas = float(entradas_mes_atual) * 0.90
    impacto_inflacao_5 = float(saidas_mes_atual) * 1.05

    # ================================================================
    # 13. ANÁLISE DE RISCOS
    # ================================================================
    concentracao_risco = 0 # Requer categorização de entradas para cálculo preciso

    # ================================================================
    # 14. OTIMIZAÇÃO DE INVESTIMENTOS
    # ================================================================
    alocacao_investimentos_labels = ['Reserva Emergencial', 'Renda Fixa', 'Renda Variável']
    alocacao_investimentos_values = [70, 20, 10] # Valores de exemplo
    sugestao_investimentos = "Priorize a construção da reserva de emergência."
    if float(saldo_poupancas) >= reserva_emergencia_ideal_indicador:
        sugestao_investimentos = "Sua reserva está completa! Considere diversificar seus investimentos."

    # ================================================================
    # 15. ÚLTIMAS TRANSAÇÕES
    # ================================================================
    ultimas_entradas = Entrada.objects.filter(
    conta_bancaria__proprietario=user
    ).select_related('conta_bancaria').order_by('-data')[:5]

    ultimas_saidas = Saida.objects.filter(
        conta_bancaria__proprietario=user
    ).select_related('conta_bancaria', 'categoria').order_by('-data_lancamento')[:5]

    ultimas_transacoes_list = []
    for entrada in ultimas_entradas:
        ultimas_transacoes_list.append({
            'data': entrada.data.isoformat(),
            'descricao': entrada.nome,
            'valor': float(entrada.valor),
            'tipo': 'Entrada',
            'categoria': 'Receita',  # Categoria padrão para entradas
            'conta': entrada.conta_bancaria.get_nome_banco_display() if entrada.conta_bancaria else 'N/A'
        })

    for saida in ultimas_saidas:
        ultimas_transacoes_list.append({
            'data': saida.data_lancamento.isoformat(),
            'descricao': saida.nome,
            'valor': float(-saida.valor),  # Despesas são negativas
            'tipo': 'Saída',
            'categoria': saida.categoria.nome if saida.categoria else 'Sem Categoria',
            'conta': saida.conta_bancaria.get_nome_banco_display() if saida.conta_bancaria else 'N/A'
        })

    ultimas_transacoes_list.sort(key=lambda x: x['data'], reverse=True)
    ultimas_transacoes_list = ultimas_transacoes_list[:10]

    # ================================================================
    # CONSTRUÇÃO DO CONTEXTO A SER PASSADO PARA JSON
    # ================================================================
    context_data = {
        'saldo_geral': float(saldo_total),
        'entradas_mes': float(entradas_mes_atual),
        'saidas_mes': float(saidas_mes_atual),
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
        'projecao_receitas': projecao_receitas_data,
        'projecao_despesas': projecao_despesas_data,
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

    # Serializa todos os dados para JSON, usando a função auxiliar para Decimals e Dates
    dados_graficos_json = json.dumps(context_data, default=serialize_for_json)
    
    context = {'dados_graficos_json': dados_graficos_json}
    
    return render(request, 'core/dashboard.html', context)


# ===== FUNÇÃO AUXILIAR ÚNICA =====
def get_sum(queryset):
    """Retorna a soma de 'valor' de um queryset como Decimal, ou 0.00 se vazio."""
    result = queryset.aggregate(total=Sum('valor'))['total']
    return Decimal(str(result)) if result is not None else Decimal('0.00')

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
# VIEWS DE SAÍDAS
# ================================================================


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
    
    # Filtros
    # Define o mês e ano atual como padrão se não houver filtro na URL
    ano_filter_str = request.GET.get('ano', str(ano_atual))
    mes_filter_str = request.GET.get('mes', str(mes_atual).zfill(2)) # Garante dois dígitos
    status_filter_code = request.GET.get('status', '') # Padrão vazio para 'Todos'
    
    # Validar filtros
    try:
        ano_filter = int(ano_filter_str)
    except (ValueError, TypeError):
        ano_filter = ano_atual
    
    if mes_filter_str == '': # Se o filtro de mês for explicitamente vazio ('Todos os meses')
        mes_num = None
    else:
        try:
            mes_num = int(mes_filter_str)
            if mes_num < 1 or mes_num > 12:
                mes_num = mes_atual
        except (ValueError, TypeError):
            mes_num = mes_atual
    
    # Aplica os filtros
    saidas_qs = Saida.objects.filter(usuario=request.user)
    
    saidas_qs = saidas_qs.filter(data_vencimento__year=ano_filter)
    
    if mes_num:
        saidas_qs = saidas_qs.filter(data_vencimento__month=mes_num)
        mes_selecionado = str(mes_num).zfill(2)
    else:
        # Se 'Todos os meses' foi selecionado (mes_num é None),
        # ou se o filtro de mês na URL estava vazio,
        # mes_selecionado deve ser vazio para marcar a opção "Todos os meses" no HTML.
        mes_selecionado = '' 
    
    if status_filter_code:
        saidas_qs = saidas_qs.filter(situacao=status_filter_code)
        status_selecionado = status_filter_code
    else:
        status_selecionado = ''
    
    # Processar despesas para exibir no template
    saidas = saidas_qs.order_by('-data_vencimento')
    
    # Cálculos para os cards
    total_despesas = get_sum(saidas_qs)
    despesas_pagas = get_sum(saidas_qs.filter(situacao='pago'))
    despesas_pendentes = get_sum(saidas_qs.filter(situacao='pendente'))
    
    percentual_pago = round((despesas_pagas / total_despesas * 100) if total_despesas > 0 else 0, 2)
    percentual_pendente = round((despesas_pendentes / total_despesas * 100) if total_despesas > 0 else 0, 2)
    
    # Para cálculo da variação mensal (apenas se estiver filtrando por mês)
    variacao_mensal = Decimal('0.00')
    variacao_mensal_abs = Decimal('0.00') # NOVO: Variável para o valor absoluto
    if mes_num: # Se um mês específico está sendo filtrado
        mes_anterior_date = hoje - relativedelta(months=1)
        primeiro_dia_mes_anterior, ultimo_dia_mes_anterior = get_month_range(mes_anterior_date)
        
        saidas_mes_anterior_qs = Saida.objects.filter(
            usuario=request.user,
            data_vencimento__range=(primeiro_dia_mes_anterior, ultimo_dia_mes_anterior)
        )
        # Se um filtro de status está ativo, aplique-o também ao mês anterior para uma comparação justa
        if status_filter_code:
            saidas_mes_anterior_qs = saidas_mes_anterior_qs.filter(situacao=status_filter_code)

        total_despesas_mes_anterior = get_sum(saidas_mes_anterior_qs)
        
        if total_despesas_mes_anterior > 0:
            variacao_mensal = round(((total_despesas - total_despesas_mes_anterior) / total_despesas_mes_anterior * 100), 2)
        else:
            variacao_mensal = Decimal('100.00') if total_despesas > 0 else Decimal('0.00')
        
        variacao_mensal_abs = abs(variacao_mensal) # NOVO: Calcula o valor absoluto aqui
    
    # Nome do mês para o título
    mes_nome = dict(meses_choices).get(mes_selecionado, 'Todos os meses') # Usa mes_selecionado aqui
    if mes_selecionado == '': # Se for "Todos os meses"
        mes_nome = 'Todos os meses'


    # Anos disponíveis (busca anos com registros e adiciona alguns anos ao redor do atual)
    anos_com_registros = set(Saida.objects.filter(usuario=request.user).values_list('data_vencimento__year', flat=True))
    anos_disponiveis = sorted(list(anos_com_registros.union(range(ano_atual - 2, ano_atual + 2))), reverse=True)

    # Mapeamento de meses e status para badges
    meses_display_map = {k: v for k, v in meses_choices}
    status_display_map = {k: v for k, v in STATUS_CHOICES_DISPLAY} # Mapeamento para exibir nomes
    
    form = SaidaForm(user=request.user) # Instancia o formulário para o modal
    
    context = {
        'saidas': saidas,
        'total_despesas': total_despesas,
        'despesas_pagas': despesas_pagas,
        'despesas_pendentes': despesas_pendentes,
        'percentual_pago': percentual_pago,
        'percentual_pendente': percentual_pendente,
        'variacao_mensal': variacao_mensal,
        'variacao_mensal_abs': variacao_mensal_abs, # NOVO: Passa o valor absoluto para o template
        'mes_atual_nome': mes_nome, # Nome do mês para o título, baseado no filtro
        'ano_atual': ano_filter, # Usa o ano filtrado, não necessariamente o atual
        'meses': meses_choices, # Para o select de filtro
        'anos_disponiveis': anos_disponiveis,
        'STATUS_CHOICES': STATUS_CHOICES_DISPLAY, # Para o select de filtro
        'ano_selecionado': str(ano_filter), # Passa o ano filtrado (string)
        'mes_selecionado': mes_selecionado, # Passa o mês filtrado (string de 2 dígitos ou '')
        'status_selecionado': status_selecionado, # Passa o status filtrado (string)
        'meses_display_map': meses_display_map, # Para os badges
        'status_display_map': status_display_map, # Para os badges
        'form': form, # Passa o formulário para o template
        'today_date': dj_timezone.now().date().isoformat(), # Para o atributo max da data de lançamento
    }
    
    return render(request, 'core/saida_list.html', context)


from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class MarcarComoPagoView(View):
    def post(self, request, saida_id):
        print(f"DEBUG: saida_id = {saida_id}")
        print(f"DEBUG: request.user = {request.user}")
        
        try:
            saida = Saida.objects.get(id=saida_id, usuario=request.user)
            saida.situacao = 'pago'
            saida.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Despesa marcada como paga com sucesso!'
            })
            
        except Saida.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Despesa não encontrada.'
            }, status=404)
        

@login_required
def saida_create(request):
    if request.method == 'POST':
        form = SaidaForm(request.POST, user=request.user)
        if form.is_valid():
            saida = form.save(commit=False)
            saida.usuario = request.user
            saida.save()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Despesa cadastrada com sucesso!'})
            else:
                messages.success(request, 'Despesa cadastrada com sucesso!')
                return redirect('core:saida_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors = {field: [str(error) for error in error_list] for field, error_list in form.errors.items()}
                return JsonResponse({'success': False, 'errors': errors}, status=400)
            else:
                # Se o formulário for inválido e não for AJAX, redireciona com erro
                messages.error(request, 'Erro ao cadastrar despesa. Verifique os dados informados.')
                return redirect('core:saida_list')

    # Requisições GET são apenas para abrir o modal via AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    # Se for um GET não-AJAX, redireciona para a lista
    return redirect('core:saida_list')

@login_required
def saida_update(request, pk):
    saida = get_object_or_404(Saida, pk=pk, usuario=request.user)

    if request.method == 'POST':
        form = SaidaForm(request.POST, instance=saida, user=request.user)
        if form.is_valid():
            form.save()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Despesa atualizada com sucesso!'})
            else:
                messages.success(request, 'Despesa atualizada com sucesso!')
                return redirect('core:saida_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # Retorna os erros de validação diretamente
                errors = {field: [str(error) for error in error_list] for field, error_list in form.errors.items()}
                return JsonResponse({'success': False, 'errors': errors}, status=400)

    else: # GET request (quando o botão "Editar" é clicado)
        form = SaidaForm(instance=saida, user=request.user)

    # Obter contas bancárias do usuário (para o template normal e para os dados do modal GET)
    contas_bancarias = ContaBancaria.objects.filter(proprietario=request.user, ativa=True)

    # Se for requisição AJAX (para abrir o modal para edição), retornar JSON com os dados para preenchimento
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'id': saida.pk,
            'nome': saida.nome,
            'valor': str(saida.valor),
            'data_lancamento': saida.data_lancamento.isoformat() if saida.data_lancamento else '',
            'data_vencimento': saida.data_vencimento.isoformat() if saida.data_vencimento else '',
            'local': saida.local if saida.local else '',
            'categoria': saida.categoria if saida.categoria else '',
            'subcategoria': saida.subcategoria if saida.subcategoria else '',
            'forma_pagamento': saida.forma_pagamento if saida.forma_pagamento else '',
            'tipo_pagamento_detalhe': saida.tipo_pagamento_detalhe if saida.tipo_pagamento_detalhe else '',
            'situacao': saida.situacao if saida.situacao else '',
            'quantidade_parcelas': saida.quantidade_parcelas if saida.quantidade_parcelas else 1,
            'recorrente': saida.recorrente if saida.recorrente else '',
            'observacao': saida.observacao if saida.observacao else '',
            'conta_bancaria': saida.conta_bancaria.pk if saida.conta_bancaria else '', # Retorna o PK da conta
            'valor_parcela': str(saida.valor_parcela) if saida.valor_parcela else ''
        })

    # Se for requisição normal (não AJAX), renderizar a página completa
    return render(request, 'core/saida_form.html', {
        'form': form,
        'action': 'Editar',
        'FORMA_PAGAMENTO_CHOICES': FORMA_PAGAMENTO_CHOICES,
        'SITUACAO_CHOICES': SITUACAO_CHOICES,
        'CATEGORIA_CHOICES': CATEGORIA_CHOICES,
        'SUBCATEGORIA_CHOICES': SUBCATEGORIA_CHOICES,
        'TIPO_PAGAMENTO_DETALHE_CHOICES': TIPO_PAGAMENTO_DETALHE_CHOICES,
        'PERIODICIDADE_CHOICES': PERIODICIDADE_CHOICES,
        'contas_bancarias': contas_bancarias
    })

@login_required
def saida_delete(request, pk):
    saida = get_object_or_404(Saida, pk=pk, usuario=request.user)

    if request.method == 'POST':
        saida.delete()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Despesa excluída com sucesso!'})

        messages.success(request, 'Despesa excluída com sucesso!')
        return redirect('core:saida_list')

    # GET request (se acessado diretamente, o que não deve ocorrer com o modal JS)
    # Apenas para garantir que o Django tem um fallback
    return render(request, 'core/saida_confirm_delete.html', {'saida': saida})


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
    
    ano_filtro = request.GET.get('ano', str(ano_atual))
    mes_filtro = request.GET.get('mes', str(mes_atual))
    tipo_filtro = request.GET.get('tipo')
    
    entradas = Entrada.objects.filter(usuario=request.user)
    saidas = Saida.objects.filter(usuario=request.user)
    
    if mes_filtro and mes_filtro != 'todos':
        entradas = entradas.filter(data__month=mes_filtro)
        saidas = saidas.filter(data_vencimento__month=mes_filtro)
    
    entradas = entradas.filter(data__year=ano_filtro)
    saidas = saidas.filter(data_vencimento__year=ano_filtro)
    
    if tipo_filtro == 'entrada':
        saidas = saidas.none()
    elif tipo_filtro == 'saida':
        entradas = entradas.none()
    
    transacoes = sorted(
        list(entradas) + list(saidas),
        key=lambda x: x.data if hasattr(x, 'data') else x.data_vencimento,
        reverse=True
    )
    
    total_entradas = entradas.aggregate(total=Sum('valor'))['total'] or 0
    total_saidas = saidas.aggregate(total=Sum('valor'))['total'] or 0
    saldo_mes = total_entradas - total_saidas
    
    mes_para_calculo = int(mes_filtro) if mes_filtro and mes_filtro != 'todos' else mes_atual
    ano_para_calculo = int(ano_filtro)
    
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
    
    mes_nome = dict(meses).get(int(mes_filtro) if mes_filtro and mes_filtro != 'todos' else mes_atual, '')
    
    return render(request, 'core/extrato_completo.html', {
        'transacoes': transacoes,
        'meses': meses,
        'anos_disponiveis': list(range(ano_atual - 2, ano_atual + 1)),
        'ano_selecionado': int(ano_filtro),
        'mes_selecionado': str(mes_atual) if not mes_filtro or mes_filtro == 'todos' else mes_filtro,
        'tipo_filtro': tipo_filtro,
        'total_entradas': total_entradas,
        'total_saidas': total_saidas,
        'saldo_mes': saldo_mes,
        'variacao_mensal': variacao_mensal,
        'mes_atual_nome': mes_nome,
        'ano_atual': ano_para_calculo,
    })

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
   

# --- Lembretes ---

@login_required
def lembrete_list(request):
    lembretes = Lembrete.objects.filter(user=request.user).order_by('data_limite')
    form = LembreteForm()
    
    context = {
        'lembretes': lembretes,
        'form': form,
    }
    return render(request, 'core/lembrete_list.html', context)

# views.py
@login_required
def lembrete_create(request):
    if request.method == 'POST':
        form = LembreteForm(request.POST)
        if form.is_valid():
            lembrete = form.save(commit=False)
            lembrete.user = request.user
            lembrete.save()
            return JsonResponse({'success': True, 'message': 'Lembrete criado com sucesso!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors.get_json_data()}, status=400)
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

@login_required
def lembrete_update(request, pk):
    lembrete = get_object_or_404(Lembrete, pk=pk, user=request.user)
    if request.method == 'POST':
        form = LembreteForm(request.POST, instance=lembrete)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Lembrete atualizado com sucesso!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors.get_json_data()}, status=400)
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

@login_required
def lembrete_delete(request, pk):
    lembrete = get_object_or_404(Lembrete, pk=pk, user=request.user)
    if request.method == 'POST':
        lembrete.delete()
        return JsonResponse({'success': True, 'message': 'Lembrete excluído com sucesso.'})
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

# views.py
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
@require_POST
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