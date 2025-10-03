# Testes Automatizados

Testes automatizados são cruciais para garantir a qualidade, a estabilidade e a manutenibilidade do projeto, especialmente por se tratar de uma aplicação financeira onde a precisão dos dados é fundamental.

O projeto utiliza o framework de testes nativo do Django.

### Localização dos Testes

Os testes para o app `core` estão localizados no arquivo `core/tests.py`.

### Como Executar os Testes

Para rodar a suíte de testes completa, utilize o seguinte comando na raiz do projeto:

```bash
python manage.py test
```

Para executar os testes de um app específico:

```bash
python manage.py test core
```

### Estrutura de Testes Sugerida

A documentação e os testes devem cobrir, no mínimo, as seguintes áreas:

1.  **Testes de Modelos (`Model Tests`):**
    - Verificar se os valores padrão (`default`) são aplicados corretamente.
    - Testar a lógica customizada nos métodos `save()` e `clean()`. Por exemplo, testar se a `Transferencia.save()` realmente atualiza os saldos das contas corretamente.
    - Validar as relações entre modelos.

    ```python
    # Exemplo de teste para o método save de Transferencia
    from django.test import TestCase
    from .models import ContaBancaria, Transferencia

    class TransferenciaModelTest(TestCase):
        def test_transferencia_atualiza_saldos(self):
            conta_origem = ContaBancaria.objects.create(proprietario=self.user, saldo_atual=1000)
            conta_destino = ContaBancaria.objects.create(proprietario=self.user, saldo_atual=500)

            Transferencia.objects.create(
                usuario=self.user,
                conta_origem=conta_origem,
                conta_destino=conta_destino,
                valor=200
            )

            conta_origem.refresh_from_db()
            conta_destino.refresh_from_db()

            self.assertEqual(conta_origem.saldo_atual, 800)
            self.assertEqual(conta_destino.saldo_atual, 700)
    ```

2.  **Testes de Views (`View Tests`):**
    - Garantir que as páginas que exigem login redirecionem usuários anônimos.
    - Testar se as views de listagem (`_list`) retornam o status code 200 e usam o template correto.
    - Verificar se as views de criação/edição processam dados de formulário válidos e inválidos corretamente (tanto para requisições normais quanto para AJAX).
    - Testar a lógica de negócio dentro das views, como os cálculos no `dashboard`.

3.  **Testes de Formulários (`Form Tests`):**
    - Testar as regras de validação customizadas dos formulários.
