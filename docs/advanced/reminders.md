# Gestão de Lembretes Financeiros

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
