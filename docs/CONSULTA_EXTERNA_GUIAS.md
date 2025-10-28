# 📋 **DOCUMENTAÇÃO - CONSULTA EXTERNA DE GUIAS**

## **🎯 VISÃO GERAL**

O sistema agora possui funcionalidade para consultar guias em rotas externas, permitindo verificar o status de aprovação e receber dados de retorno. Esta funcionalidade é **independente** do sistema atual e não quebra nada existente.

---

## **🔧 CONFIGURAÇÕES**

### **Variáveis de Ambiente (.env)**

```env
# Timeout para consultas externas (milissegundos)
CONSULTA_EXTERNA_TIMEOUT_MS=30000  # 30 segundos

# Intervalo mínimo entre consultas da mesma guia (milissegundos)
CONSULTA_EXTERNA_INTERVALO_MS=5000  # 5 segundos

# Máximo de tentativas para consulta externa
CONSULTA_EXTERNA_MAX_TENTATIVAS=3
```

### **Exemplos de Configuração**

```env
# Consulta rápida (5 segundos)
CONSULTA_EXTERNA_TIMEOUT_MS=5000
CONSULTA_EXTERNA_INTERVALO_MS=1000

# Consulta lenta (5 minutos)
CONSULTA_EXTERNA_TIMEOUT_MS=300000
CONSULTA_EXTERNA_INTERVALO_MS=60000
```

---

## **🚀 NOVAS ROTAS**

### **1. Consulta Individual**

**POST** `/guias/consulta-externa`

**Descrição:** Consulta uma guia específica em uma rota externa.

**Body:**

```json
{
  "url_destino": "https://api.externa.com/consultar-guia",
  "numero_guia": "R679542",
  "data_ultima_atualizacao": "2024-01-15T10:30:00Z"
}
```

**Resposta:**

```json
{
  "sucesso": true,
  "mensagem": "Consulta realizada com sucesso",
  "dados": {
    "aprovada": true,
    "numero_autorizacao": "AUT123456",
    "data_aprovacao": "2024-01-15T14:30:00Z"
  },
  "status_consulta": "R",
  "numero_guia": "R679542",
  "timestamp": "2024-01-15T14:30:00Z"
}
```

---

### **2. Consulta Múltipla**

**POST** `/guias/consulta-externa/multipla`

**Descrição:** Consulta múltiplas guias em lote.

**Body:**

```json
{
  "url_destino": "https://api.externa.com/consultar-guia",
  "guias": [
    {
      "numero_guia": "R679542",
      "data_ultima_atualizacao": "2024-01-15T10:30:00Z"
    },
    {
      "numero_guia": "R679543",
      "data_ultima_atualizacao": "2024-01-15T11:00:00Z"
    }
  ]
}
```

**Resposta:**

```json
{
  "sucesso": true,
  "total_processadas": 2,
  "sucessos": 2,
  "erros": 0,
  "resultados": [
    {
      "numero_guia": "R679542",
      "sucesso": true,
      "mensagem": "Consulta realizada com sucesso",
      "status_consulta": "R"
    },
    {
      "numero_guia": "R679543",
      "sucesso": true,
      "mensagem": "Consulta realizada com sucesso",
      "status_consulta": "R"
    }
  ],
  "timestamp": "2024-01-15T14:30:00Z"
}
```

---

### **3. Status de Consulta**

**GET** `/guias/{numero_guia}/status-consulta`

**Descrição:** Obtém o status de consulta externa de uma guia específica.

**Resposta:**

```json
{
  "numero_guia": "R679542",
  "status_consulta": "R",
  "data_ultima_consulta": "2024-01-15T14:30:00Z",
  "url_consulta_externa": "https://api.externa.com/consultar-guia",
  "dados_retornados": {
    "aprovada": true,
    "numero_autorizacao": "AUT123456"
  }
}
```

---

### **4. Estatísticas**

**GET** `/guias/consulta-externa/status`

**Descrição:** Obtém estatísticas das consultas externas realizadas.

**Resposta:**

```json
{
  "timestamp": "2024-01-15T14:30:00Z",
  "estatisticas": {
    "total_guias": 150,
    "pendentes": 45,
    "consultadas": 30,
    "retornadas": 75,
    "consultas_recentes_24h": 12
  },
  "urls_utilizadas": [
    "https://api.externa.com/consultar-guia",
    "https://outra-api.com/status"
  ],
  "configuracoes": {
    "timeout_ms": 30000,
    "intervalo_ms": 5000,
    "max_tentativas": 3
  }
}
```

---

## **📊 STATUS DE CONSULTA**

| Status | Descrição  | Comportamento                                      |
| ------ | ---------- | -------------------------------------------------- |
| **P**  | Pendente   | Guia nunca foi consultada externamente             |
| **C**  | Consultado | Guia foi consultada mas não retornou dados válidos |
| **R**  | Retornado  | Guia foi consultada e dados foram recebidos        |

---

## **🔄 FLUXO DE FUNCIONAMENTO**

### **1. Consulta Inicial**

```
Cliente → POST /guias/consulta-externa
Sistema → Busca guia no banco
Sistema → Verifica intervalo mínimo
Sistema → Consulta URL externa
Sistema → Atualiza status_consulta = "C" ou "R"
Sistema → Salva dados_retornados
```

### **2. Controle de Intervalo**

```
Se data_ultima_consulta < intervalo_configurado:
  → Retorna dados já armazenados
Senão:
  → Faz nova consulta externa
```

### **3. Detecção de Aprovação**

```
Se dados contêm indicadores de aprovação:
  → situacao_guia = "A" (Aprovada)
  → tp_status = "T" (Transmitida)
```

---

## **🛡️ SEGURANÇA E PERFORMANCE**

### **Rate Limiting**

- **Consulta individual:** 30/minuto
- **Consulta múltipla:** 10/minuto

### **Timeout Configurável**

- Padrão: 30 segundos
- Configurável via `.env`

### **Controle de Intervalo**

- Evita consultas excessivas
- Configurável por cliente

---

## **📝 EXEMPLOS DE USO**

### **Python/Requests**

```python
import requests

# Consulta individual
response = requests.post("http://localhost:8000/guias/consulta-externa", json={
    "url_destino": "https://api.externa.com/consultar-guia",
    "numero_guia": "R679542"
})

print(response.json())
```

### **JavaScript/Fetch**

```javascript
// Consulta múltipla
const response = await fetch("/guias/consulta-externa/multipla", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    url_destino: "https://api.externa.com/consultar-guia",
    guias: [{ numero_guia: "R679542" }, { numero_guia: "R679543" }],
  }),
});

const result = await response.json();
console.log(result);
```

### **cURL**

```bash
# Status de consulta
curl -X GET "http://localhost:8000/guias/R679542/status-consulta"

# Estatísticas
curl -X GET "http://localhost:8000/guias/consulta-externa/status"
```

---

## **🔧 MIGRAÇÃO DO BANCO**

### **SQLite (Automática)**

```bash
python migrar_consulta_externa.py
```

### **Oracle (Manual)**

```sql
-- Execute o script gerado
@migracao_oracle_consulta_externa.sql
```

---

## **✅ CHECKLIST DE IMPLEMENTAÇÃO**

- [x] ✅ Novos campos no modelo `Guia`
- [x] ✅ Configurações no `.env`
- [x] ✅ Serviço `ConsultaExternaService`
- [x] ✅ Schemas Pydantic
- [x] ✅ Rotas FastAPI
- [x] ✅ Script de migração
- [x] ✅ Documentação completa

---

## **🎯 BENEFÍCIOS**

1. **🔄 Independência:** Não quebra funcionalidades existentes
2. **⚙️ Configurável:** Timeout e intervalos ajustáveis por cliente
3. **📊 Rastreável:** Status e histórico de consultas
4. **🚀 Escalável:** Suporte a consultas em lote
5. **🛡️ Seguro:** Rate limiting e controle de tentativas
6. **📈 Monitorável:** Estatísticas e logs detalhados

---

**🎉 Sistema pronto para uso! Todas as funcionalidades foram implementadas com sucesso!**

