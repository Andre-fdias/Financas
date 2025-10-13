FROM nginx:1.25-alpine

# Remover a configuração padrão
RUN rm /etc/nginx/conf.d/default.conf

# Copiar a nova configuração
COPY nginx.conf /etc/nginx/conf.d/