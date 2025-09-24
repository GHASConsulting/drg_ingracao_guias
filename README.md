# 🏥 Sistema DRG - Guias de Internação

Sistema para processamento automático e envio de guias de internação para a API DRG Brasil usando FastAPI.

## ✨ **Características Principais**

- 🚀 **FastAPI** - Framework moderno e rápido
- 🗄️ **Multi-banco** - Oracle, PostgreSQL, SQLite
- 🤖 **Monitoramento Automático** - Processa guias em lote (até 10 por vez)
- 📊 **Logs Detalhados** - Rastreamento completo de operações
- 🐳 **Docker Ready** - Deploy simplificado
- 📋 **API REST** - Endpoints completos para integração

## 📚 **Documentação**

- 📄 **API Routes** - Rotas e endpoints
- 🧪 **Testes** - Como testar a API
- 📊 **Monitoramento** - Logs e monitoramento automático

## 🚀 **Instalação Rápida**

### **🐳 Opção 1: Docker (Recomendado)**

```bash
# 1. Clone o repositório
git clone https://github.com/GHASConsulting/drg_ingracao_guias.git
cd drg_guias

# 2. Configure o ambiente
cp env.example .env
# Edite o .env com suas configurações

# 3. Execute com Docker
docker-compose up --build
```

**Acesse:** http://localhost:8000/docs

### **🐍 Opção 2: Python Local**

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd drg_guias

# 2. Configure ambiente Python
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure variáveis
cp env.example .env
# Edite o .env conforme necessário

# 5. Execute a aplicação
python main.py
```

## ⚙️ **Configuração**

### **📋 Arquivo .env**

```bash
# Copiar exemplo
cp env.example .env
```

**Configurações essenciais:**

```env
# Ambiente
DEVELOPMENT=True          # True=dev, False=produção
DATABASE_TYPE=sqlite      # sqlite, oracle, postgresql

# Oracle (Produção)
DATABASE_TYPE=oracle
ORACLE_HOST=servidor_oracle
ORACLE_PORT=1521
ORACLE_SID=XE
ORACLE_USERNAME=usuario
ORACLE_PASSWORD=senha
ORACLE_DIR=/opt/oracle/instantclient_21_17

# DRG API
DRG_USERNAME=seu_usuario
DRG_PASSWORD=sua_senha
DRG_API_KEY=sua_chave

# Monitoramento Automático
AUTO_MONITOR_ENABLED=True
MONITOR_INTERVAL_MINUTES=5
```

### **🗄️ Bancos Suportados**

- **SQLite** - Desenvolvimento e testes
- **Oracle** - Produção (com Instant Client)
- **PostgreSQL** - Alternativa de produção
- **Firebird** - Suporte completo

## 🐳 **Docker**

### **📋 Pré-requisitos**

```bash
# Verificar se Docker está instalado
docker --version
docker-compose --version

# Se não estiver instalado, instale o Docker Desktop:
# https://www.docker.com/products/docker-desktop/
```

### **🚀 Comandos Docker Completos**

#### **1. Desenvolvimento (SQLite)**

```bash
# Parar containers existentes (se houver)
docker-compose down

# Construir e iniciar containers
docker-compose up --build

# Executar em background (detached)
docker-compose up --build -d

# Ver logs em tempo real
docker-compose logs -f

# Parar containers
docker-compose down
```

#### **2. Produção (Oracle)**

```bash
# 1. Configurar .env para Oracle
DATABASE_TYPE=oracle
ORACLE_HOST=servidor_oracle
ORACLE_PORT=1521
ORACLE_SID=XE
ORACLE_USERNAME=usuario
ORACLE_PASSWORD=senha
ORACLE_DIR=/opt/oracle/instantclient_21_17

# 2. Construir e executar
docker-compose up --build -d

# 3. Verificar se está funcionando
docker-compose ps
docker-compose logs drg-api
```

#### **3. Com PostgreSQL**

```bash
# Usar profile production (inclui PostgreSQL)
docker-compose --profile production up --build -d

# Verificar containers
docker-compose --profile production ps

# Ver logs
docker-compose --profile production logs
```

### **🔧 Comandos Úteis**

```bash
# Entrar no container da aplicação
docker-compose exec drg-api bash

# Ver logs da aplicação
docker-compose logs drg-api

# Reiniciar apenas a aplicação
docker-compose restart drg-api

# Reconstruir apenas a aplicação
docker-compose up --build drg-api

# Limpar tudo (cuidado!)
docker-compose down -v
docker system prune -f
```

### **📊 Monitoramento Docker**

```bash
# Ver status dos containers
docker-compose ps

# Ver uso de recursos
docker stats

# Ver logs em tempo real
docker-compose logs -f drg-api

# Verificar saúde da aplicação
docker-compose exec drg-api curl http://localhost:8000/api/v1/health
```

### **🆘 Troubleshooting Docker**

#### **Problemas Comuns:**

```bash
# Container não inicia
docker-compose logs drg-api

# Porta 8000 já está em uso
# Pare outros serviços ou mude a porta no docker-compose.yml

# Erro de permissão (Linux/Mac)
sudo docker-compose up --build

# Limpar cache do Docker
docker-compose down
docker system prune -f
docker-compose up --build

# Reconstruir do zero
docker-compose down -v
docker rmi $(docker images -q)
docker-compose up --build

# Verificar se .env existe
ls -la .env
cp env.example .env
```

#### **Verificações:**

```bash
# Verificar se Docker está rodando
docker ps

# Verificar se porta 8000 está livre
# Windows: netstat -an | findstr 8000
# Linux/Mac: lsof -i :8000

# Testar conectividade
curl http://localhost:8000/api/v1/health
```

## 🧪 **Testes**

```bash
# Teste completo da API
python tests/testar_api.py

# Teste DRG com logs
python tests/testar_drg_com_logs.py

# Teste de monitoramento
python tests/testar_monitoramento.py

# Adicionar dados de teste
python tests/adicionar_guias.py
```

## 📊 **Monitoramento**

### **🤖 Monitoramento Automático**

O sistema monitora automaticamente a tabela de guias e processa **até 10 guias por vez em lote** para otimizar performance:

```bash
# Verificar status
curl http://localhost:8000/api/v1/monitoramento/status

# Iniciar monitoramento
curl -X POST http://localhost:8000/api/v1/monitoramento/start

# Parar monitoramento
curl -X POST http://localhost:8000/api/v1/monitoramento/stop
```

### **📋 Logs**

- **Logs da aplicação:** `logs/app.log`
- **Logs DRG:** `logs/drg_guias.log`
- **Logs em tempo real:** `tail -f logs/drg_guias.log`

## 🔗 **API Endpoints**

**Base URL:** `http://localhost:8000/api/v1`

### **Principais Endpoints:**

- `GET /health` - Health check
- `GET /status` - Status do sistema
- `GET /guias` - Listar guias
- `GET /guias/{id}` - Consultar guia específica
- `POST /guias/{id}/processar` - Processar guia
- `GET /monitoramento` - Status do monitoramento
- `GET /monitoramento/status` - Status do monitoramento automático

**Documentação interativa:**

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🏗️ **Arquitetura**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Cliente       │───▶│  Tabela Guias    │───▶│  Monitor        │
│   (Insere dados)│    │  (inovemed_tbl_  │    │  Automático     │
│                 │    │   guias)         │    │  (Verifica)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Atualiza       │◀───│  API DRG        │
                       │  Status         │    │  (Processa)     │
                       └─────────────────┘    └─────────────────┘
```

## 🚀 **Deploy em Produção**

### **1. Servidor com Docker**

```bash
# Configurar .env para produção
DATABASE_TYPE=oracle
DEVELOPMENT=False
# ... outras configurações

# Deploy
docker-compose up -d --build
```

### **2. Servidor Tradicional**

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar .env
cp env.example .env
# Editar configurações

# Executar com Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📋 **Flags de Ambiente**

### **Desenvolvimento**

```env
DEVELOPMENT=True
TESTING=False
LOG_LEVEL=DEBUG
DATABASE_TYPE=sqlite
HOST=127.0.0.1
PORT=8000
```

### **Produção**

```env
DEVELOPMENT=False
TESTING=False
LOG_LEVEL=WARNING
DATABASE_TYPE=oracle
HOST=0.0.0.0
PORT=8000
```

### **Teste**

```env
DEVELOPMENT=False
TESTING=True
LOG_LEVEL=DEBUG
DATABASE_TYPE=sqlite
```

## 🆘 **Suporte**

- **Documentação completa:** [docs/README.md](./docs/README.md)
- **Logs detalhados:** `logs/drg_guias.log`
- **Testes automatizados:** `tests/` folder
- **API Documentation:** http://localhost:8000/docs

## 📝 **Changelog**

- ✅ **FastAPI** - Migração completa do Flask
- ✅ **Monitoramento Automático** - Processamento em lote (até 10 guias por vez)
- ✅ **Logs Detalhados** - Rastreamento completo
- ✅ **Docker** - Containerização completa
- ✅ **Multi-banco** - Oracle, PostgreSQL, SQLite
- ✅ **Documentação** - Organizada e completa
