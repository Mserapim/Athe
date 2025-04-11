FROM python:3.10-slim

WORKDIR /app
COPY . /app

# Instala dependências se existir requirements.txt
RUN test -f requirements.txt && pip install --no-cache-dir -r requirements.txt || echo "No requirements.txt found"

# Dá permissão de execução ao script
RUN chmod +x /app/configure

# Executa o script corretamente via caminho absoluto
CMD ["/app/configure"]
