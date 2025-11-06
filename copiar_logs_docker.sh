#!/usr/bin/env bash
echo "========================================================="
echo "  COPIANDO LOGS DO CONTAINER DOCKER"
echo "========================================================="

# Verifica se container está rodando
if ! docker ps --format "{{.Names}}" | grep -q "drg-api"; then
  echo "❌ Container drg-api nao esta rodando!"
  echo "   Execute: ./start_drg_api_docker.sh"
  exit 1
fi

# Cria diretório logs local se não existir
if [ ! -d "logs" ]; then
  echo "📁 Criando diretorio logs..."
  mkdir -p logs
fi

echo "📋 Copiando logs do container..."
docker cp drg-api:/app/logs/. ./logs/

if [ $? -eq 0 ]; then
  echo "✅ Logs copiados com sucesso!"
  echo
  echo "📁 Logs disponiveis em: $(pwd)/logs"
  echo
  echo "Para ver os logs:"
  echo "   tail -f logs/drg_guias.log"
else
  echo "⚠️  Nao foi possivel copiar todos os logs"
  echo "   Tentando copiar arquivo especifico..."
  docker cp drg-api:/app/logs/drg_guias.log ./logs/drg_guias.log 2>/dev/null
  docker cp drg-api:/app/logs/security.log ./logs/security.log 2>/dev/null
  echo "✅ Logs principais copiados!"
fi

echo

