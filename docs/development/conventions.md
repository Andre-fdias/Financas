# Padrões e Convenções

Para manter o código consistente, legível e de fácil manutenção, o projeto adota os seguintes padrões e convenções.

### Estilo de Código

- **PEP 8:** Todo o código Python deve seguir as diretrizes da [PEP 8](https://www.python.org/dev/peps/pep-0008/). Recomenda-se o uso de linters como `Flake8` ou `Ruff` para garantir a conformidade.
- **Nomenclatura:**
  - **Modelos:** Nomes em `CamelCase` no singular (ex: `ContaBancaria`, `OperacaoSaque`).
  - **Views:** Nomes em `snake_case` (ex: `conta_list`, `profile_update_view`).
  - **Templates:** Nomes em `snake_case` (ex: `conta_list.html`, `confirm_delete_account.html`).
  - **URLs:** Nomes de rotas em `snake_case` (ex: `name='conta_list'`).

### Commits e Controle de Versão

- **Mensagens de Commit:** Siga o padrão [Conventional Commits](https://www.conventionalcommits.org/). Isso torna o histórico do Git mais legível e permite a geração automática de changelogs.
  - **Exemplos:**
    - `feat: Adiciona funcionalidade de lembretes`
    - `fix: Corrige cálculo de saldo em transferências`
    - `docs: Atualiza documentação da API de dashboard`
    - `refactor: Simplifica lógica da view de perfil`

### Estrutura de Templates

- **Herança:** Todos os templates devem herdar do template base `theme/templates/base.html` para manter a consistência visual.
- **Includes:** Componentes reutilizáveis, como modais e partes de formulários, devem ser separados em arquivos e incluídos com a tag `{% include %}`. O projeto já faz isso em `core/templates/core/includes/`.

### Variáveis de Ambiente

- **Nunca comitar `.env`:** O arquivo `.env` nunca deve ser adicionado ao controle de versão. O arquivo `.gitignore` já está configurado para ignorá-lo.
- **Manter `.env.example` atualizado:** Sempre que uma nova variável de ambiente for adicionada, ela deve ser incluída no arquivo `.env.example` com um valor de exemplo ou vazio.

### Respostas de API (JSON)

- **Padrão de Sucesso/Erro:** As respostas de API devem seguir o padrão de conter uma chave booleana `success` e, opcionalmente, `message` para feedback ao usuário ou `errors` para erros de validação.
  ```json
  // Sucesso
  { "success": true, "message": "Operação realizada." }

  // Erro
  { "success": false, "errors": { "field": ["error message"] } }
  ```
