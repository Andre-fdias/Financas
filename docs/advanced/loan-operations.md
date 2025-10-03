# Operações de Saque e Empréstimos

Este módulo é destinado ao rastreamento de operações de crédito mais complexas, como empréstimos ou adiantamentos (saque-aniversário do FGTS, etc.), que envolvem parcelas e taxas.

### Modelo `OperacaoSaque`

O modelo `core.models.OperacaoSaque` armazena os detalhes dessas operações:

- `proprietario`: `ForeignKey` para o `User`.
- `nome_banco`: A instituição financeira.
- `tipo_operacao`: `CharField` com `choices` para definir o tipo (ex: 'Empréstimo Pessoal', 'Saque FGTS').
- `data_contratacao`: Data em que a operação foi realizada.
- `valor_saque`: O valor total da operação.
- `valor_financiado`, `valor_iof`: Campos para detalhar custos.
- `valor_liberado_cliente`: O valor líquido que o cliente recebeu.
- **Detalhes do Parcelamento:**
  - `quantidade_parcelas`
  - `valor_parcela`
  - `data_inicio_parcelas`
  - `data_termino_parcelas`

### Lógica de Negócio

O método `save()` do modelo contém uma lógica para calcular automaticamente a data de término do parcelamento se a data de início e a quantidade de parcelas forem fornecidas, utilizando a biblioteca `dateutil`.

```python
# Em core/models.py
from dateutil.relativedelta import relativedelta

class OperacaoSaque(models.Model):
    # ...
    def save(self, *args, **kwargs):
        # ...
        if self.data_inicio_parcelas and self.quantidade_parcelas:
            self.data_termino_parcelas = self.data_inicio_parcelas + relativedelta(months=self.quantidade_parcelas)
        
        super().save(*args, **kwargs)
```

### Interface de Gerenciamento

A página `/operacoes-saque/` (`operacao_saque_list`) permite ao usuário visualizar e gerenciar todas as suas operações de saque.

- **Listagem e Filtros:** As operações são listadas e podem ser filtradas por ano, mês e tipo de operação.
- **Estatísticas:** Cards no topo da página exibem o valor total sacado, o valor médio por operação e o total líquido liberado ao cliente.
- **CRUD via AJAX:** Assim como outros módulos do sistema, a criação, edição e exclusão de operações são feitas através de modais e requisições AJAX, proporcionando uma experiência de usuário ágil.
