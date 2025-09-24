#!/usr/bin/env python3
"""
Script para testar a integração com DRG e visualizar logs detalhados
"""

import os
import sys
import time
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.database import init_db, get_session
from app.models import Guia
from app.services.drg_service import DRGService
from app.services.guia_service import GuiaService
from app.config.config import get_settings


def testar_autenticacao_drg():
    """Testa apenas a autenticação com DRG"""
    print("🔐 TESTANDO AUTENTICAÇÃO DRG")
    print("=" * 50)

    drg_service = DRGService()
    resultado = drg_service.autenticar()

    if resultado.get("sucesso"):
        print("✅ Autenticação bem-sucedida!")
        print(f"🔑 Token obtido: {resultado.get('token', 'N/A')[:20]}...")
    else:
        print("❌ Falha na autenticação!")
        print(f"🚨 Erro: {resultado.get('erro', 'Erro desconhecido')}")

    return resultado.get("sucesso", False)


def testar_envio_guia():
    """Testa o envio de uma guia para DRG"""
    print("\n📋 TESTANDO ENVIO DE GUIA")
    print("=" * 50)

    try:
        # Inicializar banco
        init_db()
        session = get_session()

        # Buscar uma guia para teste
        guia = session.query(Guia).filter(Guia.tp_status == "A").first()

        if not guia:
            print("❌ Nenhuma guia aguardando encontrada!")
            print("💡 Execute 'python adicionar_guias.py' para criar dados de teste")
            return False

        print(f"📋 Testando com guia: {guia.numero_guia} (ID: {guia.id})")

        # Serviços
        drg_service = DRGService()
        guia_service = GuiaService()

        # Processar guia completa
        resultado = guia_service.processar_guia_completa(guia, drg_service)

        if resultado.get("sucesso"):
            print("✅ Guia enviada com sucesso!")
            print(f"📥 Resposta: {resultado.get('resposta', 'N/A')}")
        else:
            print("❌ Falha no envio da guia!")
            print(f"🚨 Erro: {resultado.get('erro', 'Erro desconhecido')}")

        session.close()
        return resultado.get("sucesso", False)

    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False


def visualizar_logs():
    """Visualiza os logs mais recentes"""
    print("\n📄 VISUALIZANDO LOGS")
    print("=" * 50)

    settings = get_settings()
    log_file = settings.LOG_FILE

    if not os.path.exists(log_file):
        print("❌ Arquivo de log não encontrado!")
        return

    print(f"📁 Arquivo de log: {log_file}")
    print("-" * 50)

    try:
        # Ler últimas 50 linhas do log
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            recent_lines = lines[-50:] if len(lines) > 50 else lines

            for line in recent_lines:
                print(line.rstrip())

    except Exception as e:
        print(f"❌ Erro ao ler logs: {e}")


def monitorar_logs_tempo_real():
    """Monitora logs em tempo real"""
    print("\n👁️ MONITORAMENTO EM TEMPO REAL")
    print("=" * 50)
    print("Pressione Ctrl+C para parar")
    print("-" * 50)

    settings = get_settings()
    log_file = settings.LOG_FILE

    if not os.path.exists(log_file):
        print("❌ Arquivo de log não encontrado!")
        return

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            # Ir para o final do arquivo
            f.seek(0, 2)

            while True:
                line = f.readline()
                if line:
                    print(line.rstrip())
                else:
                    time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n👋 Monitoramento interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro no monitoramento: {e}")


def main():
    """Menu principal"""
    print("🧪 TESTADOR DE INTEGRAÇÃO DRG COM LOGS")
    print("=" * 60)
    print("1. Testar apenas autenticação")
    print("2. Testar envio de guia completa")
    print("3. Visualizar logs recentes")
    print("4. Monitorar logs em tempo real")
    print("5. Teste completo (autenticação + envio + logs)")
    print("6. Sair")

    try:
        opcao = input("\nEscolha uma opção (1-6): ").strip()

        if opcao == "1":
            testar_autenticacao_drg()
        elif opcao == "2":
            testar_envio_guia()
        elif opcao == "3":
            visualizar_logs()
        elif opcao == "4":
            monitorar_logs_tempo_real()
        elif opcao == "5":
            print("\n🚀 TESTE COMPLETO")
            print("=" * 30)

            # Testar autenticação
            if testar_autenticacao_drg():
                print("\n" + "=" * 50)
                # Testar envio
                testar_envio_guia()
                print("\n" + "=" * 50)
                # Mostrar logs
                visualizar_logs()
            else:
                print("❌ Falha na autenticação, pulando envio de guia")

        elif opcao == "6":
            print("👋 Até logo!")
        else:
            print("❌ Opção inválida!")

    except KeyboardInterrupt:
        print("\n👋 Operação cancelada pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    main()


