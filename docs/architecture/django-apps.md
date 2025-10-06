# Estrutura de Apps Django

O projeto é organizado em apps Django para modularizar as funcionalidades e responsabilidades.

### `core`

Este é o app principal e o coração da aplicação. Ele contém toda a lógica de negócio do sistema financeiro.

- **`models.py`**: Define todos os modelos de dados, como `ContaBancaria`, `Entrada`, `Saida`, `Transferencia`, `Profile`, etc.
- **`views.py`**: Contém a lógica para renderizar as páginas, processar formulários e servir as APIs AJAX. É aqui que a maior parte da funcionalidade reside.
- **`forms.py`**: Define os formulários do Django para criação e edição de dados, garantindo a validação.
- **`urls.py`**: Mapeia todas as URLs da aplicação para as suas respectivas views.
- **`choices.py`**: Centraliza todas as opções de `choices` usadas nos modelos (ex: `BANCO_CHOICES`, `TIPO_CONTA_CHOICES`), promovendo a reutilização e a fácil manutenção.
- **`templates/`**: Contém os templates HTML específicos do app `core`.

### `theme`

Este app é responsável pela gestão do tema e dos assets de frontend.

- **`static/`**: Onde os arquivos estáticos compilados (CSS, JS, imagens) são armazenados.
- **`static_src/`**: Contém os arquivos fonte do frontend, incluindo o `styles.css` principal do Tailwind CSS.
- **`templates/`**: Inclui o template base (`base.html`) que é estendido por todos os outros templates da aplicação, garantindo uma aparência consistente.
- **`tailwind.config.js`**: Arquivo de configuração do Tailwind CSS.

### `financas`

Este é o diretório de configuração do projeto Django.

- **`settings.py`**: Arquivo principal de configurações do projeto.
- **`urls.py`**: O arquivo de roteamento raiz, que inclui as URLs do app `core`.
