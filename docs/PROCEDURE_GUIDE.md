# 📋 Guia para Criação de Procedure - Sistema DRG

## 🗄️ Estrutura das Tabelas

### 📊 Tabela Principal - `inovemed_tbl_guias`

**Função:** Armazena os dados principais da guia de internação.

```sql
CREATE TABLE inovemed_tbl_guias (
    -- Campos principais
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_guia VARCHAR(20) UNIQUE NOT NULL,
    codigo_operadora VARCHAR(6) NOT NULL,
    numero_guia_operadora VARCHAR(20),
    numero_guia_internacao VARCHAR(20),
    data_autorizacao DATE NOT NULL,
    senha VARCHAR(20),
    data_validade DATE,

    -- Dados do beneficiário
    numero_carteira VARCHAR(20) NOT NULL,
    data_validade_carteira DATE,
    rn VARCHAR(1),  -- S/N
    data_nascimento DATETIME NOT NULL,
    sexo VARCHAR(1) NOT NULL,  -- M/F/I
    situacao_beneficiario VARCHAR(1) NOT NULL,  -- A/I

    -- Dados do prestador
    codigo_prestador VARCHAR(14) NOT NULL,
    nome_prestador VARCHAR(70) NOT NULL,
    nome_profissional VARCHAR(70),
    codigo_profissional VARCHAR(2) NOT NULL,
    numero_registro_profissional VARCHAR(15) NOT NULL,
    uf_profissional VARCHAR(2) NOT NULL,
    codigo_cbo VARCHAR(6) NOT NULL,

    -- Dados do hospital
    codigo_contratado VARCHAR(14) NOT NULL,
    nome_hospital VARCHAR(70) NOT NULL,
    data_sugerida_internacao DATE NOT NULL,
    carater_atendimento VARCHAR(1) NOT NULL,  -- 1-5
    tipo_internacao VARCHAR(1) NOT NULL,  -- 1-5
    regime_internacao VARCHAR(1) NOT NULL,  -- 1-5
    diarias_solicitadas INTEGER NOT NULL,
    previsao_uso_opme VARCHAR(1),  -- S/N
    previsao_uso_quimioterapico VARCHAR(1),  -- S/N
    indicacao_clinica TEXT NOT NULL,
    indicacao_acidente VARCHAR(1) NOT NULL,  -- 0-2
    tipo_acomodacao_solicitada VARCHAR(2),  -- 1-2

    -- Dados da autorização
    data_admissao_estimada DATE,
    qtde_diarias_autorizadas INTEGER,
    tipo_acomodacao_autorizada VARCHAR(2),
    cnes_autorizado VARCHAR(7),
    observacao_guia TEXT,
    data_solicitacao DATE NOT NULL,
    justificativa_operadora TEXT,

    -- Dados complementares
    natureza_guia VARCHAR(1) NOT NULL,  -- 1-6
    guia_complementar VARCHAR(1) NOT NULL,  -- S/N
    situacao_guia VARCHAR(2) NOT NULL,  -- A/P/N/C/S
    tipo_doenca VARCHAR(1),  -- 1-2
    tempo_doenca INTEGER,
    longa_permanencia VARCHAR(1),  -- 1-2
    motivo_encerramento VARCHAR(2),  -- 1-5,9
    tipo_alta VARCHAR(2),  -- 1-8
    data_alta DATE,

    -- Campos de controle
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    tp_status VARCHAR(1) NOT NULL DEFAULT 'A',  -- CRÍTICO: 'A' = Aguardando processamento
    data_processamento DATETIME,
    mensagem_erro TEXT,
    tentativas INTEGER DEFAULT 0
);
```

### 📎 Tabela Anexos - `inovemed_tbl_anexos`

**Função:** Armazena documentos anexos da guia.

```sql
CREATE TABLE inovemed_tbl_anexos (
    -- Campos principais
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_lote_documento VARCHAR(12),
    numero_protocolo_documento VARCHAR(12),
    formato_documento VARCHAR(2) NOT NULL,  -- 1-5, 99
    sequencial_documento INTEGER,
    data_criacao DATE NOT NULL,
    nome VARCHAR(500) NOT NULL,
    url_documento VARCHAR(500) NOT NULL,
    observacao_documento VARCHAR(500),
    tipo_documento VARCHAR(2) NOT NULL,  -- 01-04, 99

    -- Chave estrangeira
    guia_id INTEGER NOT NULL,
    FOREIGN KEY (guia_id) REFERENCES inovemed_tbl_guias(id)
);
```

### 🔧 Tabela Procedimentos - `inovemed_tbl_procedimentos`

**Função:** Armazena procedimentos médicos da guia.

```sql
CREATE TABLE inovemed_tbl_procedimentos (
    -- Campos principais
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tabela VARCHAR(2) NOT NULL,  -- 00, 20, 22, 98
    codigo VARCHAR(10) NOT NULL,
    descricao VARCHAR(150) NOT NULL,
    qtde_solicitada INTEGER NOT NULL,
    valor_unitario NUMERIC(8,2) NOT NULL,
    qtde_autorizada INTEGER NOT NULL,

    -- Chave estrangeira
    guia_id INTEGER NOT NULL,
    FOREIGN KEY (guia_id) REFERENCES inovemed_tbl_guias(id)
);
```

### 🏥 Tabela Diagnósticos - `inovemed_tbl_diagnosticos`

**Função:** Armazena diagnósticos médicos (CID-10) da guia.

```sql
CREATE TABLE inovemed_tbl_diagnosticos (
    -- Campos principais
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo VARCHAR(4) NOT NULL,  -- CID-10
    tipo VARCHAR(1) NOT NULL,  -- P (Primário) ou S (Secundário)

    -- Chave estrangeira
    guia_id INTEGER NOT NULL,
    FOREIGN KEY (guia_id) REFERENCES inovemed_tbl_guias(id)
);
```

## 🔗 Relacionamentos

```
inovemed_tbl_guias (id)
    ↓
    ├── inovemed_tbl_anexos (guia_id)
    ├── inovemed_tbl_procedimentos (guia_id)
    └── inovemed_tbl_diagnosticos (guia_id)
```

## ⚙️ Como Criar a Procedure

### 📋 Passos Obrigatórios

1. **Inserir na tabela principal** com `tp_status = 'A'`
2. **Capturar o ID** retornado da inserção
3. **Usar o ID** para inserir nas tabelas relacionadas
4. **Fazer COMMIT** da transação completa

### 🔄 Fluxo da Procedure

```sql
-- 1. Inserir guia principal
INSERT INTO inovemed_tbl_guias (...) VALUES (...) RETURNING id INTO v_guia_id;

-- 2. Inserir anexos (se houver)
INSERT INTO inovemed_tbl_anexos (guia_id, ...) VALUES (v_guia_id, ...);

-- 3. Inserir procedimentos (se houver)
INSERT INTO inovemed_tbl_procedimentos (guia_id, ...) VALUES (v_guia_id, ...);

-- 4. Inserir diagnósticos (se houver)
INSERT INTO inovemed_tbl_diagnosticos (guia_id, ...) VALUES (v_guia_id, ...);

-- 5. Confirmar transação
COMMIT;
```

### ⚠️ Pontos Críticos

- **`tp_status = 'A'`** - API só processa guias com este status
- **`RETURNING id INTO`** - Para capturar o ID da guia
- **`guia_id`** - FK em todas as tabelas relacionadas
- **Transação completa** - COMMIT/ROLLBACK adequados

## 🤖 Processamento Automático

Após a inserção com `tp_status = 'A'`:

1. **API monitora** a tabela automaticamente
2. **Detecta nova guia** com status 'A'
3. **Busca dados relacionados** (anexos, procedimentos, diagnósticos)
4. **Monta JSON completo** para envio
5. **Envia para API DRG** externa
6. **Atualiza status** para 'T' (Transmitida) ou 'E' (Erro)

## 📊 Status da Guia

- **'A'** - Aguardando processamento (inserir com este status)
- **'P'** - Processando (API está enviando)
- **'T'** - Transmitida com sucesso
- **'E'** - Erro no processamento

## ✅ Checklist da Procedure

- [ ] Inserir na tabela principal com `tp_status = 'A'`
- [ ] Capturar ID retornado
- [ ] Inserir anexos com `guia_id`
- [ ] Inserir procedimentos com `guia_id`
- [ ] Inserir diagnósticos com `guia_id`
- [ ] Fazer COMMIT da transação
- [ ] Tratar erros com ROLLBACK

## 🎯 Resultado Esperado

Após executar a procedure com sucesso:

- Guia inserida com status 'A'
- Dados relacionados inseridos
- API detecta automaticamente
- Processamento inicia em até 1 minuto
- Status atualizado para 'T' ou 'E'
