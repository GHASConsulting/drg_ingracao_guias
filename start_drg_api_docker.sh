#!/usr/bin/env bash
echo "========================================================="
echo "  INICIANDO DRG-GUIAS COM DOCKER (PRODUCAO)"
echo "========================================================="

# Verifica se existe arquivo .env
if [ ! -f ".env" ]; then
  echo "⚠️  Arquivo .env nao encontrado!"
  echo "Por favor, copie env.example para .env e configure"
  exit 1
fi

# Verifica se Docker está instalado
if ! command -v docker &> /dev/null; then
  echo "❌ Docker nao encontrado!"
  echo "Por favor, instale o Docker"
  exit 1
fi

# Verifica se Docker está rodando
if ! docker ps &> /dev/null; then
  echo "❌ Docker nao esta rodando!"
  echo "Por favor, inicie o Docker"
  exit 1
fi

echo "✅ Docker encontrado e rodando"
echo

# Verifica se docker-compose está disponível
if command -v docker-compose &> /dev/null; then
  DOCKER_COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
  DOCKER_COMPOSE_CMD="docker compose"
else
  echo "❌ docker-compose nao encontrado!"
  exit 1
fi

echo "🐳 Parando containers existentes (se houver)..."
$DOCKER_COMPOSE_CMD --profile production down

echo
echo "🐳 Construindo e iniciando container Docker..."
$DOCKER_COMPOSE_CMD --profile production up --build -d

if [ $? -ne 0 ]; then
  echo "❌ Erro ao iniciar Docker!"
  exit 1
fi

echo
echo "✅ Container iniciado com sucesso!"
echo
echo "📊 Para ver os logs, execute:"
echo "   $DOCKER_COMPOSE_CMD --profile production logs -f drg-api"
echo
echo "🛑 Para parar o container, execute:"
echo "   $DOCKER_COMPOSE_CMD --profile production down"
echo
echo "🌐 Aplicacao disponivel em: http://localhost:8001/docs"
echo

# Mostra logs iniciais
echo "📋 Logs iniciais (aguarde alguns segundos...)"
sleep 3
$DOCKER_COMPOSE_CMD --profile production logs --tail=20 drg-api

