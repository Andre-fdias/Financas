# Use a imagem oficial do Python
FROM python:3.9-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de dependências
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação
COPY . .

# Expõe a porta que o Gunicorn irá rodar
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "financas.wsgi:application"]

# --- Build Tailwind CSS ---
# Install npm dependencies
WORKDIR /app/theme/static_src
RUN npm install

# Build the CSS
RUN npm run build

# --- Django Setup ---
# Switch back to the app root
WORKDIR /app

# Change ownership of all files to the app user
RUN chown -R app:app /app

# Change to non-root user
USER app

# Collect static files (now includes the built CSS)
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "financas.wsgi:application"]