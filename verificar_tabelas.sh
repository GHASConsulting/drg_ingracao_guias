#!/usr/bin/env bash
# Script wrapper para verificar tabelas com configuração correta do Oracle

# Configurar NLS_LANG antes de executar Python
export NLS_LANG="AMERICAN_AMERICA.AL32UTF8"

# Configurar PATH do Oracle Instant Client
export ORACLE_DIR="/c/instantclient_21_13"
export PATH="$ORACLE_DIR:$PATH"

# Executar script Python
python verificar_tabelas.py

