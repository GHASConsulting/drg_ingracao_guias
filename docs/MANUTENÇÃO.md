# 🛠️ MANUTENÇÃO - Manual do Desenvolvedor

Este documento serve como **mapa de navegação** do código. Aqui você encontra onde está cada funcionalidade e como fazer alterações.

## 📁 **Estrutura do Projeto**

```
drg_guias/
├── README.md              # 📖 Documentação principal
├── main.py                # 🚀 Ponto de entrada da aplicação
├── requirements.txt       # 📦 Dependências Python
├── env.example           # ⚙️ Configurações exemplo
├── Dockerfile            # 🐳 Containerização
├── docker-compose.yml    # 🐳 Orquestração Docker
├── app/                  # 📂 Código principal da aplicação
│   ├── config/           # ⚙️ Configurações
│   ├── database/         # 🗄️ Banco de dados
│   ├── models/           # 📊 Modelos SQLAlchemy
│   ├── routes/           # 🛣️ Rotas da API
│   ├── schemas/          # 📋 Validação Pydantic
│   ├── services/         # 🔧 Lógica de negócio
│   └── utils/            # 🛠️ Utilitários
├── tests/                # 🧪 Scripts de teste
└── logs/                 # 📊 Logs do sistema
```

## 🗺️ **Mapa de Funcionalidades**

### **🚀 Aplicação Principal**

| Arquivo            | Função                   | O que alterar aqui                              |
| ------------------ | ------------------------ | ----------------------------------------------- |
| `main.py`          | Ponto de entrada FastAPI | Para alterar configuração geral, CORS, lifespan |
| `requirements.txt` | Dependências Python      | Para adicionar/remover bibliotecas              |

### **⚙️ Configurações**

| Arquivo                | Função                  | O que alterar aqui                    |
| ---------------------- | ----------------------- | ------------------------------------- |
| `app/config/config.py` | Todas as configurações  | Para alterar URLs, credenciais, flags |
| `env.example`          | Exemplo de configuração | Para documentar novas variáveis       |

**Principais configurações:**

- `DATABASE_TYPE` - Tipo de banco (sqlite, oracle, postgresql)
- `DRG_USERNAME/PASSWORD` - Credenciais DRG
- `AUTO_MONITOR_ENABLED` - Ativar/desativar monitoramento
- `MONITOR_INTERVAL_MINUTES` - Intervalo de monitoramento

### **🗄️ Banco de Dados**

| Arquivo                    | Função             | O que alterar aqui                 |
| -------------------------- | ------------------ | ---------------------------------- |
| `app/database/database.py` | Conexão e sessões  | Para alterar configuração de banco |
| `app/models/`              | Modelos SQLAlchemy | Para alterar estrutura das tabelas |

**Modelos principais:**

- `guias.py` - Tabela principal de guias
- `anexo.py` - Anexos das guias
- `procedimento.py` - Procedimentos
- `diagnostico.py` - Diagnósticos

### **🛣️ API e Rotas**

| Arquivo                        | Função             | O que alterar aqui                  |
| ------------------------------ | ------------------ | ----------------------------------- |
| `app/routes/fastapi_routes.py` | Todos os endpoints | Para adicionar/alterar rotas da API |

**Endpoints principais:**

- `/health` - Health check
- `/guias` - Listar/consultar guias
- `/guias/{id}/processar` - Processar guia
- `/monitoramento/*` - Controle do monitoramento

### **🔧 Lógica de Negócio**

| Arquivo                           | Função                   | O que alterar aqui                   |
| --------------------------------- | ------------------------ | ------------------------------------ |
| `app/services/drg_service.py`     | Integração DRG           | Para alterar comunicação com API DRG |
| `app/services/guia_service.py`    | Processamento de guias   | Para alterar lógica de processamento |
| `app/services/monitor_service.py` | Monitoramento automático | Para alterar lógica de monitoramento |
| `app/services/token_manager.py`   | Gerenciamento de tokens  | Para alterar autenticação DRG        |

### **📋 Validação de Dados**

| Arquivo                          | Função             | O que alterar aqui                 |
| -------------------------------- | ------------------ | ---------------------------------- |
| `app/schemas/guia_schema.py`     | Validação de guias | Para alterar regras de validação   |
| `app/schemas/response_schema.py` | Respostas da API   | Para alterar formato das respostas |

### **🛠️ Utilitários**

| Arquivo               | Função          | O que alterar aqui                      |
| --------------------- | --------------- | --------------------------------------- |
| `app/utils/logger.py` | Sistema de logs | Para alterar formato/estrutura dos logs |

### **🧪 Testes**

| Arquivo                         | Função                  | O que alterar aqui              |
| ------------------------------- | ----------------------- | ------------------------------- |
| `tests/testar_api.py`           | Testes da API           | Para adicionar novos testes     |
| `tests/testar_drg_com_logs.py`  | Testes DRG              | Para testar integração DRG      |
| `tests/testar_monitoramento.py` | Testes de monitoramento | Para testar monitoramento       |
| `tests/adicionar_guias.py`      | Dados de teste          | Para adicionar dados para teste |

## 🔧 **Como Fazer Alterações Comuns**

### **📝 Adicionar Nova Rota**

1. **Editar:** `app/routes/fastapi_routes.py`
2. **Adicionar:** Nova função com decorator `@router.get/post/put/delete`
3. **Testar:** `python tests/testar_api.py`

### **⚙️ Alterar Configurações**

1. **Editar:** `app/config/config.py`
2. **Adicionar:** Nova variável na classe `Settings`
3. **Documentar:** `env.example`
4. **Reiniciar:** Aplicação

### **🗄️ Alterar Banco de Dados**

1. **Modelos:** Editar `app/models/*.py`
2. **Conexão:** Verificar `app/database/database.py`
3. **Config:** Alterar `DATABASE_TYPE` no `.env`
4. **Testar:** Verificar conexão

### **🔗 Alterar Integração DRG**

1. **URLs:** Alterar em `app/config/config.py`
2. **Lógica:** Editar `app/services/drg_service.py`
3. **Tokens:** Verificar `app/services/token_manager.py`
4. **Testar:** `python tests/testar_drg_com_logs.py`

### **🤖 Alterar Monitoramento**

1. **Intervalo:** Alterar `MONITOR_INTERVAL_MINUTES` no `.env`
2. **Lógica:** Editar `app/services/monitor_service.py`
3. **Controle:** Verificar rotas em `app/routes/fastapi_routes.py`
4. **Testar:** `python tests/testar_monitoramento.py`

### **📊 Alterar Logs**

1. **Formato:** Editar `app/utils/logger.py`
2. **Nível:** Alterar `LOG_LEVEL` no `.env`
3. **Arquivo:** Verificar `LOG_FILE` no config

## 🐳 **Docker e Deploy**

### **🐳 Alterar Docker**

| Arquivo              | Função              | O que alterar aqui                      |
| -------------------- | ------------------- | --------------------------------------- |
| `Dockerfile`         | Imagem da aplicação | Para alterar dependências do sistema    |
| `docker-compose.yml` | Orquestração        | Para alterar portas, volumes, variáveis |

### **🚀 Deploy**

1. **Configurar:** `.env` com dados de produção
2. **Executar:** `docker-compose up --build -d`
3. **Verificar:** `docker-compose logs drg-api`

## 🔍 **Troubleshooting**

### **❌ Problemas Comuns**

| Problema                   | Onde verificar                    | Solução                 |
| -------------------------- | --------------------------------- | ----------------------- |
| API não inicia             | `main.py`                         | Verificar configurações |
| Erro de banco              | `app/database/database.py`        | Verificar conexão       |
| DRG não funciona           | `app/services/drg_service.py`     | Verificar credenciais   |
| Monitoramento não funciona | `app/services/monitor_service.py` | Verificar logs          |
| Logs não aparecem          | `app/utils/logger.py`             | Verificar configuração  |

### **📊 Logs para Debug**

```bash
# Logs da aplicação
tail -f logs/app.log

# Logs DRG
tail -f logs/drg_guias.log

# Logs Docker
docker-compose logs -f drg-api
```

## 📋 **Checklist de Manutenção**

### **✅ Antes de fazer alterações:**

- [ ] Fazer backup do código
- [ ] Testar em ambiente de desenvolvimento
- [ ] Verificar logs para erros
- [ ] Documentar mudanças

### **✅ Após alterações:**

- [ ] Testar funcionalidade alterada
- [ ] Verificar se outras funcionalidades não quebraram
- [ ] Atualizar documentação se necessário
- [ ] Fazer commit com mensagem clara

## 🎯 **Resumo Rápido**

**Para alterar:**

- **Configurações** → `app/config/config.py`
- **API/Rotas** → `app/routes/fastapi_routes.py`
- **Banco de dados** → `app/models/` e `app/database/database.py`
- **Integração DRG** → `app/services/drg_service.py`
- **Monitoramento** → `app/services/monitor_service.py`
- **Logs** → `app/utils/logger.py`
- **Testes** → `tests/`
- **Docker** → `Dockerfile` e `docker-compose.yml`

**Este documento é seu guia completo para navegar e manter o sistema!** 🗺️
