# Transferências Internas e Regras de Consistência de Saldos

A funcionalidade de transferência permite ao usuário mover fundos entre suas próprias contas cadastradas. A principal preocupação nesta operação é garantir a **atomicidade** e a **consistência** dos saldos.

### Modelo `Transferencia`

O modelo `core.models.Transferencia` é composto por:

- `usuario`: O usuário que realiza a transferência.
- `conta_origem`: `ForeignKey` para `ContaBancaria` de onde o dinheiro sai.
- `conta_destino`: `ForeignKey` para `ContaBancaria` para onde o dinheiro vai.
- `valor`: `DecimalField` com o montante da transferência.
- `data`: A data em que a transferência foi realizada.

### Garantia de Atomicidade

Uma transferência envolve duas operações de atualização no banco de dados: subtrair o saldo da conta de origem e adicionar o saldo à conta de destino. Se uma dessas operações falhar, a outra não pode ser concluída, pois isso deixaria os dados em um estado inconsistente (dinheiro "desapareceria" ou seria "criado" do nada).

Para resolver isso, todas as views que manipulam transferências (`transferencia_create`, `transferencia_update`, `transferencia_delete`) são decoradas com `@transaction.atomic`.

```python
from django.db import transaction

@login_required
@transaction.atomic
def transferencia_create(request):
    # ... lógica da view ...
```

Este decorador garante que todas as operações de banco de dados dentro da view sejam executadas em uma única transação. Se qualquer erro ocorrer, a transação inteira sofre um *rollback*, e nenhuma alteração é salva no banco de dados.

### Lógica de Atualização de Saldo

A lógica de negócio para atualizar os saldos reside no método `save()` do modelo `Transferencia`.

```python
# Em core/models.py
class Transferencia(BaseModel):
    # ... campos ...

    def save(self, *args, **kwargs):
        # A lógica só é aplicada para novas transferências
        if not self.pk:
            # Atualiza os saldos das contas
            self.conta_origem.saldo_atual -= self.valor
            self.conta_destino.saldo_atual += self.valor
            
            self.conta_origem.save()
            self.conta_destino.save()
        
        super().save(*args, **kwargs)
```

- Ao **criar** uma transferência, o saldo é debitado da origem e creditado no destino.
- Ao **excluir**, a view `transferencia_delete` executa a lógica inversa: o valor é devolvido à conta de origem e removido da conta de destino antes de a transferência ser apagada.
- A **atualização** é a operação mais complexa: ela primeiro reverte a transação antiga e depois aplica a nova, tudo dentro de um bloco `atomic`.
