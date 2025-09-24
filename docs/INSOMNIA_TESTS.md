# 🧪 Testes com Insomnia - API DRG Externa

## 📋 Configuração Inicial

### **1. Importar Collection**

- Abra o Insomnia
- Clique em "Create" → "Import"
- Cole o JSON da collection abaixo

### **2. Configurar Environment**

- Clique em "Manage Environments"
- Crie um novo environment com as variáveis:

```json
{
  "auth_url": "https://api-autenticacao.iagsaude.com/login",
  "drg_url": "https://api-hospitalar.iagsaude.com/integracao/guias/save",
  "username": "seu_usuario_drg",
  "password": "sua_senha_drg",
  "api_key": "seu_codigo_unico_drg"
}
```

## 🚀 Collection para Insomnia

```json
{
  "_type": "export",
  "__export_format": 4,
  "__export_date": "2024-12-19T00:00:00.000Z",
  "__export_source": "insomnia.desktop.app:v2023.5.8",
  "resources": [
    {
      "_id": "req_auth_drg",
      "parentId": "fld_drg_auth",
      "modified": 1703030400000,
      "created": 1703030400000,
      "url": "{{ _.auth_url }}",
      "name": "Autenticação DRG",
      "description": "Obter token JWT para autenticação na API DRG",
      "method": "POST",
      "body": {
        "mimeType": "application/json",
        "text": "{\n  \"username\": \"{{ _.username }}\",\n  \"password\": \"{{ _.password }}\"\n}"
      },
      "parameters": [],
      "headers": [
        {
          "name": "Content-Type",
          "value": "application/json"
        }
      ],
      "authentication": {},
      "metaSortKey": -1703030400000,
      "isPrivate": false,
      "settingStoreCookies": true,
      "settingSendCookies": true,
      "settingDisableRenderRequestBody": false,
      "settingEncodeUrl": true,
      "settingRebuildPath": true,
      "settingFollowRedirects": "global",
      "_type": "request"
    },
    {
      "_id": "req_enviar_guias",
      "parentId": "fld_drg_guias",
      "modified": 1703030400000,
      "created": 1703030400000,
      "url": "{{ _.drg_url }}",
      "name": "Enviar Lote de Guias",
      "description": "Enviar lote de guias para processamento na API DRG",
      "method": "POST",
      "body": {
        "mimeType": "application/json",
        "text": "{\n  \"loteGuias\": {\n    \"guia\": [\n      {\n        \"codigoOperadora\": \"12345\",\n        \"numeroGuia\": \"96312341\",\n        \"numeroGuiaOperadora\": \"OP123456\",\n        \"numeroGuiaInternacao\": \"INT789\",\n        \"dataAutorizacao\": \"2024-12-19\",\n        \"senha\": \"SENHA123\",\n        \"dataValidade\": \"2024-12-26\",\n        \"numeroCarteira\": \"12345678901\",\n        \"dataValidadeCarteira\": \"2025-12-31\",\n        \"rn\": \"N\",\n        \"dataNascimento\": \"1990-01-15\",\n        \"sexo\": \"M\",\n        \"situacaoBeneficiario\": \"A\",\n        \"codigoPrestador\": \"PREST001\",\n        \"nomePrestador\": \"Hospital Exemplo\",\n        \"nomeProfissional\": \"Dr. João Silva\",\n        \"codigoProfissional\": \"PROF001\",\n        \"numeroRegistroProfissional\": \"CRM123456\",\n        \"ufProfissional\": \"SP\",\n        \"codigoCbo\": \"225125\",\n        \"codigoContratado\": \"CONT001\",\n        \"nomeHospital\": \"Hospital Exemplo\",\n        \"dataSugeridaInternacao\": \"2024-12-20\",\n        \"caraterAtendimento\": \"1\",\n        \"tipoInternacao\": \"1\",\n        \"regimeInternacao\": \"1\",\n        \"diariasSolicitadas\": \"5\",\n        \"previsaoUsoOpme\": \"N\",\n        \"previsaoUsoQuimioterapico\": \"N\",\n        \"indicacaoClinica\": \"Indicação clínica detalhada\",\n        \"indicacaoAcidente\": \"N\",\n        \"tipoAcomodacaoSolicitada\": \"1\",\n        \"dataAdmissaoEstimada\": \"2024-12-20\",\n        \"qtdeDiariasAutorizadas\": \"5\",\n        \"tipoAcomodacaoAutorizada\": \"1\",\n        \"cnesAutorizado\": \"1234567\",\n        \"observacaoGuia\": \"Observações da guia\",\n        \"dataSolicitacao\": \"2024-12-19\",\n        \"justificativaOperadora\": \"Justificativa da operadora\",\n        \"naturezaGuia\": \"1\",\n        \"guiaComplementar\": \"N\",\n        \"situacaoGuia\": \"A\",\n        \"tipoDoenca\": \"1\",\n        \"tempoDoenca\": \"30\",\n        \"longaPermanencia\": \"N\",\n        \"motivoEncerramento\": \"\",\n        \"tipoAlta\": \"\",\n        \"dataAlta\": \"\",\n        \"anexo\": [\n          {\n            \"numeroLoteDocumento\": \"LOTE001\",\n            \"numeroProtocoloDocumento\": \"PROT001\",\n            \"formatoDocumento\": \"PDF\",\n            \"sequencialDocumento\": \"1\",\n            \"dataCriacao\": \"2024-12-19\",\n            \"nome\": \"Documento Exemplo.pdf\",\n            \"urlDocumento\": \"https://exemplo.com/doc.pdf\",\n            \"observacaoDocumento\": \"Observação do documento\",\n            \"tipoDocumento\": \"1\"\n          }\n        ],\n        \"procedimento\": [\n          {\n            \"tabela\": \"TUSS\",\n            \"codigo\": \"31001017\",\n            \"descricao\": \"Consulta médica\",\n            \"qtdeSolicitada\": \"1\",\n            \"valorUnitario\": \"150.00\",\n            \"qtdeAutorizada\": \"1\"\n          }\n        ],\n        \"diagnostico\": [\n          {\n            \"codigo\": \"Z00.0\",\n            \"tipo\": \"1\"\n          }\n        ]\n      }\n    ]\n  }\n}"
      },
      "parameters": [],
      "headers": [
        {
          "name": "Content-Type",
          "value": "application/json"
        },
        {
          "name": "Authorization",
          "value": "Bearer {{ _.auth_token }}"
        },
        {
          "name": "x-api-key",
          "value": "{{ _.api_key }}"
        }
      ],
      "authentication": {},
      "metaSortKey": -1703030400000,
      "isPrivate": false,
      "settingStoreCookies": true,
      "settingSendCookies": true,
      "settingDisableRenderRequestBody": false,
      "settingEncodeUrl": true,
      "settingRebuildPath": true,
      "settingFollowRedirects": "global",
      "_type": "request"
    },
    {
      "_id": "fld_drg_auth",
      "parentId": "wrk_main",
      "modified": 1703030400000,
      "created": 1703030400000,
      "name": "Autenticação DRG",
      "description": "Endpoints de autenticação da API DRG",
      "environment": {},
      "environmentPropertyOrder": null,
      "metaSortKey": -1703030400000,
      "_type": "request_group"
    },
    {
      "_id": "fld_drg_guias",
      "parentId": "wrk_main",
      "modified": 1703030400000,
      "created": 1703030400000,
      "name": "Guias DRG",
      "description": "Endpoints para envio de guias para API DRG",
      "environment": {},
      "environmentPropertyOrder": null,
      "metaSortKey": -1703030400000,
      "_type": "request_group"
    },
    {
      "_id": "wrk_main",
      "parentId": null,
      "modified": 1703030400000,
      "created": 1703030400000,
      "name": "API DRG Externa - Guias de Internação",
      "description": "Collection para testes da API externa do DRG Brasil",
      "scope": "collection",
      "_type": "workspace"
    }
  ]
}
```

## 📝 Exemplos de Teste

### **1. Autenticação DRG**

```http
POST https://api-autenticacao.iagsaude.com/login
Content-Type: application/json

{
  "username": "seu_usuario_drg",
  "password": "sua_senha_drg"
}
```

**Resposta esperada:**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 14400,
  "type": "Bearer"
}
```

### **2. Enviar Lote de Guias**

```http
POST https://api-hospitalar.iagsaude.com/integracao/guias/save
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
x-api-key: seu_codigo_unico_drg

{
  "loteGuias": {
    "guia": [
      {
        "codigoOperadora": "12345",
        "numeroGuia": "96312341",
        "numeroGuiaOperadora": "OP123456",
        "numeroGuiaInternacao": "INT789",
        "dataAutorizacao": "2024-12-19",
        "senha": "SENHA123",
        "dataValidade": "2024-12-26",
        "numeroCarteira": "12345678901",
        "dataValidadeCarteira": "2025-12-31",
        "rn": "N",
        "dataNascimento": "1990-01-15",
        "sexo": "M",
        "situacaoBeneficiario": "A",
        "codigoPrestador": "PREST001",
        "nomePrestador": "Hospital Exemplo",
        "nomeProfissional": "Dr. João Silva",
        "codigoProfissional": "PROF001",
        "numeroRegistroProfissional": "CRM123456",
        "ufProfissional": "SP",
        "codigoCbo": "225125",
        "codigoContratado": "CONT001",
        "nomeHospital": "Hospital Exemplo",
        "dataSugeridaInternacao": "2024-12-20",
        "caraterAtendimento": "1",
        "tipoInternacao": "1",
        "regimeInternacao": "1",
        "diariasSolicitadas": "5",
        "previsaoUsoOpme": "N",
        "previsaoUsoQuimioterapico": "N",
        "indicacaoClinica": "Indicação clínica detalhada",
        "indicacaoAcidente": "N",
        "tipoAcomodacaoSolicitada": "1",
        "dataAdmissaoEstimada": "2024-12-20",
        "qtdeDiariasAutorizadas": "5",
        "tipoAcomodacaoAutorizada": "1",
        "cnesAutorizado": "1234567",
        "observacaoGuia": "Observações da guia",
        "dataSolicitacao": "2024-12-19",
        "justificativaOperadora": "Justificativa da operadora",
        "naturezaGuia": "1",
        "guiaComplementar": "N",
        "situacaoGuia": "A",
        "tipoDoenca": "1",
        "tempoDoenca": "30",
        "longaPermanencia": "N",
        "motivoEncerramento": "",
        "tipoAlta": "",
        "dataAlta": "",
        "anexo": [
          {
            "numeroLoteDocumento": "LOTE001",
            "numeroProtocoloDocumento": "PROT001",
            "formatoDocumento": "PDF",
            "sequencialDocumento": "1",
            "dataCriacao": "2024-12-19",
            "nome": "Documento Exemplo.pdf",
            "urlDocumento": "https://exemplo.com/doc.pdf",
            "observacaoDocumento": "Observação do documento",
            "tipoDocumento": "1"
          }
        ],
        "procedimento": [
          {
            "tabela": "TUSS",
            "codigo": "31001017",
            "descricao": "Consulta médica",
            "qtdeSolicitada": "1",
            "valorUnitario": "150.00",
            "qtdeAutorizada": "1"
          }
        ],
        "diagnostico": [
          {
            "codigo": "Z00.0",
            "tipo": "1"
          }
        ]
      }
    ]
  }
}
```

**Resposta esperada:**

```json
{
  "logInternacao": {
    "logGuias": {
      "guia": [
        {
          "numeroGuia": "96312341",
          "situacao": "S",
          "erro": null
        }
      ]
    }
  }
}
```

## 🔧 Configuração de Ambiente

### **Variáveis de Ambiente no Insomnia**

```json
{
  "auth_url": "https://api-autenticacao.iagsaude.com/login",
  "drg_url": "https://api-hospitalar.iagsaude.com/integracao/guias/save",
  "username": "seu_usuario_drg",
  "password": "sua_senha_drg",
  "api_key": "seu_codigo_unico_drg",
  "auth_token": "token_jwt_obtido_da_autenticacao"
}
```

### **Headers Padrão**

```
Content-Type: application/json
Authorization: Bearer {{ _.auth_token }}
x-api-key: {{ _.api_key }}
```

## 🚀 Como Usar

1. **Importe a collection** no Insomnia
2. **Configure o environment** com suas credenciais DRG
3. **Execute primeiro** a autenticação para obter o token JWT
4. **Copie o token** da resposta e cole na variável `auth_token` do environment
5. **Execute o envio** de guias com o token configurado

## 📊 Fluxo de Teste

### **Passo 1: Autenticação**

- Execute "Autenticação DRG"
- Copie o token da resposta
- Cole na variável `auth_token` do environment

### **Passo 2: Envio de Guias**

- Execute "Enviar Lote de Guias"
- Verifique a resposta com log de processamento

## 🐛 Troubleshooting

### **Erro 401 - Unauthorized**

- Verifique se as credenciais estão corretas
- Confirme se o token JWT ainda é válido (expira em 4h)
- Execute novamente a autenticação

### **Erro 403 - Forbidden**

- Verifique se o `x-api-key` está correto
- Confirme se o usuário tem permissão para enviar guias

### **Erro 400 - Bad Request**

- Verifique a estrutura do JSON
- Confirme se todos os campos obrigatórios estão preenchidos
- Verifique se o tamanho do lote não excede 500KB

### **Erro 500 - Internal Server Error**

- Aguarde alguns minutos e tente novamente
- Verifique se a API DRG está funcionando
- Entre em contato com o suporte DRG se persistir

## ⚠️ Observações Importantes

- **Token JWT**: Expira em 4 horas, renove quando necessário
- **Tamanho do lote**: Máximo 500KB por requisição
- **Rate limiting**: Respeite os limites da API DRG
- **Dados de teste**: Use apenas dados fictícios para testes
- **Ambiente**: Confirme se está testando no ambiente correto (homologação/produção)

---

**💡 Dica:** Sempre teste primeiro a autenticação e depois o envio de guias!
