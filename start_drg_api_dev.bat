@echo off
echo =======================================================
echo   INICIANDO DRG-GUIAS (DESENVOLVIMENTO)
echo =======================================================

:: Verifica se existe arquivo .env
if not exist ".env" (
    echo ⚠️  Arquivo .env nao encontrado!
    echo Por favor, copie env.example para .env e configure
    pause
    exit /b 1
)

:: Ativa ambiente virtual
if exist "venv\Scripts\activate" (
    call venv\Scripts\activate
    echo ✅ Ambiente virtual Python ativado.
) else (
    echo ⚠️  Ambiente virtual nao encontrado em venv\Scripts
    pause
    exit /b 1
)

:: Remove variáveis Oracle antigas
set ORACLE_HOME=
set TNS_ADMIN=

:: Define Instant Client correto
set ORACLE_DIR=C:\instantclient_21_13
set PATH=%ORACLE_DIR%;%PATH%

:: Define locale Oracle (corrige ORA-01804)
set NLS_LANG=AMERICAN_AMERICA.AL32UTF8

:: Mostra configuracoes atuais
echo.
echo PATH: %PATH%
echo ORACLE_DIR=%ORACLE_DIR%
echo NLS_LANG=%NLS_LANG%
echo.

:: Teste opcional de conexao
echo Testando conexao Oracle...
python -c "import cx_Oracle; cx_Oracle.connect('inovemed/inov3m3d@drg@192.168.200.250:1521/trnmv'); print('✅ Conexao OK!')"
if %ERRORLEVEL% neq 0 (
    echo ❌ Falha na conexao com o Oracle!
    pause
    exit /b 1
)

echo.
echo 🚀 Iniciando aplicacao FastAPI (modo desenvolvimento)...
echo =======================================================
python main.py

pause
