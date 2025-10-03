# Guia de Instalação Local

Siga os passos abaixo para ter uma instância do projeto rodando localmente.

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/financas-pessoais.git
    cd financas-pessoais
    ```

2.  **Crie e ative o ambiente virtual:**
    ```bash
    # Para Linux/macOS
    python3 -m venv venv
    source venv/bin/activate

    # Para Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instale as dependências do projeto:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente:**
    Copie o arquivo de exemplo `.env.example` para um novo arquivo chamado `.env`.
    ```bash
    cp .env.example .env
    ```
    Abra o arquivo `.env` e preencha as variáveis necessárias. Veja a seção "Variáveis de Ambiente" para mais detalhes.

5.  **Aplique as migrações do banco de dados:**
    Este comando criará as tabelas no banco de dados com base nos modelos do Django.
    ```bash
    python manage.py migrate
    ```

6.  **Crie um superusuário:**
    Você precisará de um usuário administrador para acessar o painel de administração do Django.
    ```bash
    python manage.py createsuperuser
    ```
    Siga as instruções no terminal para definir o nome de usuário, e-mail e senha.

7.  **Inicie o servidor de desenvolvimento:**
    ```bash
    python manage.py runserver
    ```

Por padrão, a aplicação estará acessível em `http://127.0.0.1:8000/`.
