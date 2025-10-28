#!/usr/bin/env bash
echo "======================================================="
echo "  INICIANDO DRG-GUIAS (PRODUCAO)"
echo "======================================================="

# Verifica se existe arquivo .env
if [ ! -f ".env" ]; then
  echo "⚠️  Arquivo .env nao encontrado!"
  echo "Por favor, copie env.example para .env e configure"
  exit 1
fi

# Remove variáveis antigas
unset ORACLE_HOME
unset TNS_ADMIN

# Define Instant Client correto
export ORACLE_DIR="/c/instantclient_21_13"
export PATH="$ORACLE_DIR:$PATH"

# Locale Oracle
export NLS_LANG="AMERICAN_AMERICA.AL32UTF8"

echo
echo "PATH configurado: $PATH"
echo "NLS_LANG=$NLS_LANG"
echo "ORACLE_DIR=$ORACLE_DIR"
echo

# Teste de conexão Oracle
echo "Testando conexao Oracle..."
python -c "import cx_Oracle; cx_Oracle.connect('inovemed/inov3m3d@drg@192.168.200.250:1521/trnmv'); print('✅ Conexao OK!')"
if [ $? -ne 0 ]; then
  echo "❌ Falha na conexao com o Oracle!"
  exit 1
fi

echo
echo "🚀 Iniciando aplicacao FastAPI (modo producao)..."
echo "======================================================="
python main.py
