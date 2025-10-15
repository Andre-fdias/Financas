# 📋 Guia de Versionamento e Conventional Commits

Este documento detalha o padrão de commits utilizado no projeto FinanceFlow, que alimenta nosso sistema de versionamento e changelog automáticos.

---

## CATÁLOGO COMPLETO DE TIPOS DE COMMIT

### 1. `feat`: Nova Funcionalidade
- **Quando usar:** Adicionar novas features ao sistema.
- **Impacto na versão:** ⬆️ **MINOR** (1.0.0 → 1.1.0)

**📝 Exemplos Práticos:**

- **Para Dashboard:**
  ```bash
  git commit -m "feat(dashboard): adiciona gráfico de evolução patrimonial"
  git commit -m "feat(dashboard): implementa cards de métricas rápidas"
  ```
- **Para Transferências:**
  ```bash
  git commit -m "feat(transferencias): implementa agendamento de transferências"
  git commit -m "feat(transferencias): adiciona confirmação por email para valores altos"
  ```
- **Para Relatórios:**
  ```bash
  git commit -m "feat(relatorios): adiciona exportação em PDF"
  git commit -m "feat(relatorios): implementa relatório comparativo mensal"
  ```
- **Para Sistema de Categorias:**
  ```bash
  git commit -m "feat(categorias): permite criação de categorias personalizadas"
  git commit -m "feat(categorias): implementa herança de subcategorias"
  ```

### 2. `fix`: Correção de Bug
- **Quando usar:** Corrigir comportamentos inesperados.
- **Impacto na versão:** ⬆️ **PATCH** (1.0.0 → 1.0.1)

**🐛 Exemplos de Bugs Comuns:**

- **Cálculos Financeiros:**
  ```bash
  git commit -m "fix: corrige cálculo de saldo residual no extrato"
  git commit -m "fix(calculos): corrige fórmula de juros compostos"
  ```
- **Problemas de Interface:**
  ```bash
  git commit -m "fix(ui): corrige sobreposição de modais no mobile"
  git commit -m "fix(ui): resolve alinhamento de tabelas responsivas"
  ```
- **Problemas de Dados:**
  ```bash
  git commit -m "fix: corrige duplicação de transações na importação"
  git commit -m "fix: corrige timezone em datas do extrato"
  ```
- **Validações:**
  ```bash
  git commit -m "fix(validacao): corrige validação de CPF/CNPJ"
  git commit -m "fix(validacao): corrige máscara de campos monetários"
  ```

### 3. `docs`: Documentação
- **Quando usar:** Atualizar ou adicionar documentação.
- **Impacto na versão:** 🔄 NENHUM

**📚 Exemplos:**

- **Documentação Técnica:**
  ```bash
  git commit -m "docs: atualiza README com instruções de deploy"
  git commit -m "docs: cria documentação da API REST"
  ```
- **Comentários de Código:**
  ```bash
  git commit -m "docs: adiciona docstrings nos models Django"
  git commit -m "docs: comenta funções complexas de cálculo"
  ```

### 4. `style`: Formatação
- **Quando usar:** Ajustes de formatação que não alteram lógica.
- **Impacto na versão:** 🔄 NENHUM

**🎨 Exemplos:**
```bash
git commit -m "style: aplica formatação black no código Python"
git commit -m "style: corrige indentação nos templates HTML"
git commit -m "style: ajusta espaçamento entre componentes"
```

### 5. `refactor`: Refatoração
- **Quando usar:** Melhorar código sem alterar funcionalidade.
- **Impacto na versão:** 🔄 NENHUM

**🔧 Exemplos:**
```bash
git commit -m "refactor: extrai lógica de cálculo para service layer"
git commit -m "refactor: remove código duplicado em views similares"
git commit -m "refactor: implementa repository pattern para queries"
```

### 6. `perf`: Performance
- **Quando usar:** Otimizações de velocidade/memória.
- **Impacto na versão:** 🔄 NENHUM

**⚡ Exemplos:**
```bash
git commit -m "perf: adiciona índices para consultas frequentes"
git commit -m "perf: otimiza queries do dashboard com select_related"
git commit -m "perf: implementa cache em métricas do dashboard"
```

### 7. `test`: Testes
- **Quando usar:** Adicionar ou modificar testes.
- **Impacto na versão:** 🔄 NENHUM

**✅ Exemplos:**
```bash
git commit -m "test: adiciona testes unitários para cálculos financeiros"
git commit -m "test: cria testes de integração para transferências"
git commit -m "test: refatora fixtures para serem mais realistas"
```

### 8. `chore`: Tarefas de Manutenção
- **Quando usar:** Atualizações de configuração, dependências, etc.
- **Impacto na versão:** 🔄 NENHUM

**🔩 Exemplos:**
```bash
git commit -m "chore: atualiza Django para versão 4.2.8"
git commit -m "chore: atualiza configurações do Docker"
git commit -m "chore: remove dependências não utilizadas"
```

---

## 🚨 Commits Especiais

### 9. `BREAKING CHANGE`: Mudanças que Quebram Compatibilidade
- **Quando usar:** Alterações que exigem ação do usuário/desenvolvedor.
- **Impacto na versão:** ⬆️ **MAJOR** (1.0.0 → 2.0.0)

**💥 Exemplos:**
```bash
git commit -m "feat: altera estrutura do modelo de categorias

BREAKING CHANGE: Remove campo 'tipo_antigo' do modelo Categoria, use 'novo_tipo'"
```
```bash
git commit -m "refactor: migra para novo schema de transações

BREAKING CHANGE: Modifica estrutura da tabela 'transacoes', requer migração manual"
```

---

## 🔄 Fluxos de Trabalho Práticos

### Cenário 1: Nova Funcionalidade Completa
**Branch:** `feat/novo-dashboard`
```bash
# 1. Desenvolvimento inicial
git commit -m "feat(dashboard): adiciona estrutura básica do componente"
# 2. Integração com backend
git commit -m "feat(dashboard): conecta com API de métricas"
# 3. Estilização
git commit -m "style(dashboard): aplica design responsivo"
# 4. Testes
git commit -m "test(dashboard): adiciona testes de renderização"
# 5. Documentação
git commit -m "docs(dashboard): cria documentação do componente"
```

### Cenário 2: Correção de Bug Complexo
**Branch:** `fix/calculos-financeiros`
```bash
# 1. Identificar problema
git commit -m "fix: corrige cálculo de juros em parcelamentos"
# 2. Refatorar para prevenir futuros erros
git commit -m "refactor: extrai lógica de cálculo para classe dedicada"
# 3. Adicionar testes específicos
git commit -m "test: adiciona casos de borda para cálculos"
```

---

## 🎨 Escopos Recomendados para FinanceFlow

| Escopo          | Descrição                  | Exemplos                          |
|-----------------|----------------------------|-----------------------------------|
| `dashboard`     | Painel principal           | `feat(dashboard):`, `fix(dashboard):` |
| `transferencias`| Sistema de transferências  | `feat(transferencias):`, `fix(transferencias):` |
| `entradas`      | Sistema de receitas        | `feat(entradas):`, `fix(entradas):` |
| `saidas`        | Sistema de despesas        | `feat(saidas):`, `fix(saidas):` |
| `categorias`    | Gestão de categorias       | `feat(categorias):`, `fix(categorias):` |
| `relatorios`    | Sistema de relatórios      | `feat(relatorios):`, `fix(relatorios):` |
| `auth`          | Autenticação e usuários    | `feat(auth):`, `fix(auth):` |
| `ui`            | Interface do usuário       | `style(ui):`, `fix(ui):` |
| `api`           | API REST                   | `feat(api):`, `fix(api):` |

---

## ⚠️ Checklist Antes do Commit

- [ ] Mensagem segue padrão `conventional commits`.
- [ ] Tipo correto para o tipo de mudança.
- [ ] Escopo aplicável quando relevante.
- [ ] Descrição clara e objetiva.
- [ ] Corpo explicativo para mudanças complexas (opcional).
- [ ] Rodapé `BREAKING CHANGE:` quando necessário.

### Comandos Úteis:
```bash
# Verificar status antes do commit
git status

# Ver diferenças
git diff

# Adicionar arquivos específicos
git add caminho/do/arquivo.py

# Commit com mensagem
git commit -m "tipo(escopo): descrição clara"

# Corrigir último commit (antes de fazer push)
git commit --amend -m "nova mensagem correta"
```
