# API Routes - Sistema DRG

Documentação das rotas da API para o sistema de processamento de guias DRG.

## Base URL

```
http://localhost:8000/api/v1
```

## Endpoints

### 🏥 Health Check

```http
GET /health
```

Verifica se a API está funcionando.

**Resposta:**

```json
{
  "status": "healthy",
  "timestamp": "2025-09-23T19:30:00.000Z",
  "version": "1.0.0",
  "service": "DRG API"
}
```

### 📊 Status do Sistema

```http
GET /status
```

Retorna status geral do sistema, contadores de guias e status da API DRG.

**Resposta:**

```json
{
  "sistema": {
    "status": "operacional",
    "timestamp": "2025-09-23T19:30:00.000Z"
  },
  "guias": {
    "total": 4,
    "aguardando": 2,
    "transmitidas": 1,
    "com_erro": 1
  },
  "drg_api": {
    "status": "conectado",
    "token_valido": true
  }
}
```

### 📋 Listar Guias

```http
GET /guias
```

**Parâmetros:**

- `status` (opcional): Filtro por status (A, T, E)
- `limit` (opcional): Limite de resultados (padrão: 50)
- `offset` (opcional): Offset para paginação (padrão: 0)

**Exemplos:**

```http
GET /guias
GET /guias?status=A
GET /guias?limit=10&offset=0
```

**Resposta:**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "numero_guia": "R679541",
      "nome_hospital": "HOSPITAL CINCO",
      "tp_status": "A",
      "data_criacao": "2025-09-23T19:30:00.000Z"
    }
  ],
  "pagination": {
    "limit": 50,
    "offset": 0,
    "total": 1
  }
}
```

### 🔍 Consultar Guia

```http
GET /guias/{id}
```

Retorna uma guia específica com todos os dados relacionados.

**Resposta:**

```json
{
  "success": true,
  "data": {
    "guia": {
      "id": 1,
      "numero_guia": "R679541",
      "nome_hospital": "HOSPITAL CINCO",
      "tp_status": "A"
    },
    "anexos": [
      {
        "id": 1,
        "nome": "DOC TESTE 02",
        "tipo_documento": "03"
      }
    ],
    "procedimentos": [
      {
        "id": 1,
        "codigo": "96547854",
        "descricao": "TESTE DAY",
        "valor_unitario": 119.25
      }
    ],
    "diagnosticos": [
      {
        "id": 1,
        "codigo": "A021",
        "tipo": "P"
      }
    ]
  }
}
```

### ⚡ Processar Guia

```http
POST /guias/{id}/processar
```

Processa uma guia específica enviando para a API DRG.

**Resposta de Sucesso:**

```json
{
  "success": true,
  "data": {
    "guia_id": 1,
    "status": "T",
    "tentativas": 1,
    "mensagem": "Guia transmitida com sucesso"
  }
}
```

**Resposta de Erro:**

```json
{
  "success": false,
  "data": {
    "guia_id": 1,
    "status": "E",
    "tentativas": 1,
    "mensagem": "Erro na API DRG"
  }
}
```

### 🔄 Reprocessar Guia

```http
POST /guias/{id}/reprocessar
```

Resetar uma guia com erro para reprocessamento.

**Resposta:**

```json
{
  "success": true,
  "data": {
    "guia_id": 1,
    "status": "A",
    "mensagem": "Guia resetada para reprocessamento"
  }
}
```

### 🔑 Status do Token DRG

```http
GET /drg/token
```

Retorna informações sobre o token JWT da API DRG.

**Resposta:**

```json
{
  "success": true,
  "data": {
    "has_token": true,
    "should_refresh": false,
    "time_since_auth": 3600
  }
}
```

### 🔄 Renovar Token DRG

```http
POST /drg/token/renovar
```

Força a renovação do token JWT.

**Resposta:**

```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "renovado_em": "2025-09-23T19:30:00.000Z"
  }
}
```

### 📈 Monitoramento

```http
GET /monitoramento
```

Retorna informações detalhadas de monitoramento do sistema.

### 🤖 Monitoramento Automático

```http
GET /monitoramento/status
POST /monitoramento/start
POST /monitoramento/stop
```

Controla o sistema de monitoramento automático da tabela de guias.

#### GET /monitoramento/status

**Resposta:**

```json
{
  "success": true,
  "data": {
    "monitoramento_ativo": true,
    "intervalo_minutos": 5,
    "auto_monitor_enabled": true,
    "total_guias": 25,
    "aguardando": 3,
    "processando": 1,
    "transmitidas": 20,
    "com_erro": 1,
    "ultima_verificacao": "2024-01-15T10:30:00"
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

#### POST /monitoramento/start

**Resposta:**

```json
{
  "success": true,
  "message": "Monitoramento iniciado com sucesso",
  "timestamp": "2024-01-15T10:30:00"
}
```

#### POST /monitoramento/stop

**Resposta:**

```json
{
  "success": true,
  "message": "Monitoramento parado com sucesso",
  "timestamp": "2024-01-15T10:30:00"
}
```

### 📊 Monitoramento Geral

```http
GET /monitoramento
```

**Resposta:**

```json
{
  "timestamp": "2025-09-23T19:30:00.000Z",
  "estatisticas": {
    "total_guias": 4,
    "aguardando": 2,
    "processando": 0,
    "transmitidas": 1,
    "com_erro": 1,
    "taxa_sucesso": 25.0
  },
  "guias_com_erro": [
    {
      "id": 3,
      "numero_guia": "R679543",
      "tentativas": 2,
      "mensagem_erro": "Erro na API DRG"
    }
  ],
  "drg_api": {
    "status": "conectado",
    "token_valido": true
  }
}
```

## Códigos de Status

- `200` - Sucesso
- `400` - Erro de validação/requisição
- `404` - Recurso não encontrado
- `500` - Erro interno do servidor

## Como Testar

### 1. Iniciar o Flask

```bash
python run.py
```

### 2. Testar com script

```bash
python testar_api.py
```

### 3. Testar com Insomnia/Postman

- Importe as rotas acima
- Configure base URL: `http://localhost:5000/api/v1`
- Teste os endpoints

## Status das Guias

- **A** - Aguardando processamento
- **P** - Processando (enviando para DRG)
- **T** - Transmitida com sucesso
- **E** - Erro no processamento

## Exemplos de Uso

### Listar guias aguardando

```bash
curl "http://localhost:5000/api/v1/guias?status=A"
```

### Processar uma guia

```bash
curl -X POST "http://localhost:5000/api/v1/guias/1/processar"
```

### Verificar status do sistema

```bash
curl "http://localhost:5000/api/v1/status"
```
