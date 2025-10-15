# 📊 Exemplos de Diagramas de Fluxo para Documentação

## 1. DIAGRAMA DE ARQUITETURA DO SISTEMA

```mermaid
graph TB
    subgraph "Usuário"
        U[👤 Usuário]
    end

    subgraph "Frontend (Servido pelo Django)"
        B[🌐 Browser]
        T[📄 Django Templates]
        S[🎨 Tailwind CSS]
    end

    subgraph "Backend (Aplicação Django)"
        D[🐍 Django Core]
        API[🛡️ Django REST Framework]
        DB[🗄️ Database (PostgreSQL/SQLite)]
        C[📊 Redis (Cache)]
    end

    subgraph "Plataforma & CI/CD"
        GH[🐙 GitHub] --> GHA[🤖 GitHub Actions]
        GHA --> R[☁️ Render (Hospedagem)]
    end

    subgraph "Serviços Externos"
        Email[📧 Email Service]
        Sentry[🚨 Sentry (Error Monitoring)]
        PDF[📄 PDF Generation]
    end

    %% Conexões
    U --> B
    B <--> T
    T --> S
    T <--> D

    D <--> DB
    D <--> C
    D <--> API
    API <--> DB

    D --> Email
    D --> Sentry
    D --> PDF

    R --> D

    %% Estilos
    style D fill:#f3e5f5
    style DB fill:#e8f5e8
    style R fill:#cceeff
```

## 2. FLUXO DE AUTENTICAÇÃO

```mermaid
sequenceDiagram
    participant U as Usuário
    participant F as Frontend
    participant B as Backend
    participant D as Database

    U->>F: Acessa /login
    F->>B: GET /api/auth/login
    B->>F: Formulário de login
    U->>F: Preencre credenciais
    F->>B: POST /api/auth/login
    B->>D: Verifica usuário/senha
    D->>B: Dados do usuário
    B->>B: Gera JWT Token
    B->>F: Retorna token + user data
    F->>U: Redireciona para dashboard
    U->>F: Acessa recursos protegidos
    F->>B: Request com JWT token
    B->>B: Valida token
    B->>F: Dados solicitados
```

## 3. FLUXO DE UMA TRANSFERÊNCIA

```mermaid
flowchart TD
    A[🚀 Iniciar Transferência] --> B{Validar Dados}
    B -->|Dados Inválidos| C[❌ Retornar Erro]
    B -->|Dados Válidos| D{Saldo Suficiente?}
    
    D -->|Não| E[❌ Saldo Insuficiente]
    D -->|Sim| F[💾 Registrar Transferência]
    
    F --> G[📉 Debitar Conta Origem]
    G --> H[📈 Creditar Conta Destino]
    H --> I[📧 Notificar Usuário]
    I --> J[✅ Transferência Concluída]
    
    style A fill:#4caf50,color:white
    style J fill:#4caf50,color:white
    style C fill:#f44336,color:white
    style E fill:#f44336,color:white
```

## 4. FLUXO DO DASHBOARD

```mermaid
graph LR
    subgraph "Data Collection"
        A[📥 Entradas] --> D[Dashboard Service]
        B[📤 Saídas] --> D
        C[🔄 Transferências] --> D
    end

    subgraph "Data Processing"
        D --> E[🔢 Cálculo de Métricas]
        E --> F[📊 Agregação por Período]
        F --> G[📈 Análise de Tendências]
    end

    subgraph "Data Presentation"
        G --> H[🎯 Cards de Resumo]
        G --> I[📉 Gráficos Mensais]
        G --> J[🗂️ Relatórios Detalhados]
    end

    H --> K[👤 Usuário]
    I --> K
    J --> K
```

## 5. SISTEMA DE CATEGORIAS E SUBCATEGORIAS

```mermaid
classDiagram
    class Categoria {
        +String nome
        +String descricao
        +String cor
        +String icone
        +Boolean ativa
        +DateTime criado_em
        +addSubcategoria()
        +getSubcategorias()
    }

    class Subcategoria {
        +String nome
        +String descricao
        +Categoria categoria
        +Decimal orcamento_mensal
        +Boolean ativa
    }

    class Transacao {
        +Decimal valor
        +Date data
        +String descricao
        +Subcategoria subcategoria
        +ContaBancaria conta
    }

    Categoria "1" --> "*" Subcategoria
    Subcategoria "1" --> "*" Transacao
```

## 6. FLUXO DE DEPLOY NO RENDER

```mermaid
timeline
    title Fluxo de Deploy Automático
    section Git Push
        Commit no main : Desenvolvedor faz push<br>para o repositório
    section GitHub
        Webhook Trigger : GitHub notifica o Render
    section Render Build
        Build Process : Executa build.sh<br>Instala dependências
        Versioning : Gera versão automática
        Database Migrations : Aplica migrações
        Static Files : Coleta arquivos estáticos
    section Deploy
        Health Check : Verifica se aplicação<br>está respondendo
        Traffic Routing : Direciona tráfego<br>para nova versão
    section Monitoring
        Logs & Metrics : Monitora performance<br>e errors
```

## 7. SISTEMA DE PARCELAMENTO

```mermaid
stateDiagram-v2
    [*] --> NovaDespesa
    NovaDespesa --> AnaliseParcelamento: Usuário cria despesa
    
    state AnaliseParcelamento {
        [*] --> VerificarTipo
        VerificarTipo --> Avista : Tipo = À Vista
        VerificarTipo --> Parcelado : Tipo = Parcelado
        
        state Parcelado {
            [*] --> CalcularParcelas
            CalcularParcelas --> CriarParcela1
            CriarParcela1 --> AgendarProximas
            AgendarProximas --> [*]
        }
        
        state Avista {
            [*] --> CriarDespesaUnica
            CriarDespesaUnica --> [*]
        }
    }
    
    AnaliseParcelamento --> [*]
```

## 8. FLUXO DE GERACAO DE RELATÓRIOS

```mermaid
flowchart TD
    A[ Solicitar Relatório] --> B{Parâmetros Válidos?}
    B -->|Não| C[❌ Retornar Erro de Validação]
    B -->|Sim| D[🔍 Buscar Dados no Banco]
    
    D --> E{Quantidade de Dados}
    E -->|Poucos| F[⚡ Processamento Síncrono]
    E -->|Muitos| G[🔄 Processamento Assíncrono]
    
    F --> H[📄 Gerar Relatório]
    G --> I[🎯 Agendar Task Celery]
    I --> J[📧 Notificar Conclusão]
    J --> H
    
    H --> K{Formato}
    K -->|PDF| L[📋 Gerar PDF]
    K -->|Excel| M[📊 Gerar Excel]
    K -->|HTML| N[🌐 Gerar HTML]
    
    L --> O[⬇️ Download]
    M --> O
    N --> O
```

## 9. ARQUITETURA DE BANCO DE DADOS (SIMPLIFICADA)

```mermaid
erDiagram
    USUARIO ||--o{ CONTA_BANCARIA : possui
    USUARIO ||--o{ CATEGORIA : cria
    USUARIO ||--o{ TRANSACAO : realiza
    
    CONTA_BANCARIA ||--o{ TRANSACAO : contém
    CATEGORIA ||--o{ SUBCATEGORIA : contém
    SUBCATEGORIA ||--o{ TRANSACAO : classifica
    
    TRANSACAO ||--o{ PARCELA : gera
    TRANSACAO {
        string descricao
        decimal valor
        date data
        string tipo
    }
    
    CONTA_BANCARIA {
        string nome
        string banco
        decimal saldo
        string tipo
    }
    
    CATEGORIA {
        string nome
        string cor
        string icone
    }
```

## 10. FLUXO DE RECUPERAÇÃO DE SENHA

```mermaid
sequenceDiagram
    participant U as Usuário
    participant F as Frontend
    participant B as Backend
    participant E as Email Service
    participant D as Database

    U->>F: Clica 'Esqueci senha'
    F->>B: POST /api/auth/forgot-password
    B->>D: Verifica email existe
    D->>B: Retorna usuário
    B->>B: Gera token de reset
    B->>D: Salva token com expiração
    B->>E: Envia email com link
    E->>U: Email com link de reset
    
    U->>F: Clica no link do email
    F->>B: GET /api/auth/reset-password/{token}
    B->>D: Valida token
    D->>B: Token válido
    B->>F: Formulário de nova senha
    
    U->>F: Digita nova senha
    F->>B: POST /api/auth/reset-password
    B->>D: Atualiza senha + invalida token
    B->>F: Confirmação de sucesso
    F->>U: Redireciona para login
```

## 11. SISTEMA DE CACHE

```mermaid
flowchart TD
    A[📡 Request] --> B{Cache Hit?}
    B -->|Sim| C[⚡ Retornar do Cache]
    B -->|Não| D[🗄️ Buscar no Banco]
    
    D --> E[💾 Processar Dados]
    E --> F[📦 Armazenar no Cache]
    F --> G[🔄 Retornar Dados]
    C --> G
    
    subgraph "Cache Strategy"
        H[🎯 Dashboard Metrics - 5min]
        I[📊 Relatórios - 1h]
        J[👤 User Profile - 30min]
        K[📈 Charts Data - 15min]
    end
    
    F --> H
    F --> I
    F --> J
    F --> K
```

## 12. FLUXO DE CODE REVIEW

```mermaid
graph TB
    A[💻 Desenvolvedor] --> B[🌿 Cria Feature Branch]
    B --> C[🔧 Desenvolve Feature]
    C --> D[📝 Faz Commits Conventionais]
    D --> E[📤 Push para Remote]
    E --> F[🔄 Abre Pull Request]
    
    F --> G[🤖 CI/CD Pipeline]
    G --> H[✅ Tests Pass]
    H --> I[👀 Code Review]
    
    I --> J{Approved?}
    J -->|Não| K[🔧 Request Changes]
    K --> C
    J -->|Sim| L[🎯 Merge to Main]
    
    L --> M[🚀 Auto Deploy]
    M --> N[📊 Health Check]
    N --> O[✅ Deploy Successful]
```

## 13. ESTRUTURA DE PASTAS DO PROJETO

```mermaid
graph TD
    A[financeflow/] --> B[📁 core/]
    A --> C[📁 scripts/]
    A --> D[📁 docs/]
    A --> E[📁 .github/]
    
    B --> F[🗃️ models/]
    B --> G[🎯 views/]
    B --> H[📄 templates/]
    B --> I[🎨 static/]
    B --> J[🔧 utils/]
    
    F --> K[💰 finance_models.py]
    F --> L[👤 user_models.py]
    
    C --> M[🔄 auto_version.py]
    C --> N[🔧 deployment.py]
    
    E --> O[⚙️ workflows/]
    O --> P[🚀 deploy.yml]
    O --> Q[✅ tests.yml]
```

## 14. FLUXO DE NOTIFICAÇÕES

```mermaid
stateDiagram-v2
    [*] --> Monitoring
    Monitoring --> AlertTriggered: Condição Atendida
    
    state AlertTriggered {
        [*] --> EvaluateSeverity
        EvaluateSeverity --> LowPriority : Baixa
        EvaluateSeverity --> MediumPriority : Média
        EvaluateSeverity --> HighPriority : Alta
        
        state HighPriority {
            [*] --> SendEmail
            SendEmail --> SendSMS
            SendSMS --> LogIncident
            LogIncident --> [*]
        }
        
        state MediumPriority {
            [*] --> SendEmail
            SendEmail --> LogIncident
            LogIncident --> [*]
        }
        
        state LowPriority {
            [*] --> SendEmail
            SendEmail --> [*]
        }
    }
    
    AlertTriggered --> [*]
```

## 15. DIAGRAMA DE COMPONENTES FRONTEND

```mermaid
graph TB
    subgraph "Layout Components"
        A[🖼️ AppLayout] --> B[📱 Sidebar]
        A --> C[🔝 Header]
        A --> D[📊 MainContent]
    end

    subgraph "Page Components"
        D --> E[🏠 DashboardPage]
        D --> F[💳 ContasPage]
        D --> G[📥 EntradasPage]
        D --> H[📤 SaidasPage]
    end

    subgraph "Shared Components"
        I[📋 DataTable] --> J[🔍 Filters]
        I --> K[📄 Pagination]
        L[💬 Modal] --> M[✅ ConfirmDialog]
        L --> N[📝 FormModal]
    end

    E --> I
    F --> I
    F --> L
    G --> I
    G --> L
```
