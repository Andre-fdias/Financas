# Arquitetura do FinanceFlow

O FinanceFlow é construído sobre uma arquitetura híbrida que combina o poder do framework Django para renderização de páginas no servidor com uma API RESTful robusta para servir clientes desacoplados, como o aplicativo nativo para Android.

Essa abordagem permite oferecer uma experiência web rápida e interativa, ao mesmo tempo que mantém uma lógica de negócios centralizada e segura, acessível de qualquer plataforma.

## Visão Geral

A arquitetura pode ser dividida nos seguintes componentes principais:

1.  **Backend (Django):** O núcleo do sistema, responsável pela lógica de negócios, acesso ao banco de dados e autenticação.
2.  **Aplicação Web (Django + HTMX):** A interface web para navegadores, onde o Django renderiza o HTML e o HTMX adiciona interatividade.
3.  **API RESTful (Django REST Framework):** Expõe os dados e funcionalidades do sistema de forma segura para clientes externos.
4.  **Aplicação Mobile (Android Nativo):** Um cliente nativo que consome a API RESTful.
5.  **Banco de Dados (PostgreSQL):** O sistema de persistência de dados.

```mermaid
graph TD
    subgraph "Clientes"
        A[Browser]
        B[App Android Nativo]
    end

    subgraph "Servidor FinanceFlow"
        C{Django}
        D[API RESTful<br>(Django REST Framework)]
        E[Views Web<br>(com HTMX)]
    end

    subgraph "Dados"
        F[Banco de Dados<br>(PostgreSQL)]
    end

    A -- Requisições HTTP --> E
    E -- Renderiza HTML --> A
    B -- Requisições API (JSON) --> D
    D -- Respostas API (JSON) --> B
    C -- Gerencia --> D
    C -- Gerencia --> E
    D -- Acessa --> F
    E -- Acessa --> F
```

## Componentes em Detalhe

### 1. Backend (Django)

O Django atua como a espinha dorsal do projeto. Ele é responsável por:
- **Modelagem de Dados:** Define a estrutura do banco de dados através dos modelos em `core/models.py`.
- **Lógica de Negócios:** Centraliza todas as regras de validação e manipulação de dados.
- **Autenticação e Autorização:** Gerencia o acesso de usuários tanto para a aplicação web quanto para a API.

### 2. Aplicação Web (Django + HTMX + Tailwind CSS)

Esta é a interface acessada via navegador. A arquitetura se diferencia de um SPA (Single Page Application) tradicional:

- **Renderização no Servidor:** O Django é responsável por renderizar as páginas HTML completas. Isso melhora o SEO e o tempo de carregamento inicial.
- **Estilização com Tailwind CSS:** A interface é construída com o framework de CSS utilitário Tailwind. Os arquivos-fonte em `theme/static_src/` são compilados para um único arquivo CSS estático.
- **Interatividade com HTMX:** Para evitar recarregamentos completos da página em ações como filtros ou submissão de formulários, usamos o HTMX. Ele permite que elementos HTML façam requisições AJAX a URLs específicas no Django. Em vez de retornar JSON, as views do Django respondem com *fragmentos de HTML*, que o HTMX insere diretamente no DOM. Isso mantém a lógica de renderização no servidor, simplificando o frontend.

### 3. API RESTful (Django REST Framework)

Para servir o aplicativo Android e potencialmente outros serviços, o projeto expõe uma API RESTful usando o Django REST Framework (DRF).

- **Endpoints:** URLs bem definidas (ex: `/api/transacoes/`, `/api/contas/`) permitem operações de CRUD (Criar, Ler, Atualizar, Deletar) sobre os recursos do sistema.
- **Serialização:** O DRF converte os modelos complexos do Django em formato JSON, que é facilmente consumido por clientes.
- **Autenticação JWT:** A API é protegida usando **JSON Web Tokens**. O cliente (app Android) envia as credenciais, recebe um *access token* e o utiliza no cabeçalho `Authorization` de requisições subsequentes para se autenticar.

### 4. Aplicação Mobile (Android Nativo em Kotlin)

O projeto `android_app/` contém o código para um cliente Android nativo.

- **Cliente Desacoplado:** Ele opera de forma independente do backend, comunicando-se exclusivamente através da API RESTful.
- **Gerenciamento de Estado Próprio:** O app é responsável por sua própria interface, gerenciamento de estado e lógica de apresentação.

## Organização do Código

- `core/`: É o coração da aplicação Django. Contém os `models.py` (estrutura de dados), `views.py` (lógica para as páginas web com HTMX), `api_views.py` (lógica para os endpoints da API) e `serializers.py` (serializadores para a API).
- `theme/`: Um app Django dedicado ao frontend. `static_src/` contém os fontes do Tailwind CSS, e `templates/` contém os layouts HTML base.
- `financas/`: Contém as configurações globais do projeto Django, como `settings.py` e `urls.py`.
- `android_app/`: Um projeto Android Studio completamente separado, que vive no mesmo repositório mas não tem dependência direta de código com o Django.

## Fluxo de Dados para Visualização de Gráficos

Uma das funcionalidades centrais do dashboard é a capacidade de visualizar dados financeiros de forma interativa. O fluxo para gerar um gráfico (ex: despesas por categoria) é um ótimo exemplo de como os componentes da arquitetura trabalham juntos.

1.  **Interação do Usuário (Frontend):**
    - O usuário acessa o dashboard. Na interface, ele interage com filtros (ex: seleciona um período de "Últimos 30 dias" ou uma conta bancária específica).
    - O código JavaScript no frontend detecta a mudança nos filtros.

2.  **Requisição AJAX (Frontend -> Backend):**
    - O JavaScript monta uma requisição AJAX (usando `fetch`) para um endpoint específico da API, como `/api/dashboard/`.
    - Os filtros selecionados pelo usuário são enviados como parâmetros na URL (ex: `?periodo=30&conta_id=1`).

3.  **Processamento no Backend (Django API View):**
    - A view da API no Django (`api_views.py`) recebe a requisição.
    - Ela lê os parâmetros da URL para entender os filtros solicitados.
    - A view então executa consultas ao banco de dados, utilizando o ORM do Django para buscar as `Transacoes` que correspondem aos filtros do usuário.

4.  **Agregação de Dados (Backend):**
    - Em vez de retornar milhares de transações, a view processa e agrega esses dados.
    - Por exemplo, para um gráfico de "despesas por categoria", a view agrupa as transações por `categoria` e soma os `valores` de cada grupo.
    - O resultado é uma estrutura de dados simples e consolidada, pronta para ser visualizada (ex: `{'Alimentação': 500.00, 'Transporte': 150.00}`).

5.  **Resposta JSON (Backend -> Frontend):**
    - A view da API serializa os dados agregados em formato JSON e os retorna como resposta à requisição AJAX.
    - O JSON enviado é leve e contém apenas a informação necessária para o gráfico (ex: `labels: ['Alimentação', 'Transporte']`, `data: [500.00, 150.00]`).

6.  **Renderização do Gráfico (Frontend):**
    - O JavaScript no frontend recebe a resposta JSON.
    - Ele então usa a biblioteca **Chart.js** para renderizar ou atualizar o gráfico no elemento `<canvas>` correspondente.
    - Os dados recebidos (labels e valores) são passados para o Chart.js, que cuida de toda a parte visual da renderização.

Este fluxo otimiza o desempenho, pois transfere apenas dados consolidados pela rede e aproveita o poder do navegador do cliente para a renderização visual, resultando em uma experiência de usuário rápida e responsiva.
