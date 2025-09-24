# Banco de Dados - Sistema DRG (FastAPI)

Esta pasta contém os arquivos de banco de dados do sistema.

## Arquivos

### Banco de Teste

- `teste_drg.db` - Banco SQLite com dados fictícios para desenvolvimento e testes

## Estrutura do Banco

### Tabelas Principais

- `inovemed_tbl_guias` - Guias de internação
- `inovemed_tbl_anexos` - Anexos das guias
- `inovemed_tbl_procedimentos` - Procedimentos das guias
- `inovemed_tbl_diagnosticos` - Diagnósticos das guias

### Status das Guias

- **A** - Aguardando processamento
- **T** - Transmitida com sucesso
- **E** - Erro no processamento
- **P** - Processando

## Como Visualizar

### No Cursor

1. Instale a extensão SQLite
2. Abra o arquivo `teste_drg.db`
3. Execute queries SQL

### Queries Úteis

```sql
-- Ver todas as guias
SELECT * FROM inovemed_tbl_guias;

-- Ver guias por status
SELECT numero_guia, nome_hospital, tp_status
FROM inovemed_tbl_guias;

-- Ver anexos
SELECT * FROM inovemed_tbl_anexos;

-- Ver procedimentos
SELECT * FROM inovemed_tbl_procedimentos;

-- Ver diagnósticos
SELECT * FROM inovemed_tbl_diagnosticos;

-- Contar guias por status
SELECT tp_status, COUNT(*) as total
FROM inovemed_tbl_guias
GROUP BY tp_status;
```

## Recriar Banco

Para recriar o banco com dados frescos:

```bash
python tests/criar_banco_teste.py
```

## Configuração

### SQLite (Desenvolvimento)

```bash
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///database/teste_drg.db
```

### Oracle (Produção)

```bash
DATABASE_TYPE=oracle
DATABASE_URL=oracle://usuario:senha@localhost:1521/XE
```

### PostgreSQL (Alternativa)

```bash
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://usuario:senha@localhost:5432/drg_guias
```

### Firebird (Alternativa)

```bash
DATABASE_TYPE=firebird
DATABASE_URL=firebird://usuario:senha@localhost:3050/drg_guias.fdb
```

## Status Atual

### ✅ **Banco Funcionando**

- **SQLite** configurado e operacional
- **Dados de teste** carregados
- **Tabelas criadas** automaticamente
- **Relacionamentos** funcionando

### **Dados de Teste Disponíveis**

- **1 guia** com status "A" (Aguardando)
- **1 anexo** completo
- **1 procedimento** completo
- **1 diagnóstico** completo

## Comandos Úteis

```bash
# Verificar status da API
curl http://localhost:8000/api/v1/status

# Listar guias via API
curl http://localhost:8000/api/v1/guias

# Adicionar mais dados
python adicionar_guias.py

# Executar testes
python testar_api.py
```

## Migração

O sistema suporta múltiplos bancos de dados. Para migrar:

1. **Configure** o `.env` com o novo banco
2. **Execute** a aplicação
3. **Tabelas** serão criadas automaticamente
4. **Dados** podem ser migrados via scripts

---

_Última atualização: 2025-09-23 - FastAPI_
