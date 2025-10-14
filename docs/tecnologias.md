# Tecnologias Utilizadas

O FinanceFlow é construído com um conjunto de tecnologias modernas e robustas, escolhidas para oferecer desempenho, segurança e uma ótima experiência de desenvolvimento.

Abaixo está uma tabela detalhando as principais tecnologias usadas em cada parte do sistema.

| Categoria      | Tecnologia                                                                                             |
| :------------- | :----------------------------------------------------------------------------------------------------- |
| **Backend**    | Python 3.10+, Django 5, Django REST Framework, PostgreSQL, Redis, Gunicorn                             |
| **Frontend**   | Django Templates, Tailwind CSS, HTMX, Chart.js                                                         |
| **Mobile**     | Kotlin (Nativo Android)                                                                                |
| **Testes**     | Pytest, Pytest-Django, Coverage, Factory Boy, Faker                                                    |
| **DevOps**     | Docker, GitHub Actions (CI/CD), Whitenoise                                                             |
| **Qualidade**  | Black, Flake8, isort                                                                                   |
| **Documentação**| MkDocs, Material for MkDocs                                                                            |

## Detalhes sobre as Escolhas

- **Django:** Escolhido por sua robustez, segurança e ecossistema maduro ("baterias inclusas"). Ele serve como a espinha dorsal de todo o sistema.

- **Django REST Framework (DRF):** A escolha padrão da indústria para construir APIs RESTful com Django. Oferece serialização, autenticação e um conjunto completo de ferramentas para o desenvolvimento de APIs.

- **PostgreSQL:** Um banco de dados relacional de código aberto poderoso e confiável, ideal para aplicações que exigem consistência e integridade de dados.

- **HTMX:** Em vez de um framework JavaScript pesado como React ou Vue, optamos pelo HTMX para a interface web. Ele permite criar interfaces dinâmicas e modernas com menos complexidade, mantendo a lógica de renderização no servidor, o que se alinha bem com a filosofia do Django.

- **Tailwind CSS:** Um framework de CSS "utility-first" que nos permite construir designs complexos e responsivos rapidamente, sem sair do HTML.

- **Kotlin (Android):** A linguagem oficial para o desenvolvimento Android moderno. Permite criar um aplicativo nativo rápido, seguro e com uma ótima experiência de usuário.

- **Pytest:** O framework de testes preferido na comunidade Python por sua simplicidade, flexibilidade e fixtures poderosas.

- **Docker:** Utilizado para criar ambientes de desenvolvimento e produção consistentes e isolados, facilitando o deploy e a colaboração.
