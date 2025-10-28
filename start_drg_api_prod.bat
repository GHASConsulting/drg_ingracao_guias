@echo off
echo =======================================================
echo   INICIANDO DRG-GUIAS (PRODUCAO)
echo =======================================================

:: Verifica se existe arquivo .env
if not exist ".env" (
    echo ⚠️  Arquivo .env nao encontrado!
    echo Por favor, copie env.example para .env e configure
    exit /b 1
)

:: Limpa variáveis antigas
set ORACLE_HOME=
set TNS_ADMIN=

:: Define Instant Client correto
set ORACLE_DIR=C:\instantclient_21_13
set PATH=%ORACLE_DIR%;%PATH%

:: Locale padrão Oracle
set NLS_LANG=AMERICAN_AMERICA.AL32UTF8

:: Exibe variáveis configuradas
echo.
echo PATH configurado:
echo %PATH%
echo NLS_LANG=%NLS_LANG%
echo ORACLE_DIR=%ORACLE_DIR%
echo.

:: Testa conexão Oracle antes de iniciar
echo Testando conexao Oracle...
python -c "import cx_Oracle; cx_Oracle.connect('inovemed/inov3m3d@drg@192.168.200.250:1521/trnmv'); print('✅ Conexao OK!')"
if %ERRORLEVEL% neq 0 (
    echo ❌ Falha na conexao com o Oracle!
    exit /b 1
)

:: Inicia aplicação
echo.
echo 🚀 Iniciando FastAPI em modo producao...
echo =======================================================
python main.py
