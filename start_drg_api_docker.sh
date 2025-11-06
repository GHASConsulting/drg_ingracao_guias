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

# Cria diretório logs se não existir
if [ ! -d "logs" ]; then
  echo "📁 Criando diretorio logs..."
  mkdir -p logs
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
  echo ""
  echo "💡 Para iniciar o Docker:"
  echo ""
  
  # Detecta o sistema operacional
  if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]] || [[ -n "$WINDIR" ]]; then
    echo "   Windows:"
    echo "   1. Abra o Docker Desktop"
    echo "   2. Aguarde o Docker iniciar completamente"
    echo "   3. Execute este script novamente"
    echo ""
    echo "   Ou inicie manualmente:"
    echo "   - Procure por 'Docker Desktop' no menu Iniciar"
    echo "   - Ou execute: start 'C:\Program Files\Docker\Docker\Docker Desktop.exe'"
  elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "   macOS:"
    echo "   1. Abra o Docker Desktop"
    echo "   2. Aguarde o Docker iniciar completamente"
    echo "   3. Execute este script novamente"
    echo ""
    echo "   Ou inicie manualmente:"
    echo "   open -a Docker"
  else
    echo "   Linux:"
    echo "   1. Inicie o serviço Docker:"
    echo "      sudo systemctl start docker"
    echo ""
    echo "   2. Ou se usar Docker Desktop:"
    echo "      systemctl --user start docker-desktop"
    echo ""
    echo "   3. Execute este script novamente"
  fi
  
  echo ""
  echo "   Verifique se o Docker está rodando com:"
  echo "   docker ps"
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
  echo
  echo "❌ Erro ao iniciar Docker!"
  echo
  echo "💡 Possiveis solucoes:"
  echo
  echo "   1. COMPARTILHAMENTO DE DIRETORIO (Windows):"
  echo "      - Abra o Docker Desktop"
  echo "      - Vá em Settings > Resources > File Sharing"
  echo "      - Adicione o diretorio: C:\\DRG-INOVEMED"
  echo "      - Ou aceite o prompt que aparecer"
  echo
  echo "   2. Verifique se o diretorio logs existe e tem permissao"
  echo
  echo "   3. No Linux, verifique permissoes do diretorio:"
  echo "      sudo chown -R \$USER:\$USER logs/"
  echo
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

