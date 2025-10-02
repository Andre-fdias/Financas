# Choices e Constantes

Para garantir a consistência dos dados e facilitar a manutenção, o projeto centraliza as opções de múltipla escolha (`choices`) em um único arquivo: `core/choices.py`.

Isso evita a repetição de listas de tuplas nos arquivos de modelos e formulários, tornando o código mais limpo e fácil de atualizar.

### Estrutura

O arquivo `core/choices.py` contém diversas listas de tuplas, seguindo o padrão do Django:

```python
# Exemplo de core/choices.py

BANCO_CHOICES = [
    ('BB', 'Banco do Brasil'),
    ('BBDC', 'Bradesco'),
    ('ITAU', 'Itaú Unibanco'),
    ('NU', 'Nubank'),
    # ... outros bancos
]

TIPO_CONTA_CHOICES = [
    ('corrente', 'Conta Corrente'),
    ('poupanca', 'Conta Poupança'),
    ('credito', 'Cartão de Crédito'),
    ('investimento', 'Investimento'),
    ('outros', 'Outros'),
]

SITUACAO_CHOICES = [
    ('pago', 'Pago'),
    ('pendente', 'Pendente'),
]

# ... e assim por diante para outras constantes.
```

### Utilização

Essas constantes são importadas e utilizadas nos modelos e formulários.

**Nos Modelos (`core/models.py`):**

```python
from .choices import BANCO_CHOICES, TIPO_CONTA_CHOICES

class ContaBancaria(models.Model):
    nome_banco = models.CharField(max_length=20, choices=BANCO_CHOICES)
    tipo = models.CharField(max_length=20, choices=TIPO_CONTA_CHOICES)
    # ...
```

**Nos Formulários (`core/forms.py`):**

As `choices` são usadas diretamente pelos campos do formulário, que são derivados dos campos do modelo.

### Vantagens desta Abordagem

1.  **Ponto Único de Verdade (Single Source of Truth):** Para adicionar um novo banco ou um novo tipo de conta, basta editar o arquivo `core/choices.py`. A mudança se refletirá em todos os lugares onde a constante é usada.
2.  **Legibilidade:** Mantém os arquivos de modelos e formulários mais limpos e focados em sua estrutura principal.
3.  **Manutenibilidade:** Reduz o risco de erros e inconsistências que podem ocorrer ao manter listas duplicadas em vários locais.
