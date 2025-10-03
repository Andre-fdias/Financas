# Configuração de Variáveis de Ambiente

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
