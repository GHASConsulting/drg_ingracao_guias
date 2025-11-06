# Dockerfile para Sistema DRG FastAPI
FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    wget \
    unzip \
    libaio1t64 \
    libaio-dev \
    libc6 \
    && rm -rf /var/lib/apt/lists/*

# Criar link simbólico para libaio.so.1
RUN ln -sf /usr/lib/x86_64-linux-gnu/libaio.so.1t64 /usr/lib/x86_64-linux-gnu/libaio.so.1

# Criar diretório para o Oracle Instant Client
RUN mkdir -p /opt/oracle

# Instalar Oracle Instant Client
RUN cd /tmp && \
    wget https://download.oracle.com/otn_software/linux/instantclient/2117000/instantclient-basic-linux.x64-21.17.0.0.0dbru.zip && \
    unzip instantclient-basic-linux.x64-21.17.0.0.0dbru.zip -d /opt/oracle/ && \
    rm instantclient-basic-linux.x64-21.17.0.0.0dbru.zip

# Configurar variáveis de ambiente Oracle
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_21_17 \
    TNS_ADMIN=/opt/oracle/instantclient_21_17 \
    ORACLE_LIB_DIR=/opt/oracle/instantclient_21_17

# Copiar requirements primeiro (para cache de layers)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretório de logs
RUN mkdir -p logs

# Expor porta (padrão, pode ser sobrescrita via variável de ambiente)
EXPOSE 8000

# Definir variável de ambiente para desenvolvimento
ENV PYTHONUNBUFFERED=1

# Comando para iniciar a aplicação (porta vem do .env via PORT ou padrão 8000)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
