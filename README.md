# Sistema de Gestão de Finanças Pessoais

![Django](https://img.shields.io/badge/Django-5.2-blue?logo=django)
![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-orange)

Gestão completa de contas, receitas, despesas, transferências e perfis de usuário, com painel interativo e relatórios avançados, desenvolvido em Django com uma interface de usuário moderna e reativa.

## ✨ Funcionalidades Principais

- **Gestão de Contas:** Cadastro de contas bancárias (corrente, poupança, cartão de crédito, alimentação, etc.).
- **Lançamentos Financeiros:** Registro detalhado de receitas (entradas) e despesas (saídas), com suporte a parcelamento e recorrência.
- **Categorização:** Crie e gerencie categorias e subcategorias para organizar suas transações.
- **Transferências:** Realize transferências internas entre contas com atualização atômica e consistente de saldos.
- **Dashboard Analítico:** Painel interativo com gráficos, balanço mensal, análise de despesas por categoria e projeção de saldo futuro usando regressão linear.
- **Perfil de Usuário:** Gerenciamento de perfil com foto, temas (light/dark), estatísticas de uso, alteração de senha segura e exclusão de conta.
- **Operações de Saque:** Módulo para acompanhamento de empréstimos e operações de saque (ex: adiantamento de FGTS) com detalhes de parcelas.
- **Lembretes:** Crie lembretes para contas a pagar e outras datas importantes.
- **Interface Reativa:** Ações de CRUD e filtros são realizadas via AJAX/HTMX, proporcionando uma experiência de usuário fluida e sem recarregamentos de página.
- **Segurança:** Autenticação robusta, proteção contra CSRF e separação de configurações sensíveis.

## 🚀 Instalação Rápida

Siga os passos abaixo para configurar o ambiente de desenvolvimento.

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/financas-pessoais.git
    cd financas-pessoais
    ```

2.  **Crie um ambiente virtual e instale as dependências:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Configure o ambiente e o banco de dados:**
    ```bash
    # Copie o arquivo de exemplo para criar seu ambiente local
    cp .env.example .env
    
    # Edite o .env com suas configurações (SECRET_KEY, DATABASE_URL, etc.)
    
    # Aplique as migrações e crie um superusuário
    python manage.py migrate
    python manage.py createsuperuser
    ```

4.  **Inicie o servidor de desenvolvimento:**
    ```bash
    python manage.py runserver
    ```
    Acesse a aplicação em: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## 📚 Documentação Completa

A documentação detalhada do projeto, incluindo arquitetura, descrição de funcionalidades e guias para desenvolvedores, está disponível e pode ser servida localmente com MkDocs.

```bash
# Instale o MkDocs e o tema Material (se ainda não tiver)
pip install mkdocs mkdocs-material

# Sirva a documentação
mkdocs serve
```
Acesse a documentação em: [https://andre-fdias.github.io/Financas/](https://andre-fdias.github.io/Financas/)

## 🏗️ Arquitetura

- **Backend:** Python 3.11+, Django 5.2+
- **Frontend:** HTML, Tailwind CSS, HTMX
- **Banco de Dados:** SQLite (padrão), com suporte a PostgreSQL.
- **Análise de Dados:** Scikit-learn para projeções financeiras.
- **Testes:** Testes unitários e de integração com a suíte de testes do Django.
- **Estilo de Código:** O projeto segue os padrões da PEP8.

## 🤝 Contribuindo

Pull requests são muito bem-vindos! Para mudanças importantes, por favor, abra uma *issue* primeiro para discutir o que você gostaria de mudar.

Certifique-se de atualizar os testes conforme apropriado.

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

