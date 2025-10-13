# Instalação

## Pré-requisitos

Antes de iniciar, garanta que você tenha os seguintes softwares instalados em seu ambiente de desenvolvimento:

- **Python:** Versão 3.11 ou superior.
- **Git:** Para clonar o repositório.
- **Ambiente Virtual:** Recomenda-se o uso de `venv` (nativo do Python) para isolar as dependências do projeto.
- **Banco de Dados:** O projeto é configurado para usar **SQLite** por padrão (sem necessidade de instalação adicional). Para produção, recomenda-se **PostgreSQL**.

## Guia de Instalação Local

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

## Configuração de Variáveis de Ambiente

O projeto utiliza um arquivo `.env` na raiz para gerenciar configurações sensíveis e específicas do ambiente, mantendo-as fora do controle de versão.

O arquivo `.env` é carregado pelo `python-decouple` no `settings.py`.

### Variáveis Principais

| Variável          | Descrição                                                                                                | Exemplo                                                    |
| ----------------- | -------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| `SECRET_KEY`      | Chave secreta do Django. **Nunca a exponha publicamente.**                                                | `django-insecure-your-random-secret-key`                   |
| `DEBUG`           | Define se o modo de depuração está ativo. `True` em desenvolvimento, `False` em produção.                  | `True`                                                     |
| `ALLOWED_HOSTS`   | Lista de hosts/domínios permitidos para servir a aplicação, separados por vírgula.                         | `127.0.0.1,localhost,meusite.com`                          |
| `DATABASE_URL`    | URL de conexão com o banco de dados.                                                                     | `sqlite:///db.sqlite3` ou `postgres://user:pass@host/db`   |
| `EMAIL_BACKEND`   | Backend de e-mail do Django. Use `django.core.mail.backends.console.EmailBackend` para testes em console. | `django.core.mail.backends.smtp.EmailBackend`              |
| `EMAIL_HOST`      | Host do servidor de e-mail.                                                                              | `smtp.gmail.com`                                           |
| `EMAIL_PORT`      | Porta do servidor de e-mail.                                                                             | `587`                                                      |
| `EMAIL_USE_TLS`   | Se o servidor de e-mail usa TLS.                                                                         | `True`                                                     |
| `EMAIL_HOST_USER` | Usuário para autenticação no servidor de e-mail.                                                         | `seu-email@gmail.com`                                      |
| `EMAIL_HOST_PASSWORD` | Senha para autenticação no servidor de e-mail.                                                           | `sua-senha-de-app`                                         |
