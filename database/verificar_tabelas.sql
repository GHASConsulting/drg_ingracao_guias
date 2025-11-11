-- Script SQL para verificar tabelas no Oracle
-- Execute este script diretamente no Oracle SQL Developer ou SQL*Plus

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

-- Verificar estrutura da tabela principal
SELECT 
    column_name,
    data_type,
    data_length,
    nullable,
    data_default
FROM 
    user_tab_columns
WHERE 
    table_name = 'INOVEMED_TBL_GUIAS'
ORDER BY 
    column_id;

-- Contar registros em cada tabela
SELECT 'INOVEMED_TBL_GUIAS' AS tabela, COUNT(*) AS total FROM INOVEMED_TBL_GUIAS
UNION ALL
SELECT 'INOVEMED_TBL_ANEXOS', COUNT(*) FROM INOVEMED_TBL_ANEXOS
UNION ALL
SELECT 'INOVEMED_TBL_PROCEDIMENTOS', COUNT(*) FROM INOVEMED_TBL_PROCEDIMENTOS
UNION ALL
SELECT 'INOVEMED_TBL_DIAGNOSTICOS', COUNT(*) FROM INOVEMED_TBL_DIAGNOSTICOS;

-- Verificar constraints (chaves primárias e estrangeiras)
SELECT 
    constraint_name,
    constraint_type,
    table_name
FROM 
    user_constraints
WHERE 
    table_name IN (
        'INOVEMED_TBL_GUIAS',
        'INOVEMED_TBL_ANEXOS',
        'INOVEMED_TBL_PROCEDIMENTOS',
        'INOVEMED_TBL_DIAGNOSTICOS'
    )
ORDER BY 
    table_name, constraint_type;

