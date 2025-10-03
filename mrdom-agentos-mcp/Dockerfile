# MrDom SDR AgentOS + Bedrock Dockerfile
FROM python:3.11-slim

# Metadados
LABEL maintainer="DOM-360 <contato@dom360.com.br>"
LABEL description="Sistema de automação de vendas com agentes inteligentes usando AgentOS e AWS Bedrock"
LABEL version="1.0.0"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Cria usuário não-root
RUN groupadd -r mrdom && useradd -r -g mrdom mrdom

# Define diretório de trabalho
WORKDIR /app

# Copia arquivos de dependências
COPY requirements.txt pyproject.toml ./

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia código fonte
COPY src/ ./src/
COPY main.py ./
COPY env.example .env

# Cria diretórios necessários
RUN mkdir -p /app/logs /app/data && \
    chown -R mrdom:mrdom /app

# Muda para usuário não-root
USER mrdom

# Expõe porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Comando padrão
CMD ["python", "main.py"]
