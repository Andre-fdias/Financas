# FAQ e Troubleshooting

### Perguntas Frequentes (FAQ)

**P: Como adiciono um novo banco à lista de opções?**

R: Edite o arquivo `core/choices.py` e adicione uma nova tupla à lista `BANCO_CHOICES`. O sistema o refletirá automaticamente nos formulários.

**P: Por que a projeção no dashboard não aparece?**

R: A projeção de saldo futuro requer um mínimo de 3 meses de dados de receitas e despesas para que o modelo de regressão linear possa ser treinado. Continue usando o sistema e ela aparecerá quando houver dados suficientes.

**P: Posso usar o sistema com outro banco de dados, como PostgreSQL ou MySQL?**

R: Sim. O projeto usa `dj_database_url` para configurar o banco de dados a partir de uma URL. Para usar PostgreSQL, por exemplo, instale o driver (`psycopg2-binary`) e configure a variável `DATABASE_URL` no seu arquivo `.env` para `postgres://USER:PASSWORD@HOST:PORT/NAME`.

### Solução de Problemas (Troubleshooting)

**Erro: `SECRET_KEY` não definida.**

- **Causa:** Você não criou ou não preencheu o arquivo `.env`.
- **Solução:** Copie o arquivo `.env.example` para `.env` (`cp .env.example .env`) e gere uma nova chave secreta para a variável `SECRET_KEY`.

**Erro: Imagens não aparecem ou quebram após o upload.**

- **Causa:** A configuração para servir arquivos de mídia em desenvolvimento pode estar faltando.
- **Solução:** Garanta que o `financas/urls.py` principal contenha a configuração para servir arquivos de mídia em modo `DEBUG`, e que as variáveis `MEDIA_URL` e `MEDIA_ROOT` em `settings.py` estejam corretas.
  ```python
  # Em financas/urls.py
  if settings.DEBUG:
      urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
  ```

**Erro: Estilos (CSS) não são aplicados.**

- **Causa:** O processo de compilação do Tailwind CSS pode não ter sido executado ou falhou.
- **Solução:** Rode o comando de compilação do Tailwind, que geralmente é gerenciado pelo `django-tailwind`.
  ```bash
  python manage.py tailwind build
  ```
  Para desenvolvimento, você pode rodar o processo em modo de observação:
  ```bash
  python manage.py tailwind start
  ```
