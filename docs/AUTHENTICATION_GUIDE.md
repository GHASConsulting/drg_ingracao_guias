# 🔐 Guia de Autenticação JWT - Sistema DRG

Este guia explica como usar o sistema de autenticação JWT implementado no sistema DRG.

## 📋 **Como Funciona a Autenticação**

### **1. Conceito Básico:**

- **JWT (JSON Web Token)** = Um "bilhete" digital que prova quem você é
- **Token** = Uma string longa que contém suas informações de login
- **Bearer Authentication** = Você "porta" o token em cada requisição

### **2. Fluxo de Autenticação:**

```
1. Login → Recebe Token
2. Usa Token → Acessa API
3. Token Expira → Faz Login Novamente
```

## 🗄️ **Sistema de Usuários e Tabelas**

### **Tabela: `usuarios`**

```sql
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,                    -- ID único
    username VARCHAR(50) UNIQUE NOT NULL,     -- Nome de usuário
    email VARCHAR(100) UNIQUE NOT NULL,       -- Email
    password_hash VARCHAR(255) NOT NULL,      -- Senha criptografada
    full_name VARCHAR(100),                   -- Nome completo
    role VARCHAR(20) DEFAULT 'user',          -- Papel: admin, user, readonly
    is_active BOOLEAN DEFAULT true,           -- Usuário ativo?
    is_superuser BOOLEAN DEFAULT false,       -- Super administrador?
    created_at TIMESTAMP DEFAULT NOW(),       -- Data de criação
    updated_at TIMESTAMP,                     -- Última atualização
    last_login TIMESTAMP,                     -- Último login
    created_by INTEGER,                       -- Quem criou este usuário
    updated_by INTEGER                        -- Quem atualizou por último
);
```

### **Tipos de Usuários (Roles):**

#### **👑 ADMIN**

- **Pode fazer:** Tudo
- **Exemplos:** Criar usuários, parar/iniciar monitoramento, acessar logs de segurança
- **Endpoints:** Todos

#### **👤 USER**

- **Pode fazer:** Operações básicas
- **Exemplos:** Ver guias, processar dados, alterar própria senha
- **NÃO pode:** Criar usuários, controlar monitoramento

#### **👁️ READONLY**

- **Pode fazer:** Apenas visualizar
- **Exemplos:** Ver status, listar guias, health check
- **NÃO pode:** Processar dados, alterar configurações

## 🚀 **Como Usar - Passo a Passo**

### **Passo 1: Fazer Login**

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Resposta:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@drg.com",
    "role": "admin",
    "is_active": true
  }
}
```

### **Passo 2: Usar o Token**

**Copie o `access_token` e use em todas as requisições:**

```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### **Passo 3: Acessar Endpoints Protegidos**

```bash
# Ver informações do usuário atual
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"

# Ver guias (usuário comum)
curl -X GET http://localhost:8000/api/v1/guias \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"

# Iniciar monitoramento (apenas admin)
curl -X POST http://localhost:8000/api/v1/monitoramento/start \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"
```

## 📱 **Usando com Postman/Insomnia**

### **1. Configurar Autenticação:**

1. Vá para a aba **Authorization**
2. Selecione **Bearer Token**
3. Cole o token recebido no login

### **2. Exemplo de Requisição:**

```
GET http://localhost:8000/api/v1/guias
Headers:
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 🛠️ **Gerenciamento de Usuários (Apenas Admins)**

### **Criar Novo Usuário:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Authorization: Bearer SEU_TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "operador1",
    "email": "operador@empresa.com",
    "password": "senha123",
    "full_name": "Operador 1",
    "role": "user",
    "is_active": true
  }'
```

### **Listar Usuários:**

```bash
curl -X GET http://localhost:8000/api/v1/auth/users \
  -H "Authorization: Bearer SEU_TOKEN_ADMIN"
```

### **Alterar Senha (Própria):**

```bash
curl -X POST http://localhost:8000/api/v1/auth/change-password \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "admin123",
    "new_password": "novasenha456"
  }'
```

## 🔒 **Endpoints por Nível de Acesso**

### **🌐 Públicos (Sem Autenticação):**

- `GET /health` - Health check
- `POST /auth/login` - Login
- `POST /auth/init-admin` - Criar admin inicial

### **👤 Usuário Comum:**

- `GET /auth/me` - Minhas informações
- `POST /auth/change-password` - Alterar minha senha
- `GET /guias` - Ver guias
- `GET /guias/{id}` - Ver guia específica
- `GET /status` - Status do sistema
- `GET /monitoramento/status` - Status do monitoramento

### **👑 Apenas Admin:**

- `POST /auth/register` - Criar usuários
- `GET /auth/users` - Listar usuários
- `PUT /auth/users/{id}` - Editar usuários
- `DELETE /auth/users/{id}` - Desativar usuários
- `POST /monitoramento/start` - Iniciar monitoramento
- `POST /monitoramento/stop` - Parar monitoramento

### **👁️ Apenas Readonly:**

- `GET /health` - Health check
- `GET /status` - Status básico
- `GET /guias` - Ver guias (sem processar)
- `GET /monitoramento/status` - Status do monitoramento

## 🚨 **Códigos de Erro Comuns**

### **401 - Não Autorizado:**

```json
{
  "detail": "Token de acesso inválido ou expirado"
}
```

**Solução:** Fazer login novamente

### **403 - Acesso Negado:**

```json
{
  "detail": "Acesso negado. Permissões de administrador necessárias"
}
```

**Solução:** Usar conta de admin ou solicitar permissão

### **422 - Erro de Validação:**

```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "Senha deve ter pelo menos 6 caracteres"
    }
  ]
}
```

**Solução:** Corrigir os dados enviados

## ⏰ **Expiração de Token**

- **Duração:** 30 minutos
- **O que acontece:** Token expira automaticamente
- **Como resolver:** Fazer login novamente
- **Dica:** Guarde as credenciais para re-login rápido

## 🎯 **Exemplos Práticos**

### **Cenário 1: Operador Diário**

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "operador1", "password": "senha123"}' \
  | jq -r '.access_token')

# 2. Ver guias
curl -X GET http://localhost:8000/api/v1/guias \
  -H "Authorization: Bearer $TOKEN"

# 3. Ver status
curl -X GET http://localhost:8000/api/v1/status \
  -H "Authorization: Bearer $TOKEN"
```

### **Cenário 2: Administrador**

```bash
# 1. Login como admin
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  | jq -r '.access_token')

# 2. Criar novo usuário
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "supervisor",
    "email": "supervisor@empresa.com",
    "password": "super123",
    "full_name": "Supervisor",
    "role": "admin"
  }'

# 3. Parar monitoramento
curl -X POST http://localhost:8000/api/v1/monitoramento/stop \
  -H "Authorization: Bearer $TOKEN"
```

## 🛡️ **Segurança**

### **Boas Práticas:**

- ✅ **Nunca compartilhe** tokens
- ✅ **Use HTTPS** em produção
- ✅ **Altere senhas padrão** imediatamente
- ✅ **Faça logout** quando terminar
- ✅ **Use senhas fortes** (mínimo 6 caracteres)

### **Tokens são Seguros?**

- ✅ **Sim:** Criptografados e com expiração
- ✅ **Não contêm senhas:** Apenas informações básicas
- ✅ **Expiração automática:** 30 minutos
- ✅ **Logs de acesso:** Todas as ações são registradas

## 🔧 **Troubleshooting**

### **"Token inválido"**

1. Verifique se copiou o token completo
2. Verifique se o token não expirou (30 min)
3. Faça login novamente

### **"Acesso negado"**

1. Verifique se tem permissão para o endpoint
2. Use conta de admin para operações administrativas
3. Verifique se sua conta está ativa

### **"Usuário não encontrado"**

1. Verifique se o username está correto
2. Verifique se a conta está ativa
3. Solicite ao admin para verificar

## 📞 **Suporte**

### **Usuário Admin Padrão:**

- **Username:** `admin`
- **Password:** `admin123`
- **Email:** `admin@drg.com`

### **Comandos Úteis:**

```bash
# Ver logs de autenticação
docker compose --profile production logs drg-api | grep -i "auth\|login"

# Verificar usuários no banco
docker compose --profile production exec postgres psql -U drg_user -d drg_guias -c "SELECT username, role, is_active FROM usuarios;"

# Reiniciar aplicação
docker compose --profile production restart drg-api
```

---

## 🎉 **Resumo Rápido**

1. **Faça login** → Receba token
2. **Use token** → Acesse endpoints
3. **Token expira** → Faça login novamente
4. **Diferentes roles** → Diferentes permissões
5. **Admin pode tudo** → Usuários têm limitações

**A autenticação JWT torna sua API segura e profissional!** 🔐✨
