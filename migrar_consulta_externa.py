#!/usr/bin/env python3
"""
Script de migração para adicionar novos campos de consulta externa
"""

import sqlite3
import sys
from pathlib import Path


def migrar_banco_sqlite():
    """Migra banco SQLite adicionando novos campos"""
    db_path = Path("database/teste_drg.db")

    if not db_path.exists():
        print("❌ Banco SQLite não encontrado!")
        return False

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        print("🔄 Iniciando migração do banco SQLite...")

        # Verificar se os campos já existem
        cursor.execute("PRAGMA table_info(inovemed_tbl_guias)")
        colunas = [coluna[1] for coluna in cursor.fetchall()]

        campos_novos = [
            "status_consulta",
            "data_ultima_consulta",
            "dados_retornados",
            "senha_autorizacao",
            "status_monitoramento",
        ]

        campos_para_adicionar = [
            campo for campo in campos_novos if campo not in colunas
        ]

        if not campos_para_adicionar:
            print("✅ Todos os campos já existem no banco!")
            return True

        # Adicionar novos campos
        for campo in campos_para_adicionar:
            if campo == "status_consulta":
                sql = "ALTER TABLE inovemed_tbl_guias ADD COLUMN status_consulta VARCHAR(1) DEFAULT 'P'"
            elif campo == "data_ultima_consulta":
                sql = "ALTER TABLE inovemed_tbl_guias ADD COLUMN data_ultima_consulta DATETIME"
            elif campo == "dados_retornados":
                sql = "ALTER TABLE inovemed_tbl_guias ADD COLUMN dados_retornados TEXT"
            elif campo == "senha_autorizacao":
                sql = "ALTER TABLE inovemed_tbl_guias ADD COLUMN senha_autorizacao VARCHAR(20)"
            elif campo == "status_monitoramento":
                sql = "ALTER TABLE inovemed_tbl_guias ADD COLUMN status_monitoramento VARCHAR(1) DEFAULT 'N'"

            cursor.execute(sql)
            print(f"✅ Campo '{campo}' adicionado com sucesso!")

        conn.commit()
        print("✅ Migração do SQLite concluída com sucesso!")
        return True

    except Exception as e:
        print(f"❌ Erro na migração SQLite: {e}")
        return False
    finally:
        if "conn" in locals():
            conn.close()


def gerar_script_oracle():
    """Gera script SQL para Oracle"""
    script_oracle = """
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
"""

    with open("migracao_oracle_consulta_externa.sql", "w", encoding="utf-8") as f:
        f.write(script_oracle)

    print("✅ Script Oracle gerado: migracao_oracle_consulta_externa.sql")


def main():
    """Função principal"""
    print("🚀 Iniciando migração para campos de consulta externa...")

    # Migrar SQLite
    if migrar_banco_sqlite():
        print("✅ Migração SQLite concluída!")

    # Gerar script Oracle
    gerar_script_oracle()

    print("\n📋 RESUMO DA MIGRAÇÃO:")
    print("✅ Campos adicionados:")
    print("   - status_consulta (VARCHAR(1), default 'P')")
    print("   - data_ultima_consulta (DATETIME)")
    print("   - dados_retornados (TEXT/CLOB)")
    print("   - senha_autorizacao (VARCHAR(20))")
    print("   - status_monitoramento (VARCHAR(1), default 'N')")
    print("\n📁 Arquivos gerados:")
    print("   - migracao_oracle_consulta_externa.sql")
    print("\n🎯 Próximos passos:")
    print("   1. Execute o script Oracle no banco de produção")
    print("   2. Reinicie a aplicação para carregar os novos campos")
    print("   3. Teste as novas rotas de consulta externa")


if __name__ == "__main__":
    main()
