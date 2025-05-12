FROM python:3.11-slim

# Evita prompts interativos
ENV DEBIAN_FRONTEND=noninteractive

# Instala dependências básicas do sistema
RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia a aplicação
COPY . /app
WORKDIR /app

# Copia arquivos específicos
COPY src/ src/
COPY tests/ tests/
COPY .env .env

# Expose a porta
EXPOSE 8000

# Permite saída imediata no log
ENV PYTHONUNBUFFERED=1
ENV ENV_FILE=.env

# Comando para subir a aplicação
CMD ["uvicorn", "src.automation.app:app", "--host", "0.0.0.0", "--port", "8000"]