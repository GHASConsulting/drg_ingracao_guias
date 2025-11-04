#!/usr/bin/env bash
echo "======================================================="
echo "  INICIANDO DRG-GUIAS (DESENVOLVIMENTO)"
echo "======================================================="

# Verifica se existe arquivo .env
if [ ! -f ".env" ]; then
  echo "⚠️  Arquivo .env nao encontrado!"
  echo "Por favor, copie env.example para .env e configure"
  exit 1
fi

# Verifica se existe ambiente virtual
if [ ! -d "venv" ]; then
  echo "⚠️  Ambiente virtual nao encontrado!"
  echo "Criando ambiente virtual..."
  python -m venv venv
  if [ $? -ne 0 ]; then
    echo "❌ Erro ao criar ambiente virtual!"
    exit 1
  fi
fi

# Ativa ambiente virtual (Linux/Git Bash)
if [ -f "venv/bin/activate" ]; then
  source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
  source venv/Scripts/activate
else
  echo "⚠️  Script de ativacao do ambiente virtual nao encontrado!"
  exit 1
fi

# Verifica se pip está disponível
if ! command -v pip &> /dev/null; then
  echo "❌ pip nao encontrado! Instale Python 3.11+"
  exit 1
fi

# Verifica se cx_Oracle está instalado
echo "Verificando dependencias..."
python -c "import cx_Oracle" 2>/dev/null
if [ $? -ne 0 ]; then
  echo "⚠️  Dependencias nao instaladas. Instalando..."
  pip install -r requirements.txt
  if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar dependencias!"
    exit 1
  fi
  echo "✅ Dependencias instaladas com sucesso!"
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
echo "Python: $(python --version)"
echo "Ambiente virtual: $(which python)"
echo

# Teste opcional de conexão Oracle (modo desenvolvimento)
echo "Testando conexao Oracle..."
python -c "import cx_Oracle; cx_Oracle.connect('inovemed/inov3m3d@drg@192.168.200.250:1521/trnmv'); print('✅ Conexao OK!')" 2>/dev/null
if [ $? -ne 0 ]; then
  echo "⚠️  Aviso: Nao foi possivel testar conexao Oracle"
  echo "A aplicacao sera iniciada mesmo assim (modo desenvolvimento)"
fi

echo
echo "🚀 Iniciando aplicacao FastAPI (modo desenvolvimento)..."
echo "======================================================="
python main.py

