@echo off
echo ========================================================
echo   INICIANDO DRG-GUIAS COM DOCKER (PRODUCAO)
echo ========================================================

:: Verifica se existe arquivo .env
if not exist ".env" (
    echo ⚠️  Arquivo .env nao encontrado!
    echo Por favor, copie env.example para .env e configure
    pause
    exit /b 1
)

:: Verifica se Docker está instalado e rodando
docker --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Docker nao encontrado!
    echo Por favor, instale o Docker Desktop
    pause
    exit /b 1
)

:: Verifica se Docker está rodando
docker ps >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ Docker nao esta rodando!
    echo Por favor, inicie o Docker Desktop
    pause
    exit /b 1
)

echo ✅ Docker encontrado e rodando
echo.

:: Verifica se docker-compose está disponível
docker-compose --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ⚠️  docker-compose nao encontrado, tentando docker compose...
    set DOCKER_COMPOSE_CMD=docker compose
) else (
    set DOCKER_COMPOSE_CMD=docker-compose
)

echo.
echo 🐳 Parando containers existentes (se houver)...
%DOCKER_COMPOSE_CMD% --profile production down

echo.
echo 🐳 Construindo e iniciando container Docker...
%DOCKER_COMPOSE_CMD% --profile production up --build -d

if %ERRORLEVEL% neq 0 (
    echo ❌ Erro ao iniciar Docker!
    pause
    exit /b 1
)

echo.
echo ✅ Container iniciado com sucesso!
echo.
echo 📊 Para ver os logs, execute:
echo    %DOCKER_COMPOSE_CMD% --profile production logs -f drg-api
echo.
echo 🛑 Para parar o container, execute:
echo    %DOCKER_COMPOSE_CMD% --profile production down
echo.
echo 🌐 Aplicacao disponivel em: http://localhost:8001/docs
echo.

:: Mostra logs iniciais
echo 📋 Logs iniciais (aguarde alguns segundos...):
timeout /t 3 /nobreak >nul
%DOCKER_COMPOSE_CMD% --profile production logs --tail=20 drg-api

pause

