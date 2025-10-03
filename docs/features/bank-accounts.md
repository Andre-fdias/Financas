# Cadastro e Gerenciamento de Contas Bancárias

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
