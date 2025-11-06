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
    echo.
    echo 💡 Para iniciar o Docker Desktop:
    echo    1. Abra o Docker Desktop pelo menu Iniciar
    echo    2. Aguarde o Docker iniciar completamente ^(icone na bandeja^)
    echo    3. Execute este script novamente
    echo.
    echo    Ou tente iniciar automaticamente...
    
    :: Tenta iniciar o Docker Desktop automaticamente
    if exist "C:\Program Files\Docker\Docker\Docker Desktop.exe" (
        echo 🐳 Tentando iniciar Docker Desktop...
        start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
        echo ⏳ Aguarde 30 segundos para o Docker iniciar...
        timeout /t 30 /nobreak >nul
        
        :: Verifica novamente
        docker ps >nul 2>&1
        if %ERRORLEVEL% neq 0 (
            echo ❌ Docker ainda nao esta rodando!
            echo    Por favor, inicie manualmente e tente novamente
            pause
            exit /b 1
        )
        echo ✅ Docker iniciado com sucesso!
    ) else (
        echo    Docker Desktop nao encontrado em C:\Program Files\Docker\Docker\
        echo    Por favor, instale ou inicie manualmente
        pause
        exit /b 1
    )
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
echo 💡 Tentando iniciar com volumes nomeados (sem compartilhamento de diretorio)...
echo    Se falhar, tentaremos sem volumes...
echo.

:: Tenta primeiro com docker-compose.yml normal (volumes nomeados)
%DOCKER_COMPOSE_CMD% --profile production up --build -d

if %ERRORLEVEL% neq 0 (
    echo.
    echo ⚠️  Falha com volumes nomeados. Tentando sem volumes...
    echo    (Logs ficarao apenas dentro do container)
    echo.
    
    :: Tenta sem volumes
    %DOCKER_COMPOSE_CMD% -f docker-compose.sem-volumes.yml --profile production up --build -d
    
    if %ERRORLEVEL% neq 0 (
        echo.
        echo ❌ Erro ao iniciar Docker!
        echo.
        echo 💡 Possiveis solucoes:
        echo.
        echo    1. Verifique os logs: docker-compose logs
        echo    2. Tente executar como Administrador
        echo    3. Verifique se o arquivo .env existe e esta correto
        echo.
        pause
        exit /b 1
    ) else (
        echo ✅ Container iniciado SEM volumes (logs apenas no container)
        echo.
        echo 📋 Para ver logs, use:
        echo    docker logs drg-api
        echo    OU
        echo    docker exec drg-api cat /app/logs/drg_guias.log
        echo    OU copie para sua maquina:
        echo    copiar_logs_docker.bat
        echo.
        goto :docker_success
    )
) else (
    echo ✅ Container iniciado com volumes nomeados
    echo.
    echo 📋 Para copiar logs do container para sua maquina:
    echo    copiar_logs_docker.bat
    echo.
    goto :docker_success
)

:docker_success
echo.
echo 📊 Para ver os logs em tempo real, execute:
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
