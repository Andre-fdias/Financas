# Funcionalidades

## Painéis Analíticos (Dashboard)

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

## Operações de Saque e Empréstimos

Este módulo é destinado ao rastreamento de operações de crédito mais complexas, como empréstimos ou adiantamentos (saque-aniversário do FGTS, etc.), que envolvem parcelas e taxas.

### Modelo `OperacaoSaque`

O modelo `core.models.OperacaoSaque` armazena os detalhes dessas operações:

- `proprietario`: `ForeignKey` para o `User`.
- `nome_banco`: A instituição financeira.
- `tipo_operacao`: `CharField` com `choices` para definir o tipo (ex: 'Empréstimo Pessoal', 'Saque FGTS').
- `data_contratacao`: Data em que a operação foi realizada.
- `valor_saque`: O valor total da operação.
- `valor_financiado`, `valor_iof`: Campos para detalhar custos.
- `valor_liberado_cliente`: O valor líquido que o cliente recebeu.
- **Detalhes do Parcelamento:**
  - `quantidade_parcelas`
  - `valor_parcela`
  - `data_inicio_parcelas`
  - `data_termino_parcelas`

### Lógica de Negócio

O método `save()` do modelo contém uma lógica para calcular automaticamente a data de término do parcelamento se a data de início e a quantidade de parcelas forem fornecidas, utilizando a biblioteca `dateutil`.

```python
# Em core/models.py
from dateutil.relativedelta import relativedelta

class OperacaoSaque(models.Model):
    # ...
    def save(self, *args, **kwargs):
        # ...
        if self.data_inicio_parcelas and self.quantidade_parcelas:
            self.data_termino_parcelas = self.data_inicio_parcelas + relativedelta(months=self.quantidade_parcelas)
        
        super().save(*args, **kwargs)
```

### Interface de Gerenciamento

A página `/operacoes-saque/` (`operacao_saque_list`) permite ao usuário visualizar e gerenciar todas as suas operações de saque.

- **Listagem e Filtros:** As operações são listadas e podem ser filtradas por ano, mês e tipo de operação.
- **Estatísticas:** Cards no topo da página exibem o valor total sacado, o valor médio por operação e o total líquido liberado ao cliente.
- **CRUD via AJAX:** Assim como outros módulos do sistema, a criação, edição e exclusão de operações são feitas através de modais e requisições AJAX, proporcionando uma experiência de usuário ágil.

## Gestão de Lembretes Financeiros

O módulo de lembretes permite que o usuário cadastre datas e eventos importantes para não perder prazos de pagamentos ou outras obrigações financeiras.

### Modelo `Lembrete`

O modelo `core.models.Lembrete` é simples e direto:

- `user`: `ForeignKey` para o usuário dono do lembrete.
- `titulo`: Um título curto para o lembrete.
- `descricao`: Um campo de texto opcional para mais detalhes.
- `data_limite`: A data final para o lembrete.
- `concluido`: Um `BooleanField` para marcar o lembrete como concluído.

### Interface e Funcionalidades

A gestão de lembretes é feita na página `/lembretes/` (`lembrete_list`) e é totalmente orientada a AJAX para uma experiência fluida.

- **Listagem:** Os lembretes são listados em ordem de `data_limite`.
- **Criação:** Um formulário em um modal permite a criação de novos lembretes.
- **Edição e Exclusão:** Ações rápidas disponíveis para cada lembrete na lista.

### Ação de Alternar Status

A funcionalidade mais interativa é a de marcar um lembrete como concluído diretamente na lista.

- **Endpoint:** `POST /lembretes/alternar-status/`
- **View:** `alternar_status_lembrete`

1.  O usuário clica em uma checkbox ao lado do lembrete.
2.  Uma requisição `POST` via JavaScript é enviada para a API, contendo o ID do lembrete e o novo status (`true` ou `false`).
3.  A view atualiza o campo `concluido` no banco de dados.
4.  A interface é atualizada visualmente (ex: o texto do lembrete é riscado) sem a necessidade de recarregar a página.

### `@csrf_exempt`

A view `alternar_status_lembrete` utiliza o decorador `@csrf_exempt`. Isso é feito para simplificar a chamada AJAX a partir do JavaScript. 

**Nota de Segurança:** Embora simplifique o desenvolvimento, o uso de `@csrf_exempt` deve ser feito com cautela. Neste caso, o risco é baixo, pois a ação (marcar um lembrete como concluído) é idempotente e restrita ao usuário logado (`request.user`). No entanto, para ações mais sensíveis, seria preferível enviar o token CSRF no cabeçalho da requisição AJAX.

## Cadastro e Gerenciamento de Contas Bancárias

O gerenciamento de contas é uma funcionalidade central do sistema, permitindo que o usuário cadastre todas as suas contas financeiras, sejam elas contas correntes, poupanças ou cartões.

### Modelo `ContaBancaria`

O modelo `core.models.ContaBancaria` possui os seguintes campos importantes:

- `proprietario`: `ForeignKey` para o `User`.
- `nome_banco`: `CharField` com `choices` vindos de `core.choices.BANCO_CHOICES`.
- `tipo`: `CharField` com `choices` como 'corrente', 'poupanca', 'credito', etc.
- `saldo_atual`: `DecimalField` para o saldo da conta.
- `ativa`: `BooleanField` para ativar ou desativar uma conta.
- **Campos de Cartão de Crédito:** `limite_cartao`, `dia_fechamento_fatura`, `dia_vencimento_fatura`.

### Operações CRUD

O sistema oferece um CRUD (Create, Read, Update, Delete) completo para contas, com forte integração AJAX.

- **Listagem (`/contas/`):** A view `conta_list` exibe todas as contas do usuário, com filtros por tipo, status, titular e banco. A página também apresenta estatísticas como saldo total e número de contas ativas/inativas.

- **Criação (`/contas/nova/`):** A criação de contas pode ser feita através de um modal na página de listagem, que envia os dados via AJAX para a view `conta_create`. Isso evita um recarregamento da página.

- **Atualização (`/contas/<int:pk>/editar/`):** A edição também é feita via AJAX, pré-preenchendo os dados da conta em um modal.

- **Exclusão (`/contas/<int:pk>/excluir/`):** A exclusão requer confirmação e também é processada via AJAX.

### Validações

O modelo `ContaBancaria` possui validações no método `clean()` para garantir a integridade dos dados:

- Contas do tipo `corrente` ou `poupanca` exigem que os campos `agencia` and `numero_conta` sejam preenchidos.
- Outros tipos de conta, como cartões, não devem ter o campo `agencia` preenchido.

### APIs e Endpoints Auxiliares

- `GET /get_banco_code/`: Uma pequena API que retorna o código de um banco com base no seu nome.
- `GET /get-account-balance/<int:pk>/`: Retorna o saldo de uma conta específica, usado para atualizar dinamicamente a interface.

## Fluxo de Entradas (Receitas) e Saídas (Despesas)

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

## Transferências Internas e Regras de Consistência de Saldos

A funcionalidade de transferência permite ao usuário mover fundos entre suas próprias contas cadastradas. A principal preocupação nesta operação é garantir a **atomicidade** e a **consistência** dos saldos.

### Modelo `Transferencia`

O modelo `core.models.Transferencia` é composto por:

- `usuario`: O usuário que realiza a transferência.
- `conta_origem`: `ForeignKey` para `ContaBancaria` de onde o dinheiro sai.
- `conta_destino`: `ForeignKey` para `ContaBancaria` para onde o dinheiro vai.
- `valor`: `DecimalField` com o montante da transferência.
- `data`: A data em que a transferência foi realizada.

### Garantia de Atomicidade

Uma transferência envolve duas operações de atualização no banco de dados: subtrair o saldo da conta de origem e adicionar o saldo à conta de destino. Se uma dessas operações falhar, a outra não pode ser concluída, pois isso deixaria os dados em um estado inconsistente (dinheiro "desapareceria" ou seria "criado" do nada).

Para resolver isso, todas as views que manipulam transferências (`transferencia_create`, `transferencia_update`, `transferencia_delete`) são decoradas com `@transaction.atomic`.

```python
from django.db import transaction

@login_required
@transaction.atomic
def transferencia_create(request):
    # ... lógica da view ...
```

Este decorador garante que todas as operações de banco de dados dentro da view sejam executadas em uma única transação. Se qualquer erro ocorrer, a transação inteira sofre um *rollback*, e nenhuma alteração é salva no banco de dados.

### Lógica de Atualização de Saldo

A lógica de negócio para atualizar os saldos reside no método `save()` do modelo `Transferencia`.

```python
# Em core/models.py
class Transferencia(BaseModel):
    # ... campos ...

    def save(self, *args, **kwargs):
        # A lógica só é aplicada para novas transferências
        if not self.pk:
            # Atualiza os saldos das contas
            self.conta_origem.saldo_atual -= self.valor
            self.conta_destino.saldo_atual += self.valor
            
            self.conta_origem.save()
            self.conta_destino.save()
        
        super().save(*args, **kwargs)
```

- Ao **criar** uma transferência, o saldo é debitado da origem e creditado no destino.
- Ao **excluir**, a view `transferencia_delete` executa a lógica inversa: o valor é devolvido à conta de origem e removido da conta de destino antes de a transferência ser apagada.
- A **atualização** é a operação mais complexa: ela primeiro reverte a transação antiga e depois aplica a nova, tudo dentro de um bloco `atomic`.

## Autenticação e Perfis de Usuário

O sistema possui um fluxo completo de autenticação e gerenciamento de perfis, utilizando o sistema de autenticação nativo do Django e estendendo-o com um modelo de perfil personalizado.

### Fluxo de Autenticação

- **Registro:** Novos usuários podem se registrar através da página `/register`. A view `core.views.register` utiliza o `CustomUserCreationForm` para criar um novo `User`.
- **Login:** A autenticação é feita na página `/login`, usando a `LoginView` nativa do Django. Após o login, o usuário é redirecionado para o `dashboard`.
- **Logout:** A rota `/logout` (`custom_logout`) encerra a sessão do usuário e exibe uma mensagem de sucesso.
- **Reset de Senha:** O fluxo completo de recuperação de senha está implementado usando as views nativas do Django (`PasswordResetView`, etc.), com templates personalizados.

### Perfil do Usuário (`Profile`)

O modelo `Profile` (`core/models.py`) estende o modelo `User` com uma relação `OneToOneField` para armazenar informações adicionais.

- **Campos Principais:**
  - `foto_perfil`: `ImageField` para a foto do usuário. O sistema redimensiona a imagem para 300x300 pixels no upload e remove a foto antiga para economizar espaço.
  - `theme`: Permite que o usuário escolha um tema (`light`, `dark`, `auto`).
  - `login_streak`, `total_logins`: Campos para gamificação, rastreando a frequência de acesso.

### Gerenciamento de Perfil

A página de perfil (`/profile/`) permite ao usuário:

- **Atualizar Informações:** Alterar nome, sobrenome e e-mail através do `UserUpdateForm`.
- **Alterar Foto:** Fazer upload de uma nova foto de perfil ou remover a foto existente (`ProfileUpdateForm`).
- **Mudar Senha:** Alterar a senha de forma segura (`PasswordChangeForm`).
- **Excluir Conta:** Uma opção para excluir permanentemente a conta, com uma etapa de confirmação para segurança.

### APIs Relacionadas

Diversas ações no perfil são realizadas via AJAX para uma melhor experiência do usuário:

- `POST /api/profile/update-info/`: Atualiza dados básicos do usuário.
- `POST /api/profile/update-photo/`: Atualiza a foto de perfil.
- `GET /api/profile/statistics/`: Fornece dados para um painel de estatísticas do usuário (dias de acesso, etc.).
