#!/usr/bin/env python3
"""
Script para testar a API DRG
"""

import requests
import json
from datetime import datetime

# URL base da API
BASE_URL = "http://localhost:8000/api/v1"


def testar_endpoint(endpoint, method="GET", data=None):
    """Testa um endpoint da API."""
    url = f"{BASE_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)

        print(f"\n{'='*60}")
        print(f"🔗 {method} {endpoint}")
        print(f"📊 Status: {response.status_code}")

        if response.headers.get("content-type", "").startswith("application/json"):
            result = response.json()
            print(f"📋 Resposta: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"📋 Resposta: {response.text}")

        return response.status_code == 200

    except requests.exceptions.ConnectionError:
        print(f"\n❌ Erro: Não foi possível conectar ao servidor")
        print(f"💡 Certifique-se de que o Flask está rodando em http://localhost:5000")
        return False
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return False


def main():
    """Executa todos os testes da API."""
    print("🧪 TESTANDO API DRG")
    print("=" * 60)

    # Lista de endpoints para testar
    endpoints = [
        # Health check
        ("/health", "GET"),
        # Status do sistema
        ("/status", "GET"),
        # Listar guias
        ("/guias", "GET"),
        ("/guias?status=A", "GET"),
        ("/guias?limit=2", "GET"),
        # Consultar guia específica
        ("/guias/1", "GET"),
        # Status do token DRG
        ("/drg/token", "GET"),
        # Monitoramento
        ("/monitoramento", "GET"),
    ]

    resultados = []

    for endpoint, method in endpoints:
        sucesso = testar_endpoint(endpoint, method)
        resultados.append((endpoint, sucesso))

    # Resumo dos resultados
    print(f"\n{'='*60}")
    print("📊 RESUMO DOS TESTES:")
    print(f"{'='*60}")

    sucessos = 0
    for endpoint, sucesso in resultados:
        status = "✅ OK" if sucesso else "❌ FALHOU"
        print(f"{status} {endpoint}")
        if sucesso:
            sucessos += 1

    print(f"\n🎯 Resultado: {sucessos}/{len(resultados)} testes passaram")

    if sucessos == len(resultados):
        print("🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("⚠️  Alguns testes falharam!")
        print("💡 Verifique se o FastAPI está rodando em http://localhost:8000")


if __name__ == "__main__":
    main()
