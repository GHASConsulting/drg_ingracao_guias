# 📊 Monitoramento da Integração DRG

Este documento explica como monitorar e visualizar a comunicação com a API DRG Brasil.

## 🔍 **O que é Monitorado**

### **1. 🔐 Autenticação**

- Requisição de login
- Headers enviados (com dados sensíveis mascarados)
- Resposta da API (token obtido)
- Erros de autenticação

### **2. 📋 Envio de Guias**

- JSON completo enviado para DRG
- Headers da requisição
- Resposta completa da API
- Status codes e mensagens de erro

### **3. ⚡ Processamento**

- ID e número da guia processada
- JSON montado antes do envio
- Resultado do processamento
- Mensagens de erro detalhadas

## 📁 **Localização dos Logs**

### **Arquivo de Log**

```
logs/drg_guias.log
```

### **Configuração no .env**

```env
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/drg_guias.log
```

## 🧪 **Como Testar e Monitorar**

### **1. Script de Teste Completo**

```bash
python testar_drg_com_logs.py
```

**Opções disponíveis:**

- Testar apenas autenticação
- Testar envio de guia completa
- Visualizar logs recentes
- Monitorar logs em tempo real
- Teste completo (autenticação + envio + logs)

### **2. Visualizar Logs Recentes**

```bash
# Windows
type logs\drg_guias.log

# Linux/Mac
tail -f logs/drg_guias.log
```

### **3. Monitorar em Tempo Real**

```bash
python testar_drg_com_logs.py
# Escolha opção 4
```

## 📋 **Exemplo de Log de Autenticação**

```
2025-01-27 10:30:15 - drg_integration - INFO - ================================================================================
2025-01-27 10:30:15 - drg_integration - INFO - 🚀 REQUISIÇÃO DRG - POST https://api-autenticacao.iagsaude.com/login
2025-01-27 10:30:15 - drg_integration - INFO - ================================================================================
2025-01-27 10:30:15 - drg_integration - INFO - 📋 Headers: {
  "Content-Type": "application/json",
  "Authorization": "***e57"
}
2025-01-27 10:30:15 - drg_integration - INFO - 📦 JSON: {
  "userName": "seu_usuario_drg",
  "password": "***123",
  "origin": "API_DRG"
}
2025-01-27 10:30:15 - drg_integration - INFO - --------------------------------------------------------------------------------
2025-01-27 10:30:15 - drg_integration - INFO - 📥 RESPOSTA DRG - Status: 200
2025-01-27 10:30:15 - drg_integration - INFO - --------------------------------------------------------------------------------
2025-01-27 10:30:15 - drg_integration - INFO - 📋 Response Headers: {
  "content-type": "application/json",
  "content-length": "150"
}
2025-01-27 10:30:15 - drg_integration - INFO - 📦 Response Text: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
2025-01-27 10:30:15 - drg_integration - INFO - 🔐================================================================================
2025-01-27 10:30:15 - drg_integration - INFO - 🔐 AUTENTICAÇÃO DRG - SUCESSO
2025-01-27 10:30:15 - drg_integration - INFO - 🔐 Token: eyJh...J9
2025-01-27 10:30:15 - drg_integration - INFO - 🔐================================================================================
```

## 📋 **Exemplo de Log de Envio de Guia**

```
2025-01-27 10:31:00 - drg_integration - INFO - ================================================================================
2025-01-27 10:31:00 - drg_integration - INFO - 🚀 REQUISIÇÃO DRG - POST https://api-hospitalar.iagsaude.com/integracao/guias/save
2025-01-27 10:31:00 - drg_integration - INFO - ================================================================================
2025-01-27 10:31:00 - drg_integration - INFO - 📋 Headers: {
  "Content-Type": "application/json",
  "Authorization": "eyJh...J9"
}
2025-01-27 10:31:00 - drg_integration - INFO - 📦 JSON: {
  "loteGuias": {
    "guia": [
      {
        "codigoOperadora": "4764",
        "numeroGuia": "R123456",
        "numeroGuiaOperadora": "UI123456",
        "dataAutorizacao": "2025-01-27",
        "senha": "123456789",
        "numeroCarteira": "123456",
        "nomePrestador": "HOSPITAL TESTE",
        "nomeProfissional": "DR. TESTE",
        "nomeHospital": "HOSPITAL TESTE",
        "indicacaoClinica": "Internação para tratamento",
        "diariasSolicitadas": "3",
        "qtdeDiariasAutorizadas": "3",
        "procedimentos": [
          {
            "tabela": "98",
            "codigo": "9654001",
            "descricao": "PROCEDIMENTO TESTE",
            "qtdeSolicitada": "1",
            "valorUnitario": 100.00
          }
        ],
        "diagnosticos": [
          {
            "codigo": "A123",
            "tipo": "P"
          }
        ]
      }
    ]
  }
}
2025-01-27 10:31:00 - drg_integration - INFO - --------------------------------------------------------------------------------
2025-01-27 10:31:00 - drg_integration - INFO - 📥 RESPOSTA DRG - Status: 200
2025-01-27 10:31:00 - drg_integration - INFO - --------------------------------------------------------------------------------
2025-01-27 10:31:00 - drg_integration - INFO - 📋 Response Headers: {
  "content-type": "application/json",
  "content-length": "200"
}
2025-01-27 10:31:00 - drg_integration - INFO - 📦 Response JSON: {
  "sucesso": true,
  "mensagem": "Guia processada com sucesso",
  "protocolo": "PROT123456",
  "dataProcessamento": "2025-01-27T10:31:00Z"
}
2025-01-27 10:31:00 - drg_integration - INFO - 📋================================================================================
2025-01-27 10:31:00 - drg_integration - INFO - 📋 PROCESSAMENTO GUIA - ID: 1 | Número: R123456
2025-01-27 10:31:00 - drg_integration - INFO - 📋================================================================================
2025-01-27 10:31:00 - drg_integration - INFO - 📤 JSON Enviado: {
  "loteGuias": {
    "guia": [
      {
        "codigoOperadora": "4764",
        "numeroGuia": "R123456",
        ...
      }
    ]
  }
}
2025-01-27 10:31:00 - drg_integration - INFO - ✅ PROCESSAMENTO SUCESSO
2025-01-27 10:31:00 - drg_integration - INFO - 📥 Resposta: {
  "sucesso": true,
  "mensagem": "Guia processada com sucesso",
  "protocolo": "PROT123456"
}
2025-01-27 10:31:00 - drg_integration - INFO - 📋================================================================================
```

## 🚨 **Logs de Erro**

```
2025-01-27 10:32:00 - drg_integration - ERROR - ❌================================================================================
2025-01-27 10:32:00 - drg_integration - ERROR - ❌ ERRO DRG - Envio de guia DRG
2025-01-27 10:32:00 - drg_integration - ERROR - ❌================================================================================
2025-01-27 10:32:00 - drg_integration - ERROR - ❌ Tipo: ConnectionError
2025-01-27 10:32:00 - drg_integration - ERROR - ❌ Mensagem: Connection timeout
2025-01-27 10:32:00 - drg_integration - ERROR - ❌--------------------------------------------------------------------------------
```

## 🔧 **Configurações de Log**

### **Níveis de Log**

- **DEBUG**: Todos os detalhes (desenvolvimento)
- **INFO**: Informações importantes (padrão)
- **WARNING**: Apenas avisos e erros
- **ERROR**: Apenas erros críticos

### **Mascaramento de Dados Sensíveis**

- Senhas: `***123`
- Tokens: `eyJh...J9`
- API Keys: `***e57`

## 📊 **Interpretando os Logs**

### **✅ Sucesso**

- Status 200 na resposta
- Token válido obtido
- JSON enviado corretamente
- Resposta positiva da DRG

### **❌ Erros Comuns**

- **401**: Token expirado ou inválido
- **400**: JSON malformado ou dados inválidos
- **500**: Erro interno do servidor DRG
- **Timeout**: Problemas de conectividade

### **🔍 Debugging**

1. Verificar se o JSON está correto
2. Confirmar se o token é válido
3. Verificar conectividade com DRG
4. Analisar mensagens de erro específicas

## 🔄 **4. Monitoramento PULL da DRG**

O sistema agora suporta monitoramento PULL, buscando periodicamente atualizações da DRG sobre as guias já enviadas.

### **Configuração no .env**

```env
# Habilitar/desabilitar monitoramento PULL
MONITOR_PULL_ENABLED=True

# Intervalo entre consultas (minutos)
MONITOR_PULL_INTERVAL_MINUTES=5

# Tamanho máximo de lote por página
MONITOR_PULL_MAX_PAGE_SIZE=100
```

### **Como Funciona**

1. A cada X minutos (configurável), o sistema busca atualizações das guias enviadas nas últimas 24h
2. Implementa regra de **conflito simultâneo**: se já houver uma execução há menos de 1 minuto, aguarda
3. Processa as atualizações e atualiza campos da guia (situação, senha, autorização, etc.)
4. Registra logs detalhados de cada consulta

### **Rotas da API**

#### **Obter Status**
```bash
GET /api/v1/monitor-pull/status
```

#### **Iniciar Monitoramento Manualmente**
```bash
POST /api/v1/monitor-pull/start
```

#### **Parar Monitoramento Manualmente**
```bash
POST /api/v1/monitor-pull/stop
```

### **Exemplo de Log PULL**

```
2025-01-27 10:35:00 - monitor_pull - INFO - 🔍 Buscando atualizações da DRG via PULL...
2025-01-27 10:35:00 - monitor_pull - INFO - 📋 Processando 15 guias enviadas...
2025-01-27 10:35:00 - monitor_pull - INFO - 📦 Processando lote 1/1 (15 guias)...
2025-01-27 10:35:01 - drg_integration - INFO - 🚀 REQUISIÇÃO DRG - POST https://api-exportacaoassistencial.iagsaude.com/guiainternacao/search
2025-01-27 10:35:01 - drg_integration - INFO - 📋 Headers: {
  "Content-Type": "application/json",
  "Authorization": "eyJh...J9",
  "x-api-key": "298d9c85-65af-44f9-b684-0dd92dcb3e57"
}
2025-01-27 10:35:01 - drg_integration - INFO - 📦 JSON: {
  "numeroGuia": ["R123456", "R123457", ...],
  "page": 1
}
2025-01-27 10:35:02 - drg_integration - INFO - 📥 RESPOSTA DRG - Status: 200
2025-01-27 10:35:02 - monitor_pull - INFO - 📝 Processando 15 guias da resposta...
2025-01-27 10:35:02 - monitor_pull - INFO - 📝 Guia R123456 atualizada: situacao_guia, senha_autorizacao
2025-01-27 10:35:02 - monitor_pull - INFO - ✅ Atualizações salvas com sucesso
2025-01-27 10:35:02 - monitor_pull - INFO - ✅ Processamento PULL concluído
```

### **Prevenção de Conflito Simultâneo**

O sistema implementa a regra de conflito simultâneo conforme documento 22391:

- Se houver uma execução há menos de 1 minuto, a nova execução aguarda
- Logs mostram avisos quando conflito é detectado
- Evita múltiplas requisições simultâneas à API DRG

```
2025-01-27 10:35:05 - monitor_pull - WARNING - ⚠️ Conflito simultâneo: última execução há 5s
2025-01-27 10:35:05 - monitor_pull - WARNING - ⏸️ Conflito simultâneo detectado, aguardando...
```

## 🚀 **Próximos Passos**

1. **Execute o teste**: `python testar_drg_com_logs.py`
2. **Monitore os logs**: Observe as requisições e respostas
3. **Verifique o JSON**: Confirme se está no formato correto
4. **Analise erros**: Use as mensagens para debug
5. **Ajuste configurações**: Baseado nos resultados
6. **Configure PULL**: Ajuste intervalo e tamanho de lote conforme necessidade

---

**📊 Com este sistema de monitoramento, você pode ver exatamente o que está sendo enviado para o DRG e o que está retornando!**


