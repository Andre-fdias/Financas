# Estágio 1: Build dos assets de frontend (Tailwind CSS)
FROM node:18-slim as frontend-builder

WORKDIR /app/theme/static_src
COPY theme/static_src/package.json theme/static_src/package-lock.json ./
RUN npm install

COPY theme/static_src/ ./
RUN npm run build

# Estágio 2: Build da aplicação Python/Django
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependências do sistema para compilar pacotes (ex: pycairo)
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libcairo2-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala as dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Copia os assets construídos do estágio anterior
COPY --from=frontend-builder /app/theme/static/css/dist/styles.css theme/static/css/styles.css

# Coleta os arquivos estáticos do Django
RUN SECRET_KEY=dummy-key-for-build-only python manage.py collectstatic --noinput

# Expõe a porta
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "financas.wsgi:application"]
