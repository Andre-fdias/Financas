# APIs e Integração AJAX

Uma característica central da arquitetura do sistema é o uso intensivo de AJAX para criar uma interface de usuário dinâmica e reativa, minimizando recarregamentos de página. Isso é alcançado através de uma combinação de views que respondem com JSON e JavaScript/HTMX no frontend.

### Padrão de Views de API

A maioria das views que interagem com AJAX segue um padrão:

1.  Verifica se a requisição é do tipo AJAX checando o cabeçalho `X-Requested-With`.
    ```python
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Lógica para AJAX
    ```
2.  Processa os dados do formulário (`request.POST`).
3.  Se o formulário for válido, executa a ação e retorna um `JsonResponse` com `success: True`.
4.  Se o formulário for inválido, retorna um `JsonResponse` com `success: False` e um dicionário de `errors`.

### Exemplo de Resposta de Sucesso

Usado para notificar o frontend que a operação foi concluída.

`POST /entradas/nova/`
```json
{
  "success": true,
  "message": "Entrada criada com sucesso!"
}
```

### Exemplo de Resposta de Erro de Validação

Usado para que o frontend possa exibir os erros de validação de formulário perto dos campos correspondentes.

`POST /saidas/nova/`
```json
{
  "success": false,
  "errors": {
    "valor": ["Este campo é obrigatório."],
    "data_vencimento": ["Insira uma data válida."]
  }
}
```

### Endpoints de API Notáveis

Além das views de CRUD que respondem a AJAX, existem endpoints que funcionam puramente como APIs de dados:

- **`GET /api/transacao/<int:pk>/detalhes/`**: Retorna o HTML de um modal com os detalhes de uma transação específica (`Entrada` ou `Saida`).
- **`GET /api/profile/statistics/`**: Fornece dados numéricos e textuais sobre a atividade do usuário para popular um painel de estatísticas.
- **`GET /get-account-balance/<int:pk>/`**: Retorna o saldo atual de uma conta, útil para atualizar valores na interface após uma operação.
- **`POST /saidas/<int:saida_id>/marcar-pago/`**: Endpoint de ação que altera o status de uma despesa para "pago".
