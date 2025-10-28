# 🗄️ Database Schema - Sistema DRG

Este documento descreve a estrutura das tabelas do banco de dados e como criar uma procedure para alimentar os dados.

## 📋 **Estrutura das Tabelas**

### **1. Tabela Principal: `inovemed_tbl_guias`**

```sql
CREATE TABLE inovemed_tbl_guias (
    id SERIAL PRIMARY KEY,
    numero_guia VARCHAR(50) NOT NULL,
    numero_guia_operadora VARCHAR(50),
    numero_guia_internacao VARCHAR(50),
    data_autorizacao DATE,
    senha VARCHAR(20),
    data_validade DATE,
    numero_carteira VARCHAR(50),
    data_validade_carteira DATE,
    rn VARCHAR(1),
    data_nascimento TIMESTAMP,
    sexo VARCHAR(1),
    situacao_beneficiario VARCHAR(1),
    codigo_prestador VARCHAR(20),
    nome_prestador VARCHAR(255),
    nome_profissional VARCHAR(255),
    codigo_profissional VARCHAR(10),
    numero_registro_profissional VARCHAR(50),
    uf_profissional VARCHAR(2),
    codigo_cbo VARCHAR(10),
    codigo_contratado VARCHAR(20),
    nome_hospital VARCHAR(255),
    data_sugerida_internacao DATE,
    carater_atendimento VARCHAR(1),
    tipo_internacao VARCHAR(1),
    regime_internacao VARCHAR(1),
    diarias_solicitadas INTEGER,
    previsao_uso_opme VARCHAR(1),
    previsao_uso_quimioterapico VARCHAR(1),
    indicacao_clinica TEXT,
    indicacao_acidente VARCHAR(1),
    tipo_acomodacao_solicitada VARCHAR(2),
    data_admissao_estimada DATE,
    qtde_diarias_autorizadas INTEGER,
    tipo_acomodacao_autorizada VARCHAR(2),
    cnes_autorizado VARCHAR(20),
    observacao_guia TEXT,
    data_solicitacao DATE,
    justificativa_operadora TEXT,
    natureza_guia VARCHAR(1),
    guia_complementar VARCHAR(1),
    situacao_guia VARCHAR(1),
    tipo_doenca VARCHAR(1),
    tempo_doenca VARCHAR(2),
    longa_permanencia VARCHAR(1),
    motivo_encerramento VARCHAR(100),
    tipo_alta VARCHAR(1),
    data_alta DATE,

    -- Campos de controle da aplicação
    tp_status VARCHAR(1) DEFAULT 'A',  -- A=Aguardando, P=Processando, E=Enviado, R=Rejeitado
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Índices
    CONSTRAINT uk_inovemed_tbl_guias_numero_guia UNIQUE (numero_guia)
);

-- Índices para performance
CREATE INDEX idx_inovemed_tbl_guias_tp_status ON inovemed_tbl_guias(tp_status);
CREATE INDEX idx_inovemed_tbl_guias_data_criacao ON inovemed_tbl_guias(data_criacao);
CREATE INDEX idx_inovemed_tbl_guias_numero_guia ON inovemed_tbl_guias(numero_guia);
```

### **2. Tabela de Anexos: `inovemed_tbl_guias_anexos`**

```sql
CREATE TABLE inovemed_tbl_guias_anexos (
    id SERIAL PRIMARY KEY,
    guia_id INTEGER NOT NULL,
    tipo_anexo VARCHAR(50),
    nome_arquivo VARCHAR(255),
    conteudo_arquivo TEXT,  -- Base64 ou caminho do arquivo
    tamanho_arquivo INTEGER,
    data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Chave estrangeira
    CONSTRAINT fk_inovemed_tbl_guias_anexos_guia
        FOREIGN KEY (guia_id)
        REFERENCES inovemed_tbl_guias(id)
        ON DELETE CASCADE,

    -- Índices
    CONSTRAINT uk_inovemed_tbl_guias_anexos_guia_tipo
        UNIQUE (guia_id, tipo_anexo)
);

CREATE INDEX idx_inovemed_tbl_guias_anexos_guia_id ON inovemed_tbl_guias_anexos(guia_id);
```

### **3. Tabela de Procedimentos: `inovemed_tbl_guias_procedimentos`**

```sql
CREATE TABLE inovemed_tbl_guias_procedimentos (
    id SERIAL PRIMARY KEY,
    guia_id INTEGER NOT NULL,
    codigo_procedimento VARCHAR(20) NOT NULL,
    descricao_procedimento VARCHAR(255),
    quantidade INTEGER DEFAULT 1,
    valor_unitario DECIMAL(10,2),
    valor_total DECIMAL(10,2),
    data_procedimento DATE,

    -- Chave estrangeira
    CONSTRAINT fk_inovemed_tbl_guias_procedimentos_guia
        FOREIGN KEY (guia_id)
        REFERENCES inovemed_tbl_guias(id)
        ON DELETE CASCADE,

    -- Índices
    CONSTRAINT uk_inovemed_tbl_guias_procedimentos_guia_codigo
        UNIQUE (guia_id, codigo_procedimento)
);

CREATE INDEX idx_inovemed_tbl_guias_procedimentos_guia_id ON inovemed_tbl_guias_procedimentos(guia_id);
CREATE INDEX idx_inovemed_tbl_guias_procedimentos_codigo ON inovemed_tbl_guias_procedimentos(codigo_procedimento);
```

### **4. Tabela de Diagnósticos: `inovemed_tbl_guias_diagnosticos`**

```sql
CREATE TABLE inovemed_tbl_guias_diagnosticos (
    id SERIAL PRIMARY KEY,
    guia_id INTEGER NOT NULL,
    codigo_diagnostico VARCHAR(20) NOT NULL,
    descricao_diagnostico VARCHAR(255),
    tipo_diagnostico VARCHAR(1),  -- P=Principal, S=Secundário
    data_diagnostico DATE,

    -- Chave estrangeira
    CONSTRAINT fk_inovemed_tbl_guias_diagnosticos_guia
        FOREIGN KEY (guia_id)
        REFERENCES inovemed_tbl_guias(id)
        ON DELETE CASCADE,

    -- Índices
    CONSTRAINT uk_inovemed_tbl_guias_diagnosticos_guia_codigo_tipo
        UNIQUE (guia_id, codigo_diagnostico, tipo_diagnostico)
);

CREATE INDEX idx_inovemed_tbl_guias_diagnosticos_guia_id ON inovemed_tbl_guias_diagnosticos(guia_id);
CREATE INDEX idx_inovemed_tbl_guias_diagnosticos_codigo ON inovemed_tbl_guias_diagnosticos(codigo_diagnostico);
```

## 🔄 **Como Funciona o Processamento**

### **Fluxo de Dados:**

1. **Inserção de Dados**: Uma procedure externa insere dados na `inovemed_tbl_guias` com `tp_status = 'A'`
2. **Monitoramento**: A aplicação monitora automaticamente a tabela a cada X minutos
3. **Processamento**: Quando encontra guias com `tp_status = 'A'`, processa até 10 por vez
4. **Envio**: Envia para a API DRG e atualiza o `tp_status` para 'E' (Enviado) ou 'R' (Rejeitado)

### **Estados do Campo `tp_status`:**

- **'A'** = Aguardando processamento (padrão)
- **'P'** = Processando (em andamento)
- **'E'** = Enviado com sucesso
- **'R'** = Rejeitado/Falha no envio

## 📝 **Exemplo de Procedure para Inserir Dados**

```sql
-- Procedure para inserir uma guia completa
CREATE OR REPLACE FUNCTION inserir_guia_completa(
    p_numero_guia VARCHAR(50),
    p_numero_guia_operadora VARCHAR(50),
    p_nome_prestador VARCHAR(255),
    p_nome_profissional VARCHAR(255),
    p_codigo_procedimento VARCHAR(20),
    p_descricao_procedimento VARCHAR(255),
    p_codigo_diagnostico VARCHAR(20),
    p_descricao_diagnostico VARCHAR(255)
) RETURNS INTEGER AS $$
DECLARE
    v_guia_id INTEGER;
BEGIN
    -- 1. Inserir guia principal
    INSERT INTO inovemed_tbl_guias (
        numero_guia,
        numero_guia_operadora,
        nome_prestador,
        nome_profissional,
        data_autorizacao,
        data_validade,
        tp_status  -- Importante: deve ser 'A' para ser processada
    ) VALUES (
        p_numero_guia,
        p_numero_guia_operadora,
        p_nome_prestador,
        p_nome_profissional,
        CURRENT_DATE,
        CURRENT_DATE + INTERVAL '30 days',
        'A'  -- Status 'A' = Aguardando processamento
    ) RETURNING id INTO v_guia_id;

    -- 2. Inserir procedimento (se fornecido)
    IF p_codigo_procedimento IS NOT NULL THEN
        INSERT INTO inovemed_tbl_guias_procedimentos (
            guia_id,
            codigo_procedimento,
            descricao_procedimento,
            quantidade
        ) VALUES (
            v_guia_id,
            p_codigo_procedimento,
            p_descricao_procedimento,
            1
        );
    END IF;

    -- 3. Inserir diagnóstico (se fornecido)
    IF p_codigo_diagnostico IS NOT NULL THEN
        INSERT INTO inovemed_tbl_guias_diagnosticos (
            guia_id,
            codigo_diagnostico,
            descricao_diagnostico,
            tipo_diagnostico
        ) VALUES (
            v_guia_id,
            p_codigo_diagnostico,
            p_descricao_diagnostico,
            'P'  -- P = Principal
        );
    END IF;

    -- 4. Retornar ID da guia criada
    RETURN v_guia_id;

EXCEPTION
    WHEN OTHERS THEN
        -- Em caso de erro, fazer rollback
        RAISE EXCEPTION 'Erro ao inserir guia: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- Exemplo de uso da procedure:
SELECT inserir_guia_completa(
    'GUI001234567',
    'OP001234567',
    'HOSPITAL EXEMPLO LTDA',
    'DR. JOÃO SILVA',
    '03100101',  -- Código do procedimento
    'CONSULTA MÉDICA',
    'Z00.0',     -- Código do diagnóstico
    'EXAME GERAL'
);
```

## 🔍 **Queries Úteis para Monitoramento**

### **Verificar Guias Aguardando Processamento:**

```sql
SELECT
    id,
    numero_guia,
    nome_prestador,
    data_criacao,
    tp_status
FROM inovemed_tbl_guias
WHERE tp_status = 'A'
ORDER BY data_criacao ASC
LIMIT 10;
```

### **Verificar Guias Processadas Hoje:**

```sql
SELECT
    id,
    numero_guia,
    tp_status,
    data_atualizacao
FROM inovemed_tbl_guias
WHERE DATE(data_atualizacao) = CURRENT_DATE
    AND tp_status IN ('E', 'R')
ORDER BY data_atualizacao DESC;
```

### **Estatísticas por Status:**

```sql
SELECT
    tp_status,
    COUNT(*) as quantidade,
    MIN(data_criacao) as primeira_guia,
    MAX(data_criacao) as ultima_guia
FROM inovemed_tbl_guias
GROUP BY tp_status
ORDER BY tp_status;
```

### **Verificar Relacionamentos:**

```sql
-- Guias com procedimentos
SELECT
    g.id,
    g.numero_guia,
    COUNT(p.id) as total_procedimentos
FROM inovemed_tbl_guias g
LEFT JOIN inovemed_tbl_guias_procedimentos p ON g.id = p.guia_id
GROUP BY g.id, g.numero_guia
HAVING COUNT(p.id) > 0;

-- Guias com diagnósticos
SELECT
    g.id,
    g.numero_guia,
    COUNT(d.id) as total_diagnosticos
FROM inovemed_tbl_guias g
LEFT JOIN inovemed_tbl_guias_diagnosticos d ON g.id = d.guia_id
GROUP BY g.id, g.numero_guia
HAVING COUNT(d.id) > 0;
```

## ⚠️ **Importante**

### **Para o Sistema Funcionar Corretamente:**

1. **Campo `tp_status`**: Sempre inserir com valor `'A'` (Aguardando)
2. **Relacionamentos**: Usar o `id` retornado da tabela principal para inserir nas tabelas relacionadas
3. **Índices**: Manter os índices para performance do monitoramento
4. **Constraints**: Respeitar as chaves estrangeiras e constraints de unicidade

### **Campos Obrigatórios na Tabela Principal:**

- `numero_guia` (único)
- `tp_status = 'A'` (para ser processada)
- `data_criacao` (automático)

### **Monitoramento Automático:**

A aplicação monitora a tabela `inovemed_tbl_guias` automaticamente e:

- Busca guias com `tp_status = 'A'`
- Processa até 10 guias por vez
- Atualiza o `tp_status` após processamento
- Registra logs detalhados de todo o processo
