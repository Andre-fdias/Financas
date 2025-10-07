# syntax=docker/dockerfile:1

# Base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies including Node.js and npm
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN addgroup --system app && adduser --system --group app

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

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