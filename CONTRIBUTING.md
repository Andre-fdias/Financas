# Como Contribuir para o FinanceFlow

Ficamos muito felizes com o seu interesse em contribuir! Toda ajuda é bem-vinda, desde a correção de bugs e melhoria na documentação até a sugestão de novas funcionalidades.

Para garantir um ambiente colaborativo e organizado, por favor, siga as diretrizes abaixo.

## Código de Conduta

Esperamos que todos os contribuidores sigam o nosso [Código de Conduta](CODE_OF_CONDUCT.md). Por favor, seja respeitoso e construtivo em todas as interações.

## Como Você Pode Ajudar

### Reportando Bugs

Se você encontrar um bug, por favor, abra uma **Issue** no GitHub com as seguintes informações:

- Uma descrição clara e concisa do bug.
- Passos para reproduzir o comportamento.
- O comportamento esperado.
- O que de fato acontece.
- Screenshots, se aplicável.
- Informações do seu ambiente (versão do sistema operacional, navegador, etc.).

### Sugerindo Melhorias e Novas Funcionalidades

Se você tem uma ideia para uma nova funcionalidade ou uma melhoria, abra uma **Issue** com a tag `enhancement`. Descreva sua ideia em detalhes, explicando o problema que ela resolve e como ela beneficiaria os usuários.

## Processo de Pull Request (PR)

Para contribuir com código, por favor, siga este processo:

1.  **Faça um Fork** do repositório para a sua conta no GitHub.

2.  **Clone o seu fork** para a sua máquina local:
    ```bash
    git clone https://github.com/seu-usuario/FinanceFlow.git
    ```

3.  **Crie uma nova Branch** para a sua alteração. Use um nome descritivo (ex: `feature/adiciona-grafico-pizza` ou `fix/corrige-bug-login`).
    ```bash
    git checkout -b nome-da-sua-branch
    ```

4.  **Faça suas alterações** no código. Siga os padrões de estilo do projeto:
    - **Python/Django:** Usamos `black` para formatação e `flake8` para linting. Certifique-se de que seu código está em conformidade.
    - **JavaScript/CSS:** Siga os padrões existentes nos arquivos.

5.  **Adicione Testes:** Se você está adicionando uma nova funcionalidade ou corrigindo um bug, por favor, adicione testes que cubram suas alterações.

6.  **Garanta que todos os testes passem:**
    ```bash
    pytest
    ```

7.  **Faça o Commit** das suas alterações com uma mensagem clara e concisa.
    ```bash
    git commit -m "feat: Adiciona nova funcionalidade X"
    # ou
    git commit -m "fix: Corrige bug Y na validação Z"
    ```

8.  **Envie suas alterações** para o seu fork no GitHub:
    ```bash
    git push origin nome-da-sua-branch
    ```

9.  **Abra um Pull Request** no repositório original do FinanceFlow. Preencha o template do PR com uma descrição clara do que você fez e por quê.

Após o envio, um dos mantenedores do projeto irá revisar seu PR. Podemos pedir algumas alterações antes de integrar o seu código. Agradecemos sua paciência e colaboração durante este processo.

Obrigado por ajudar a tornar o FinanceFlow ainda melhor!
