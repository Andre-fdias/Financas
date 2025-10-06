# Painéis Analíticos (Dashboard)

A view `dashboard` (`/dashboard/`) é o principal centro de inteligência do sistema, oferecendo uma visão consolidada e analítica da saúde financeira do usuário.

Devido à sua complexidade e ao grande volume de dados processados, esta é uma das views mais críticas em termos de performance.

### Componentes do Dashboard

A view agrega e processa dados para exibir:

1.  **Cards de Resumo:**
    - Saldo total atual.
    - Total de receitas e despesas do mês.
    - Variação percentual de receitas/despesas em relação ao mês anterior.
    - Status da reserva de emergência.

2.  **Gráficos Históricos:**
    - Evolução de receitas, despesas e saldo acumulado ao longo dos últimos 12 meses.

3.  **Projeção Futura (Regressão Linear):**
    - Utilizando a biblioteca `scikit-learn`, a view treina um modelo de regressão linear simples com os dados dos últimos meses.
    - Com base nesse modelo, projeta as tendências de receitas, despesas e saldo para os próximos 6 meses.
    - **Dependência:** `numpy`, `scikit-learn`.

4.  **Análise de Despesas:**
    - Gráfico de pizza mostrando a distribuição de despesas por categoria no mês atual.
    - Gráfico comparativo de despesas fixas vs. variáveis.

5.  **Análise Comportamental:**
    - Gráfico de barras mostrando o total de gastos por dia da semana, ajudando a identificar padrões de consumo.

6.  **Indicadores de Saúde Financeira:**
    - **Liquidez Corrente:** Capacidade de cobrir despesas de curto prazo.
    - **Margem de Segurança:** Percentual da renda que sobra após as despesas.
    - **Nível de Endividamento:** Percentual do limite de crédito que está sendo utilizado.

### Otimização e Performance

A view `dashboard` executa um número significativo de consultas ao banco de dados. Para otimizar:

- **Consultas:** As consultas são feitas usando `aggregate(Sum(...))` para que o banco de dados realize os cálculos, o que é mais eficiente do que trazer os objetos para o Python e somá-los.
- **Serialização:** Todos os dados para os gráficos são coletados, processados e passados para o template como um único objeto JSON (`dados_graficos_json`). O JavaScript no lado do cliente é responsável por ler este JSON e renderizar os gráficos (usando uma biblioteca como Chart.js, por exemplo).

### API de Insights

- **Endpoint:** `GET /api/insights/`
- **View:** `financial_insights_api`
- **Funcionalidade:** Esta API complementar fornece insights rápidos e acionáveis em formato de texto, como "Sua reserva de emergência está baixa" ou "Sua taxa de economia este mês foi de 20%", ideal para ser exibido em um widget no painel.
