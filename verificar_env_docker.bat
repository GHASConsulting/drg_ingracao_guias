@echo off
echo ========================================================
echo   VERIFICANDO VARIAVEIS DE AMBIENTE NO DOCKER
echo ========================================================

:: Verifica se container está rodando
docker ps --filter "name=drg-api" --format "{{.Names}}" | findstr /C:"drg-api" >nul
if %ERRORLEVEL% neq 0 (
    echo ❌ Container drg-api nao esta rodando!
    echo    Execute: start_drg_api_docker.bat
    pause
    exit /b 1
)

echo ✅ Container encontrado
echo.
echo 📋 Verificando variaveis importantes do .env:
echo.

echo [DATABASE]
docker exec drg-api sh -c "echo DATABASE_TYPE=$DATABASE_TYPE"
docker exec drg-api sh -c "echo ORACLE_HOST=$ORACLE_HOST"
docker exec drg-api sh -c "echo ORACLE_USERNAME=$ORACLE_USERNAME"

echo.
echo [DRG API]
docker exec drg-api sh -c "echo DRG_USERNAME=$DRG_USERNAME"
docker exec drg-api sh -c "echo DRG_API_URL=$DRG_API_URL"
docker exec drg-api sh -c "echo DRG_API_PULL_URL=$DRG_API_PULL_URL"

echo.
echo [MONITORAMENTO]
docker exec drg-api sh -c "echo AUTO_MONITOR_ENABLED=$AUTO_MONITOR_ENABLED"
docker exec drg-api sh -c "echo MONITOR_PULL_ENABLED=$MONITOR_PULL_ENABLED"

echo.
echo ========================================================
echo   TESTE: Verificando se aplicacao leu as configuracoes
echo ========================================================
echo.
echo Executando teste dentro do container...
docker exec drg-api python -c "from app.config.config import get_settings; s = get_settings(); print(f'DATABASE_TYPE: {s.DATABASE_TYPE}'); print(f'ORACLE_HOST: {s.ORACLE_HOST}'); print(f'DRG_USERNAME: {s.DRG_USERNAME}'); print(f'DRG_API_URL: {s.DRG_API_URL}')"

echo.
pause

