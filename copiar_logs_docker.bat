@echo off
echo ========================================================
echo   COPIANDO LOGS DO CONTAINER DOCKER
echo ========================================================

:: Verifica se container está rodando
docker ps --filter "name=drg-api" --format "{{.Names}}" | findstr /C:"drg-api" >nul
if %ERRORLEVEL% neq 0 (
    echo ❌ Container drg-api nao esta rodando!
    echo    Execute: start_drg_api_docker.bat
    pause
    exit /b 1
)

:: Cria diretório logs local se não existir
if not exist "logs" (
    echo 📁 Criando diretorio logs...
    mkdir logs
)

echo 📋 Copiando logs do container...
docker cp drg-api:/app/logs/. ./logs/

if %ERRORLEVEL% equ 0 (
    echo ✅ Logs copiados com sucesso!
    echo.
    echo 📁 Logs disponiveis em: %CD%\logs
    echo.
    echo Para ver os logs:
    echo    type logs\drg_guias.log
) else (
    echo ⚠️  Nao foi possivel copiar todos os logs
    echo    Tentando copiar arquivo especifico...
    docker cp drg-api:/app/logs/drg_guias.log ./logs/drg_guias.log 2>nul
    docker cp drg-api:/app/logs/security.log ./logs/security.log 2>nul
    echo ✅ Logs principais copiados!
)

echo.
pause

