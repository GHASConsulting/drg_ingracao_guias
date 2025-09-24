#!/usr/bin/env python3
"""
Script para testar o sistema de monitoramento automático
"""

import requests
import time
import json
from datetime import datetime


def testar_status_monitoramento():
    """Testa o endpoint de status do monitoramento"""
    print("🔍 TESTANDO STATUS DO MONITORAMENTO")
    print("=" * 50)

    try:
        response = requests.get("http://localhost:8000/api/v1/monitoramento/status")

        if response.status_code == 200:
            data = response.json()
            print("✅ Status obtido com sucesso!")
            print(f"📊 Dados: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"📄 Resposta: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False


def testar_controle_monitoramento():
    """Testa os endpoints de controle do monitoramento"""
    print("\n🎛️ TESTANDO CONTROLE DO MONITORAMENTO")
    print("=" * 50)

    # Testar parar monitoramento
    print("🛑 Parando monitoramento...")
    try:
        response = requests.post("http://localhost:8000/api/v1/monitoramento/stop")
        if response.status_code == 200:
            print("✅ Monitoramento parado com sucesso!")
        else:
            print(f"⚠️ Resposta inesperada: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao parar: {e}")

    time.sleep(2)

    # Testar iniciar monitoramento
    print("🚀 Iniciando monitoramento...")
    try:
        response = requests.post("http://localhost:8000/api/v1/monitoramento/start")
        if response.status_code == 200:
            print("✅ Monitoramento iniciado com sucesso!")
        else:
            print(f"⚠️ Resposta inesperada: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao iniciar: {e}")


def monitorar_em_tempo_real():
    """Monitora o status em tempo real"""
    print("\n👁️ MONITORAMENTO EM TEMPO REAL")
    print("=" * 50)
    print("Pressione Ctrl+C para parar")
    print("-" * 50)

    try:
        while True:
            try:
                response = requests.get(
                    "http://localhost:8000/api/v1/monitoramento/status"
                )

                if response.status_code == 200:
                    data = response.json()
                    status = data.get("data", {})

                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(
                        f"[{timestamp}] Monitor: {'✅ Ativo' if status.get('monitoramento_ativo') else '❌ Parado'} | "
                        f"Aguardando: {status.get('aguardando', 0)} | "
                        f"Processando: {status.get('processando', 0)} | "
                        f"Transmitidas: {status.get('transmitidas', 0)} | "
                        f"Erros: {status.get('com_erro', 0)}"
                    )
                else:
                    print(
                        f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Erro ao obter status"
                    )

            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Erro: {e}")

            time.sleep(10)  # Verificar a cada 10 segundos

    except KeyboardInterrupt:
        print("\n👋 Monitoramento interrompido pelo usuário")


def main():
    """Menu principal"""
    print("🤖 TESTADOR DE MONITORAMENTO AUTOMÁTICO")
    print("=" * 60)
    print("1. Ver status do monitoramento")
    print("2. Testar controle (parar/iniciar)")
    print("3. Monitorar em tempo real")
    print("4. Teste completo")
    print("5. Sair")

    try:
        opcao = input("\nEscolha uma opção (1-5): ").strip()

        if opcao == "1":
            testar_status_monitoramento()
        elif opcao == "2":
            testar_controle_monitoramento()
        elif opcao == "3":
            monitorar_em_tempo_real()
        elif opcao == "4":
            print("\n🚀 TESTE COMPLETO")
            print("=" * 30)
            testar_status_monitoramento()
            print("\n" + "=" * 50)
            testar_controle_monitoramento()
            print("\n" + "=" * 50)
            print("✅ Teste completo finalizado!")
        elif opcao == "5":
            print("👋 Até logo!")
        else:
            print("❌ Opção inválida!")

    except KeyboardInterrupt:
        print("\n👋 Operação cancelada pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")


if __name__ == "__main__":
    main()
