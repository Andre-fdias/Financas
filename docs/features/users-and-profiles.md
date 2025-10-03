# Autenticação e Perfis de Usuário

O sistema possui um fluxo completo de autenticação e gerenciamento de perfis, utilizando o sistema de autenticação nativo do Django e estendendo-o com um modelo de perfil personalizado.

### Fluxo de Autenticação

- **Registro:** Novos usuários podem se registrar através da página `/register`. A view `core.views.register` utiliza o `CustomUserCreationForm` para criar um novo `User`.
- **Login:** A autenticação é feita na página `/login`, usando a `LoginView` nativa do Django. Após o login, o usuário é redirecionado para o `dashboard`.
- **Logout:** A rota `/logout` (`custom_logout`) encerra a sessão do usuário e exibe uma mensagem de sucesso.
- **Reset de Senha:** O fluxo completo de recuperação de senha está implementado usando as views nativas do Django (`PasswordResetView`, etc.), com templates personalizados.

### Perfil do Usuário (`Profile`)

O modelo `Profile` (`core/models.py`) estende o modelo `User` com uma relação `OneToOneField` para armazenar informações adicionais.

- **Campos Principais:**
  - `foto_perfil`: `ImageField` para a foto do usuário. O sistema redimensiona a imagem para 300x300 pixels no upload e remove a foto antiga para economizar espaço.
  - `theme`: Permite que o usuário escolha um tema (`light`, `dark`, `auto`).
  - `login_streak`, `total_logins`: Campos para gamificação, rastreando a frequência de acesso.

### Gerenciamento de Perfil

A página de perfil (`/profile/`) permite ao usuário:

- **Atualizar Informações:** Alterar nome, sobrenome e e-mail através do `UserUpdateForm`.
- **Alterar Foto:** Fazer upload de uma nova foto de perfil ou remover a foto existente (`ProfileUpdateForm`).
- **Mudar Senha:** Alterar a senha de forma segura (`PasswordChangeForm`).
- **Excluir Conta:** Uma opção para excluir permanentemente a conta, com uma etapa de confirmação para segurança.

### APIs Relacionadas

Diversas ações no perfil são realizadas via AJAX para uma melhor experiência do usuário:

- `POST /api/profile/update-info/`: Atualiza dados básicos do usuário.
- `POST /api/profile/update-photo/`: Atualiza a foto de perfil.
- `GET /api/profile/statistics/`: Fornece dados para um painel de estatísticas do usuário (dias de acesso, etc.).
