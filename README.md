# 🏥 Sistema DRG - Guias de Internação

Sistema para processamento automático e envio de guias de internação para a API DRG Brasil usando FastAPI.

## ✨ Características

- 🚀 **FastAPI** - Framework moderno e rápido
- 🗄️ **Multi-banco** - Oracle, PostgreSQL, SQLite
- 🤖 **Monitoramento Automático** - Processa guias em lote
- 📊 **Logs Detalhados** - Rastreamento completo
- 🐳 **Docker Ready** - Deploy simplificado

## 🎯 Início Rápido

**Método Principal:** Use os scripts `.bat` (Windows) ou `.sh` (Linux/Mac) para iniciar a aplicação rapidamente:

```bash
# Windows - Desenvolvimento
start_drg_api_dev.bat

# Windows - Produção
start_drg_api_prod.bat

# Linux/Mac - Produção
./start_drg_api_prod.sh
```

Estes scripts fazem tudo automaticamente: ativam ambiente virtual, configuram Oracle, testam banco e iniciam a API.

**Acesse:** http://localhost:8000/docs

## 🚀 Instalação Rápida

### Pré-requisitos

- Python 3.11+ ou Docker
- Oracle Instant Client (se usar Oracle)
- Credenciais da API DRG

### 1. Clone e Configure

```bash
# Clone o repositório
git clone https://github.com/GHASConsulting/drg_ingracao_guias.git
cd drg_guias

# Configure o ambiente
cp env.example .env
```

### 2. Edite o arquivo `.env`

```env
# AMBIENTE
DEVELOPMENT=True          # True=dev, False=produção

# DATABASE (Escolha um)
DATABASE_TYPE=sqlite      # sqlite, oracle, postgresql
DATABASE_URL=sqlite:///database/teste_drg.db

# ORACLE (Produção)
# DATABASE_TYPE=oracle
# ORACLE_HOST=servidor
# ORACLE_PORT=1521
# ORACLE_SID=XE
# ORACLE_USERNAME=usuario
# ORACLE_PASSWORD=senha
# ORACLE_DIR=C:\instantclient_21_13  # Windows
# ORACLE_DIR=/opt/oracle/instantclient_21_17  # Linux

# DRG API
DRG_USERNAME=seu_usuario
DRG_PASSWORD=sua_senha
DRG_API_KEY=sua_chave
AUTH_API_URL=https://api-autenticacao.iagsaude.com/login
DRG_API_URL=https://api-hospitalar.iagsaude.com/integracao/guias/save

# MONITORAMENTO
AUTO_MONITOR_ENABLED=True
MONITOR_INTERVAL_MINUTES=5
```

## ⚡ Executar a Aplicação (Método Principal)

### 🪟 Windows - Desenvolvimento

```bash
# Duplo clique ou execute no terminal
start_drg_api_dev.bat
```

Este script:

- ✅ Ativa o ambiente virtual automaticamente
- ✅ Configura variáveis Oracle
- ✅ Testa conexão com banco
- ✅ Inicia a aplicação FastAPI

**Acesse:** http://localhost:8000/docs

### 🐧 Linux/Mac - Produção

```bash
# Dar permissão de execução
chmod +x start_drg_api_prod.sh

# Executar
./start_drg_api_prod.sh
```

### 🪟 Windows - Produção

```bash
# Executar no terminal
start_drg_api_prod.bat
```

---

## 🔄 Métodos Alternativos (Secundários)

### 🐍 Executar com Python Direto

```bash
# Windows
venv\Scripts\activate
python main.py

# Linux/Mac
source venv/bin/activate
python main.py
```

### 🐳 Executar com Docker

```bash
# Construir e iniciar
docker-compose --profile production up --build -d

# Ver logs
docker-compose logs -f drg-api

# Parar
docker-compose down

# Acesse: http://localhost:8000/docs
```

## ✅ Testar Conexão com Banco

### SQLite

```bash
# O banco será criado automaticamente em database/teste_drg.db
```

### Oracle

```bash
# 1. Instale o Oracle Instant Client
# Windows: C:\instantclient_21_13
# Linux: /opt/oracle/instantclient_21_17

# 2. Configure no .env
DATABASE_TYPE=oracle
ORACLE_HOST=servidor
ORACLE_PORT=1521
ORACLE_SID=XE
ORACLE_USERNAME=usuario
ORACLE_PASSWORD=senha

# 3. Teste a conexão
python -c "import cx_Oracle; print('✅ Oracle OK')"
```

### PostgreSQL

```bash
# Configure no .env
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://usuario:senha@servidor:5432/database

# Teste a conexão
python -c "import psycopg2; print('✅ PostgreSQL OK')"
```

## 📊 Verificar se Está Funcionando

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Status do sistema
curl http://localhost:8000/api/v1/status

# Monitoramento
curl http://localhost:8000/api/v1/monitoramento/status

# Ver logs
tail -f logs/drg_guias.log
```

## 🧪 Testes

```bash
# Teste completo da API
python tests/testar_api.py

# Teste DRG com logs
python tests/testar_drg_com_logs.py

# Teste de monitoramento
python tests/testar_monitoramento.py
```

## 📚 API Endpoints

**Base URL:** `http://localhost:8000/api/v1`

**Principais:**

- `GET /health` - Health check
- `GET /status` - Status do sistema
- `GET /guias` - Listar guias
- `GET /guias/{id}` - Consultar guia
- `POST /guias/{id}/processar` - Processar guia
- `GET /monitoramento` - Status do monitoramento

**Documentação interativa:**

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🔄 Como Funciona

```
1. Cliente insere guia na tabela (inovemed_tbl_guias)
   ↓
2. Sistema monitora automaticamente (a cada X minutos)
   ↓
3. Detecta guias com status 'A' (Aguardando)
   ↓
4. Processa em lote (até 10 guias por vez)
   ↓
5. Monta JSON completo
   ↓
6. Envia para API DRG
   ↓
7. Atualiza status (T=Transmitida, E=Erro)
```

## 📁 Estrutura de Diretórios

```
drg_guias/
├── app/
│   ├── config/          # Configurações
│   ├── database/        # Conexão com banco
│   ├── models/          # Models SQLAlchemy
│   ├── routes/          # Rotas FastAPI
│   ├── services/        # Serviços (DRG, Monitor)
│   └── utils/           # Utilitários
├── database/            # Banco SQLite
├── docs/                # Documentação
├── logs/                # Logs da aplicação
├── tests/               # Scripts de teste
├── .env                 # Configurações (criar a partir de env.example)
├── docker-compose.yml   # Docker Compose
├── main.py              # Aplicação principal
└── requirements.txt     # Dependências Python
```

## 🏗️ Tabelas do Banco

### inovemed_tbl_guias (Principal)

```sql
INSERT INTO inovemed_tbl_guias (
    numero_guia, codigo_operadora, tp_status, ...
) VALUES (
    'R123456', '3945', 'A', ...  -- tp_status='A' (Aguardando)
);
```

**Status da Guia:**

- `'A'` - Aguardando processamento
- `'P'` - Processando
- `'T'` - Transmitida com sucesso
- `'E'` - Erro no processamento

### Tabelas Relacionadas

- `inovemed_tbl_anexos` - Documentos anexos
- `inovemed_tbl_procedimentos` - Procedimentos da guia
- `inovemed_tbl_diagnosticos` - Diagnósticos (CID-10)

## 🔧 Troubleshooting

### Aplicação não inicia

```bash
# Verificar se .env existe
ls -la .env

# Ver logs
tail -f logs/drg_guias.log

# Verificar dependências
pip install -r requirements.txt
```

### Erro de conexão Oracle

```bash
# Verificar se Instant Client está instalado
# Windows: C:\instantclient_21_13
# Linux: /opt/oracle/instantclient_21_17

# Verificar variáveis de ambiente
echo $ORACLE_DIR
echo $LD_LIBRARY_PATH
```

### Guias não são processadas

```bash
# Verificar se monitoramento está ativo
curl http://localhost:8000/api/v1/monitoramento/status

# Verificar logs
tail -f logs/drg_guias.log | grep -i "monitoramento"

# Verificar guias no banco
# Guias devem ter tp_status='A'
```

### Docker não inicia

```bash
# Verificar se Docker está rodando
docker ps

# Ver logs
docker-compose logs

# Reconstruir
docker-compose down
docker-compose up --build
```

## 📖 Documentação Completa

- [API Routes](docs/API_ROUTES.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)
- [Monitoramento Automático](docs/MONITORAMENTO_AUTOMATICO.md)
- [Authentication Guide](docs/AUTHENTICATION_GUIDE.md)

## 🆘 Suporte

- **Documentação:** [docs/README.md](docs/README.md)
- **Logs:** `logs/drg_guias.log`
- **Testes:** `tests/` folder
- **API Docs:** http://localhost:8000/docs

## 📝 Changelog

- ✅ FastAPI migration
- ✅ Monitoramento automático (lote de 10 guias)
- ✅ Logs detalhados
- ✅ Docker completa
- ✅ Multi-banco (Oracle, PostgreSQL, SQLite)
- ✅ Segurança (rate limiting)
- ✅ Processamento em tempo real
