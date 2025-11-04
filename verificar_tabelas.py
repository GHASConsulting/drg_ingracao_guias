#!/usr/bin/env python3
"""
Script para verificar se as tabelas foram criadas corretamente no banco de dados Oracle
verificar se as tabelas foram criadas corretamente no banco de dados Oracle
"""

import sys
import os
from sqlalchemy import inspect, text
from app.database.database import init_db, SessionLocal
from app.models import Guia, Anexo, Procedimento, Diagnostico
from app.config.config import get_settings


def verificar_tabelas():
    """Verifica se todas as tabelas foram criadas corretamente"""

    print("=" * 60)
    print("  VERIFICAÇÃO DE TABELAS NO BANCO DE DADOS")
    print("=" * 60)
    print()

    # Configurar NLS_LANG antes de conectar ao Oracle (resolve ORA-01804)
    settings = get_settings()
    if settings.DATABASE_TYPE == "oracle":
        # Configurar NLS_LANG para evitar erro ORA-01804
        os.environ["NLS_LANG"] = "AMERICAN_AMERICA.AL32UTF8"

        # Configurar PATH do Oracle Instant Client se necessário
        oracle_dir = "/c/instantclient_21_13"
        if os.path.exists(oracle_dir):
            current_path = os.environ.get("PATH", "")
            if oracle_dir not in current_path:
                os.environ["PATH"] = f"{oracle_dir}{os.pathsep}{current_path}"

        print(f"🔧 NLS_LANG configurado: {os.environ.get('NLS_LANG')}")
        print()

    # Mostrar informações de configuração
    print(f"📊 Tipo de banco: {settings.DATABASE_TYPE}")
    if settings.DATABASE_TYPE == "oracle":
        print(f"📊 Host: {settings.ORACLE_HOST}:{settings.ORACLE_PORT}")
        print(f"📊 SID: {settings.ORACLE_SID}")
    print()

    # Inicializar banco (agora com NLS_LANG configurado)
    try:
        print("🔧 Inicializando conexão com o banco...")
        init_db()
        print("✅ Conexão estabelecida!")
        print()
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        print("\n💡 Dica: Verifique se:")
        print("   - Oracle Instant Client está instalado em /c/instantclient_21_13")
        print("   - NLS_LANG está configurado corretamente")
        print("   - Credenciais no .env estão corretas")
        print("   - Servidor Oracle está acessível")
        raise

    # Importar engine novamente após init_db() para obter referência atualizada
    import app.database.database as db_module

    engine = db_module.engine

    # Verificar se engine foi inicializado
    if engine is None:
        print("❌ Erro: Engine do banco não foi inicializado!")
        print("   Verifique se init_db() foi executado corretamente.")
        return False

    # Verificar tabelas usando inspector
    try:
        inspector = inspect(engine)
    except Exception as e:
        print(f"❌ Erro ao criar inspector: {e}")
        return False
    tabelas_existentes = inspector.get_table_names()

    print("=" * 60)
    print("  TABELAS ENCONTRADAS NO BANCO")
    print("=" * 60)

    tabelas_esperadas = [
        "inovemed_tbl_guias",
        "inovemed_tbl_anexos",
        "inovemed_tbl_procedimentos",
        "inovemed_tbl_diagnosticos",
    ]

    todas_ok = True

    for tabela in tabelas_esperadas:
        existe = tabela in tabelas_existentes
        status = "✅" if existe else "❌"
        print(f"{status} {tabela}")
        if not existe:
            todas_ok = False

    print()
    print("=" * 60)
    print("  DETALHES DAS TABELAS")
    print("=" * 60)

    # Verificar estrutura da tabela principal
    if "inovemed_tbl_guias" in tabelas_existentes:
        print("\n📋 Estrutura da tabela: inovemed_tbl_guias")
        print("-" * 60)

        colunas = inspector.get_columns("inovemed_tbl_guias")
        print(f"Total de colunas: {len(colunas)}")
        print()

        # Mostrar algumas colunas importantes
        colunas_importantes = [
            "id",
            "numero_guia",
            "tp_status",
            "situacao_guia",
            "data_criacao",
            "data_atualizacao",
            "data_processamento",
            "senha_autorizacao",
            "status_monitoramento",
        ]

        print("Colunas principais:")
        for col in colunas:
            if col["name"] in colunas_importantes:
                tipo = str(col["type"])
                nullable = "NULL" if col["nullable"] else "NOT NULL"
                print(f"  - {col['name']:<30} {tipo:<20} {nullable}")

        print()

        # Contar registros
        session = SessionLocal()
        try:
            count = session.query(Guia).count()
            print(f"📊 Total de registros na tabela: {count}")

            # Estatísticas por status
            if count > 0:
                print("\n📊 Estatísticas por status:")
                status_counts = (
                    session.query(Guia.tp_status, text("COUNT(*)"))
                    .group_by(Guia.tp_status)
                    .all()
                )

                for status, count_status in status_counts:
                    print(f"  - Status '{status}': {count_status} guias")
        finally:
            session.close()

    # Verificar outras tabelas relacionadas
    tabelas_relacionadas = {
        "inovemed_tbl_anexos": "Anexos",
        "inovemed_tbl_procedimentos": "Procedimentos",
        "inovemed_tbl_diagnosticos": "Diagnósticos",
    }

    for tabela, nome in tabelas_relacionadas.items():
        if tabela in tabelas_existentes:
            session = SessionLocal()
            try:
                # Usar text() para executar SQL direto
                result = session.execute(text(f"SELECT COUNT(*) FROM {tabela}"))
                count = result.scalar()
                print(f"\n📊 {nome}: {count} registros")
            except Exception as e:
                print(f"\n⚠️  Erro ao contar registros em {tabela}: {e}")
            finally:
                session.close()

    print()
    print("=" * 60)
    print("  RESUMO")
    print("=" * 60)

    if todas_ok:
        print("✅ Todas as tabelas foram criadas corretamente!")
        print("✅ O banco de dados está pronto para uso!")
    else:
        print("❌ Algumas tabelas não foram encontradas!")
        print("   Execute as migrações ou crie as tabelas manualmente.")
        print()
        print("   Para criar as tabelas, execute:")
        print("   python -c 'from app.database.database import init_db; init_db()'")

    print()

    return todas_ok


if __name__ == "__main__":
    try:
        sucesso = verificar_tabelas()
        sys.exit(0 if sucesso else 1)
    except Exception as e:
        print(f"\n❌ Erro ao verificar tabelas: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
