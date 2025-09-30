-- Script para adicionar campo nome_beneficiario na tabela Oracle
ALTER TABLE inovemed_tbl_guias ADD nome_beneficiario VARCHAR2(100) NOT NULL;

-- Atualizar dados existentes com nome do beneficiário
UPDATE inovemed_tbl_guias 
SET nome_beneficiario = 'João Silva Santos'
WHERE numero_guia = 'GUI002';

-- Resetar status para processar novamente
UPDATE inovemed_tbl_guias 
SET 
    tp_status = 'A',
    data_processamento = NULL,
    mensagem_erro = NULL,
    tentativas = 0
WHERE numero_guia = 'GUI002';

COMMIT;
