# Testes do Sistema DRG (FastAPI)

Esta pasta contém todos os arquivos de teste do sistema.

## Arquivos de Teste

### 🧪 **Scripts de Teste da API**

- `testar_api.py` - Teste completo da API FastAPI
- `testar_drg_com_logs.py` - Teste DRG com logs detalhados
- `testar_monitoramento.py` - Teste do sistema de monitoramento automático

### 📊 **Utilitários de Dados**

- `adicionar_guias.py` - Script para adicionar dados de teste ao banco
- `criar_banco_teste.py` - Script para criar banco SQLite com dados fictícios

### 🔧 **Testes de Integração (Legados)**

- `test_integracao_completa.py` - Teste completo de integração SQLite → GuiaService → DRGService
- `test_drg_debug.py` - Teste detalhado do DRGService para debug
- `test_services_simple.py` - Teste simplificado dos serviços (sem FastAPI)
- `test_token_manager.py` - Teste do gerenciador de tokens
- `test_schemas.py` - Teste de validação dos schemas Pydantic

## Como Executar

### 🚀 **Scripts Principais**

```bash
# Teste completo da API FastAPI
python tests/testar_api.py

# Teste DRG com logs detalhados
python tests/testar_drg_com_logs.py

# Teste do monitoramento automático
python tests/testar_monitoramento.py

# Adicionar dados de teste
python tests/adicionar_guias.py
```

### 🔧 **Testes Legados**

```bash
# Teste de integração completo
python tests/test_integracao_completa.py

# Teste de debug do DRG
python tests/test_drg_debug.py

# Criar banco de teste
python tests/criar_banco_teste.py

# Teste de schemas
python tests/test_schemas.py

# Teste do token manager
python tests/test_token_manager.py
```

## Banco de Teste

O banco SQLite de teste é criado em `../database/teste_drg.db` e contém:

- 4 guias com diferentes status (A, T, E)
- 1 anexo completo
- 1 procedimento completo
- 3 diagnósticos

## Dados Fictícios

Os dados de teste são baseados nos exemplos da documentação da API DRG e incluem:

- Guias com todos os campos obrigatórios
- Relacionamentos completos (anexos, procedimentos, diagnósticos)
- Diferentes status de processamento para teste

## Status dos Testes

### ✅ **Testes da API FastAPI**

```
🎯 Resultado: 8/8 testes passaram
🎉 TODOS OS TESTES PASSARAM!
```

**Rotas testadas:**

- ✅ `/health` - Health check
- ✅ `/status` - Status do sistema
- ✅ `/guias` - Listar guias
- ✅ `/guias?status=A` - Filtrar por status
- ✅ `/guias?limit=2` - Paginação
- ✅ `/guias/1` - Consultar guia específica
- ✅ `/drg/token` - Status do token DRG
- ✅ `/monitoramento` - Monitoramento do sistema

### **Documentação Automática**

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Estrutura de Testes

```
tests/
├── README.md                    # Este arquivo
├── test_integracao_completa.py  # Teste completo
├── test_drg_debug.py           # Debug DRG
├── test_services_simple.py     # Teste serviços
├── test_token_manager.py       # Teste tokens
├── test_schemas.py             # Teste schemas
└── criar_banco_teste.py        # Criar banco teste
```

## Comandos Úteis

```bash
# Executar todos os testes
python tests/testar_api.py

# Adicionar mais dados de teste
python tests/adicionar_guias.py

# Verificar status da API
curl http://localhost:8000/api/v1/health

# Listar guias
curl http://localhost:8000/api/v1/guias
```
