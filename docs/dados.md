# Modelagem de Dados

Esta seção detalha a estrutura do banco de dados, os modelos do Django e os relacionamentos entre as entidades do sistema FinanceFlow.

## Diagrama de Classes Principal

O diagrama a seguir ilustra as principais entidades do sistema e como elas se interconectam. Ele foi gerado a partir dos modelos definidos em `core/models.py`.

```mermaid
classDiagram
    direction LR

    class User {
        +username
        +email
    }

    class Profile {
        +foto_perfil
        +theme
    }

    class ContaBancaria {
        +nome_banco
        +tipo
        +saldo_atual
        +limite_cartao
    }

    class Categoria {
        +nome
    }

    class Subcategoria {
        +nome
    }

    class Entrada {
        +nome
        -valor
        +data
    }

    class Saida {
        +nome
        -valor
        +data_vencimento
        +quantidade_parcelas
    }

    class Transferencia {
        -valor
        +data
    }

    class Lembrete {
        +titulo
        +data_limite
        +concluido
    }

    class OperacaoSaque {
        +tipo_operacao
        +valor_saque
    }

    %% Relacionamentos
    User "1" -- "1" Profile : possui
    User "1" -- "0..*" ContaBancaria : é proprietário de
    User "1" -- "0..*" Categoria : cria
    User "1" -- "0..*" Subcategoria : cria
    User "1" -- "0..*" Entrada : realiza
    User "1" -- "0..*" Saida : realiza
    User "1" -- "0..*" Transferencia : realiza
    User "1" -- "0..*" Lembrete : cria
    User "1" -- "0..*" OperacaoSaque : realiza

    Categoria "1" -- "0..*" Subcategoria : contém

    ContaBancaria "1" -- "0..*" Entrada : recebe em
    ContaBancaria "1" -- "0..*" Saida : sai de
    Transferencia -- "1" ContaBancaria : tem origem em
    Transferencia -- "1" ContaBancaria : tem destino em

    Saida "1" -- "0..*" Saida : é parcela de
```
