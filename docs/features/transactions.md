# Fluxo de Entradas (Receitas) e Saídas (Despesas)

O registro de transações é a operação mais frequente no sistema. O fluxo é otimizado para ser rápido e eficiente, com uso intensivo de modais e AJAX.

### Entradas (Receitas)

O modelo `Entrada` é mais simples e representa qualquer dinheiro que entra em uma conta.

- **Campos:** `usuario`, `conta_bancaria`, `nome`, `valor`, `data`, `forma_recebimento`.
- **Validação:** O método `clean()` impede o registro de entradas com data futura.
- **Listagem (`/entradas/`):** A página `entrada_list` exibe todas as receitas, com filtros por ano, mês, conta e forma de recebimento. Cards no topo da página mostram totais, saldo residual e variação mensal.

### Saídas (Despesas)

O modelo `Saida` é mais complexo para acomodar diferentes tipos de despesas.

- **Campos Adicionais:**
  - `data_vencimento`: Data de vencimento da despesa.
  - `categoria`, `subcategoria`: Para classificação.
  - `forma_pagamento`, `tipo_pagamento_detalhe` (à vista, parcelado).
  - `situacao` ('pago', 'pendente').
  - `quantidade_parcelas`, `valor_parcela`.
  - `recorrente` (única, mensal, anual).

- **Validações Críticas (no método `clean()`):**
  - Para pagamentos parcelados, a quantidade de parcelas deve ser maior que 1.
  - A soma das parcelas não pode ter uma diferença maior que R$ 0,01 em relação ao valor total (para lidar com arredondamentos).
  - Despesas recorrentes não podem ser parceladas.

- **Listagem (`/saidas/`):** A página `saida_list` permite filtrar despesas por período (mês/ano) e status. Ela também inclui estatísticas como total pago vs. pendente e variação em relação ao mês anterior.

### Ações Rápidas

- **Marcar como Pago:** Na lista de saídas, há um botão para marcar uma despesa como `paga` sem sair da página. Esta ação é tratada pela `MarcarComoPagoView` através de uma requisição `POST` via AJAX.
  - **Endpoint:** `POST /saidas/<int:saida_id>/marcar-pago/`

### Formulários e Interação

Tanto para entradas quanto para saídas, os formulários de criação e edição são renderizados em modais e submetidos via AJAX. As views (`entrada_create`, `saida_create`, etc.) são projetadas para responder tanto a requisições normais (com recarregamento de página) quanto a requisições AJAX, retornando `JsonResponse` com mensagens de sucesso ou listas de erros de validação.
