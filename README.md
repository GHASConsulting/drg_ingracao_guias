# 📚 Documentação do Sistema DRG - FastAPI

## 📖 Índice da Documentação

### **📋 Documentação Principal**

- **[README.md](../README.md)** - Documentação principal do projeto (na raiz)

### **📄 Documentação Técnica**

- **[API_ROUTES.md](./API_ROUTES.md)** - Documentação completa das rotas da API
- **[INSOMNIA_TESTS.md](./INSOMNIA_TESTS.md)** - Testes da API com Insomnia
- **[MONITORAMENTO_AUTOMATICO.md](./MONITORAMENTO_AUTOMATICO.md)** - Sistema de monitoramento automático
- **[MONITORAMENTO_DRG.md](./MONITORAMENTO_DRG.md)** - Logs e monitoramento DRG

### **🗺️ Documentação de Desenvolvimento**

- **[MAPA_DESENVOLVIMENTO.md](./MAPA_DESENVOLVIMENTO.md)** - Mapa completo do desenvolvimento
- **[REGRAS_DESENVOLVIMENTO.md](./REGRAS_DESENVOLVIMENTO.md)** - Regras e decisões do projeto

### **📊 Especificações e Dados**

- **Componente de Comunicação.pdf** - Especificação oficial DRG
- **Componente Conteudo Estrutura.xlsx** - Estrutura dos dados
- **Entrada.json** - Exemplo de entrada
- **Saida.json** - Exemplo de saída

---

## 📋 Visão Geral do Sistema

Sistema desenvolvido em Python com FastAPI para processamento, validação e gerenciamento de guias de internação hospitalar. O sistema recebe lotes de guias em formato JSON, processa as informações, valida os dados e retorna o status de processamento para cada guia.

## 🎯 Objetivo

Criar uma API REST robusta que:

- Receba lotes de guias de internação em formato JSON
- Valide os dados conforme especificações técnicas
- Processe e armazene as informações automaticamente
- Monitore a tabela de guias e processe em lote (até 10 por vez)
- Integre com a API do DRG Brasil para envio de guias
- Forneça logs detalhados de todo o processo

## 🏗️ Arquitetura do Sistema

### **Padrão Arquitetural**

- **FastAPI**: Framework moderno e rápido
- **MVC (Model-View-Controller)**: Separação de responsabilidades
- **Repository Pattern**: Camada de acesso a dados
- **Service Layer**: Lógica de negócio isolada
- **API Gateway**: Interface única para comunicação externa

### **Camadas da Aplicação**

```
┌─────────────────────────────────────┐
│      Monitor Service Layer          │ ← Monitoramento Automático
├─────────────────────────────────────┤
│         FastAPI Routes              │ ← API Endpoints + Dependency Injection
├─────────────────────────────────────┤
│         Service Layer               │ ← Business Logic + DRG Integration
├─────────────────────────────────────┤
│        Repository Layer             │ ← Data Access + Queue Management
├─────────────────────────────────────┤
│         Model Layer                 │ ← SQLAlchemy Models + Queue Table
├─────────────────────────────────────┤
│        Database Layer               │ ← Oracle/PostgreSQL/Firebird/SQLite
└─────────────────────────────────────┘
```

### **Fluxo Arquitetural**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Cliente       │───▶│  Tabela Guias    │───▶│  Monitor        │
│   (Insere dados)│    │  (inovemed_tbl_  │    │  Automático     │
│                 │    │   guias)         │    │  (Lote até 10)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Atualiza       │◀───│  API DRG        │
                       │  Status         │    │  (Lote)         │
                       └─────────────────┘    └─────────────────┘
```

## 🚀 Tecnologias Utilizadas

### **Backend**

- **FastAPI 0.104.1**: Framework web moderno e rápido
- **Uvicorn**: Servidor ASGI para FastAPI
- **Pydantic v2**: Validação e serialização de dados
- **SQLAlchemy 2.0**: ORM para acesso ao banco de dados
- **Background Tasks**: Monitoramento automático da tabela
- **AsyncIO**: Processamento assíncrono integrado

### **Banco de Dados**

- **Oracle**: Banco principal (produção)
- **PostgreSQL**: Alternativa
- **Firebird**: Alternativa
- **SQLite**: Desenvolvimento e testes

### **Integração Externa**

- **DRG Brasil API**: Integração com sistema externo
- **JWT Authentication**: Autenticação segura
- **HTTP/HTTPS**: Comunicação REST

## 📊 Estrutura de Dados

### **Tabela Principal: inovemed_tbl_guias**

```sql
CREATE TABLE inovemed_tbl_guias (
    id INTEGER PRIMARY KEY,
    numero_guia VARCHAR(50) NOT NULL,
    codigo_operadora VARCHAR(20) NOT NULL,
    data_autorizacao DATE,
    situacao_guia VARCHAR(1),
    tp_status VARCHAR(1) DEFAULT 'A', -- A=Aguardando, T=Transmitida, E=Erro
    data_processamento DATETIME,
    mensagem_erro TEXT,
    tentativas INTEGER DEFAULT 0,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### **Tabelas Relacionadas**

- **inovemed_tbl_anexos**: Anexos das guias
- **inovemed_tbl_procedimentos**: Procedimentos das guias
- **inovemed_tbl_diagnosticos**: Diagnósticos das guias

## 🔧 Configuração e Instalação

### **1. Pré-requisitos**

- Python 3.11+
- Virtual Environment
- Redis (para Celery)

### **2. Instalação**

```bash
# Clone o repositório
git clone <repository-url>
cd drg_guias

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instale dependências
pip install -r requirements.txt
```

### **3. Configuração**

```bash
# Copie o arquivo de exemplo
cp env.example .env

# Configure as variáveis necessárias
nano .env
```

### **4. Execução**

```bash
# Iniciar a API FastAPI
python main.py

# A API estará disponível em:
# http://localhost:8000
# Documentação: http://localhost:8000/docs
```

## 📚 Documentação da API

### **Documentação Automática**

A FastAPI gera automaticamente:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### **Endpoints Principais**

- `GET /api/v1/health` - Health check
- `GET /api/v1/status` - Status do sistema
- `GET /api/v1/guias` - Listar guias
- `GET /api/v1/guias/{id}` - Consultar guia específica
- `POST /api/v1/guias/{id}/processar` - Processar guia
- `GET /api/v1/monitoramento` - Monitoramento do sistema

## 🧪 Testes

### **Executar Testes**

```bash
# Testar todas as rotas
python testar_api.py

# Adicionar dados de teste
python adicionar_guias.py
```

### **Resultado dos Testes**

```
🎯 Resultado: 8/8 testes passaram
🎉 TODOS OS TESTES PASSARAM!
```

## 🔗 Integração com DRG Brasil

### **Configuração**

```bash
# URLs de teste
AUTH_API_URL=https://api-autenticacao.iagsaude.com/login
DRG_API_URL=https://api-hospitalar.iagsaude.com/integracao/guias/save

# Credenciais
DRG_USERNAME=seu_usuario
DRG_PASSWORD=sua_senha
DRG_API_KEY=seu_codigo_unico
```

### **Fluxo de Autenticação**

1. **Login**: POST para `/login` com credenciais
2. **Token JWT**: Recebido com expiração de 4 horas
3. **Envio**: POST para `/integracao/guias/save` com JWT

### **Formato de Envio**

```json
{
  "loteGuias": {
    "guia": [
      {
        "codigoOperadora": "4764",
        "numeroGuia": "R679541",
        "dataAutorizacao": "2025-08-02"
        // ... outros campos
      }
    ]
  }
}
```

## 📈 Status do Projeto

### **✅ Concluído**

- [x] Migração Flask → FastAPI
- [x] Modelos SQLAlchemy
- [x] Schemas Pydantic v2
- [x] Rotas da API
- [x] Serviços de negócio
- [x] Integração DRG
- [x] Testes completos
- [x] Documentação automática

### **🔄 Em Desenvolvimento**

- [ ] Processamento Celery
- [ ] Retry automático
- [ ] Monitoramento avançado

### **📊 Métricas**

- **8/8 testes** passando (100% sucesso)
- **Todas as rotas** funcionando
- **Banco de dados** operacional
- **Documentação** automática disponível

## 🎯 Próximos Passos

1. **Implementar processamento Celery** para fila
2. **Configurar retry automático** para falhas
3. **Adicionar mais dados de teste**
4. **Implementar monitoramento** avançado

## 📞 Suporte

Para dúvidas ou suporte, consulte:

- **Documentação**: `http://localhost:8000/docs`
- **Logs**: `logs/app.log`
- **Testes**: Execute `python testar_api.py`

---

_Última atualização: 2025-09-23 - Migração FastAPI Concluída_
