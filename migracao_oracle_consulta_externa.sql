
-- =============================================================================
-- SCRIPT DE MIGRAÇÃO ORACLE - CAMPOS DE CONSULTA EXTERNA
-- =============================================================================
-- Execute este script no Oracle para adicionar os novos campos

-- Adicionar campo status_consulta
ALTER TABLE inovemed_tbl_guias ADD status_consulta VARCHAR2(1) DEFAULT 'P' NOT NULL;
COMMENT ON COLUMN inovemed_tbl_guias.status_consulta IS 'Status da consulta externa: P=Pendente, C=Consultado, R=Retornado';

-- Adicionar campo data_ultima_consulta
ALTER TABLE inovemed_tbl_guias ADD data_ultima_consulta DATE;
COMMENT ON COLUMN inovemed_tbl_guias.data_ultima_consulta IS 'Data da última consulta externa realizada';

-- Adicionar campo dados_retornados
ALTER TABLE inovemed_tbl_guias ADD dados_retornados CLOB;
COMMENT ON COLUMN inovemed_tbl_guias.dados_retornados IS 'JSON com dados retornados da consulta externa';

-- Adicionar campo senha_autorizacao
ALTER TABLE inovemed_tbl_guias ADD senha_autorizacao VARCHAR2(20);
COMMENT ON COLUMN inovemed_tbl_guias.senha_autorizacao IS 'Senha de autorização retornada pela consulta externa';

-- Adicionar campo status_monitoramento
ALTER TABLE inovemed_tbl_guias ADD status_monitoramento VARCHAR2(1) DEFAULT 'N';
COMMENT ON COLUMN inovemed_tbl_guias.status_monitoramento IS 'Status do monitoramento: N=Não monitorando, M=Monitorando, F=Finalizado';

-- Criar índice para performance
CREATE INDEX idx_guias_status_consulta ON inovemed_tbl_guias(status_consulta);
CREATE INDEX idx_guias_data_consulta ON inovemed_tbl_guias(data_ultima_consulta);

-- Atualizar comentário da tabela
COMMENT ON TABLE inovemed_tbl_guias IS 'Tabela de guias de internação com suporte a consulta externa';

-- Verificar se os campos foram criados
SELECT column_name, data_type, data_length, nullable, data_default
FROM user_tab_columns 
WHERE table_name = 'INOVEMED_TBL_GUIAS' 
AND column_name IN ('STATUS_CONSULTA', 'DATA_ULTIMA_CONSULTA', 'DADOS_RETORNADOS', 'SENHA_AUTORIZACAO', 'STATUS_MONITORAMENTO')
ORDER BY column_name;

-- =============================================================================
-- FIM DO SCRIPT DE MIGRAÇÃO
-- =============================================================================
