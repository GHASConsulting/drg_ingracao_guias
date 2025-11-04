# 🔍 Como Verificar se as Tabelas Foram Criadas no Banco

Existem **3 formas** de verificar se as tabelas foram criadas corretamente:

---

## 📋 **Opção 1: Script Python (Recomendado)**

Execute o script Python que verifica automaticamente:

```bash
python verificar_tabelas.py
```

Este script vai:
- ✅ Verificar se todas as 4 tabelas existem
- ✅ Mostrar a estrutura das colunas principais
- ✅ Contar registros em cada tabela
- ✅ Mostrar estatísticas por status das guias

---

## 📋 **Opção 2: SQL Direto no Oracle**

Conecte-se ao Oracle usando SQL Developer, SQL*Plus ou qualquer cliente SQL e execute:

```sql
-- Verificar se as tabelas existem
SELECT 
    table_name,
    num_rows,
    last_analyzed
FROM 
    user_tables
WHERE 
    table_name IN (
        'INOVEMED_TBL_GUIAS',
        'INOVEMED_TBL_ANEXOS',
        'INOVEMED_TBL_PROCEDIMENTOS',
        'INOVEMED_TBL_DIAGNOSTICOS'
    )
ORDER BY 
    table_name;
```

Ou execute o arquivo completo:

```bash
# No SQL*Plus ou SQL Developer
@verificar_tabelas.sql
```

---

## 📋 **Opção 3: Verificar Durante a Execução da API**

Quando você iniciar a aplicação com `./start_drg_api_prod.sh`, procure nos logs:

```
INFO:app.database.database:Banco de dados inicializado: oracle
```

Se aparecer algum erro de tabela não encontrada, as tabelas não foram criadas.

---

## 🔧 **Se as Tabelas NÃO Foram Criadas**

Execute este comando para criar as tabelas:

```bash
python -c "from app.database.database import init_db; init_db()"
```

Ou dentro do Python:

```python
from app.database.database import init_db
init_db()
print("✅ Tabelas criadas!")
```

---

## 📊 **Tabelas Esperadas**

As seguintes tabelas devem existir:

1. ✅ `INOVEMED_TBL_GUIAS` - Tabela principal de guias
2. ✅ `INOVEMED_TBL_ANEXOS` - Anexos das guias
3. ✅ `INOVEMED_TBL_PROCEDIMENTOS` - Procedimentos das guias
4. ✅ `INOVEMED_TBL_DIAGNOSTICOS` - Diagnósticos das guias

---

## ⚠️ **Nota Importante**

- O Oracle é **case-sensitive** para nomes de tabelas entre aspas
- Os nomes das tabelas são criados em **minúsculas** (com aspas)
- Se você criou as tabelas manualmente em **maiúsculas**, pode haver conflito

Para verificar no Oracle, use:

```sql
SELECT table_name FROM user_tables WHERE LOWER(table_name) LIKE 'inovemed_tbl%';
```

