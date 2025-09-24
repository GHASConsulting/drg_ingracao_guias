# Regras de Desenvolvimento - Sistema DRG (FastAPI)

## 📋 Regras Estabelecidas

### 1. **Controle de Arquivos**

- ❌ **NÃO** criar arquivos sem permissão explícita do usuário
- ❌ **NÃO** criar arquivos fora do contexto ou "do nada"
- ✅ **SEMPRE** pedir permissão antes de criar qualquer arquivo
- ✅ **SEMPRE** explicar o motivo e contexto do arquivo a ser criado

### 2. **Metodologia de Desenvolvimento**

- 🔄 **Desenvolvimento passo a passo** - arquivo por arquivo
- 🧪 **Testar cada etapa** antes de prosseguir
- 📝 **Validar cada implementação** antes da próxima
- 🎯 **Foco em uma funcionalidade por vez**

### 3. **Execução de Comandos**

- 💻 **Usuário executa comandos** - assistente fornece os comandos
- 📊 **Usuário envia logs** - assistente analisa resultados
- 🔍 **Análise colaborativa** dos resultados
- ⚠️ **Nunca executar comandos automaticamente**

### 4. **Nível de Desenvolvimento**

- 👨‍💻 **Nível pleno** - código profissional e bem estruturado
- 🎯 **Funcional e robusto** - priorizar funcionalidade
- 🚫 **Evitar complexidade desnecessária** - simplicidade é chave
- 📚 **Código limpo e legível** - fácil manutenção

### 5. **Colaboração**

- 🤝 **Desenvolvimento colaborativo** - usuário e assistente juntos
- 💡 **Autocompletes e sugestões** - assistente oferece melhorias
- 🗣️ **Comunicação clara** - explicar cada decisão
- 📖 **Documentação contínua** - registrar decisões e mudanças

## 🎯 Objetivos do Projeto

### Sistema DRG - Guias de Internação (FastAPI)

- **Backend**: API REST em FastAPI (simplificado)
- **Banco**: Oracle (padrão), PostgreSQL, Firebird, SQLite (teste)
- **Processamento**: Síncrono (simplificado)
- **Validação**: Pydantic v2
- **Tabela**: Tabela de guias no banco

### Funcionalidades Principais

1. Cliente alimenta tabela de guias no banco
2. FastAPI processa via rotas da API
3. Validar dados de beneficiários, prestadores, procedimentos
4. Montar JSON e enviar para API do DRG Brasil
5. Atualizar status de processamento na tabela
6. Logs de auditoria

### Integração com DRG Brasil

- **Autenticação**: JWT com expiração de 4 horas
- **URL Auth**: https://api-autenticacao.iagsaude.com/login (teste)
- **URL API**: https://api-hospitalar.iagsaude.com/integracao/guias/save (teste)
- **Headers**: Authorization (JWT) + x-api-key
- **Limite**: 500KB por lote
- **Processamento**: Síncrono

## 📁 Estrutura Atual (FastAPI)

```
drg_guias/
├── main.py                    # Ponto de entrada FastAPI
├── app/
│   ├── models/                # Modelos SQLAlchemy
│   ├── routes/                # Rotas FastAPI
│   │   └── fastapi_routes.py  # Router principal
│   ├── services/              # Lógica de negócio
│   ├── schemas/               # Schemas Pydantic
│   ├── utils/                 # Utilitários e helpers
│   ├── config/                # Configurações
│   │   └── config.py          # Settings com Pydantic
│   ├── database/              # Configurações de conexão
│   │   └── database.py        # SQLAlchemy direto
│   └── celery_app.py          # Configuração Celery
├── tests/                     # Testes unitários
├── database/                  # Banco SQLite de teste
├── docs/                      # Documentação
├── requirements.txt           # Dependências FastAPI
├── env.example                # Variáveis de ambiente
├── testar_api.py             # Script de testes
└── adicionar_guias.py        # Script para adicionar dados
```

## 🔄 Workflow de Desenvolvimento

### 1. **Análise e Planejamento**

- [x] Analisar arquivos de documentação
- [x] Definir stack tecnológico
- [x] Estabelecer regras de desenvolvimento
- [x] Analisar estrutura do Excel
- [x] Definir modelos de dados

### 2. **Estrutura Base**

- [x] Criar estrutura de pastas
- [x] Configurar ambiente virtual
- [x] Instalar dependências FastAPI
- [x] Configurar banco de dados

### 3. **Modelos e Banco**

- [x] Criar modelos SQLAlchemy básicos
- [x] ~~Criar modelo FilaProcesso~~ (Removido - não necessário)
- [x] Implementar schemas de validação (Pydantic)
- [x] Configurar banco de dados (SQLite para testes)
- [x] Testar conexão com banco

### 4. **Processamento (Simplificado)**

- [x] ~~Configurar Celery + Redis~~ (Removido - não necessário)
- [x] ~~Criar worker para monitorar fila~~ (Removido - não necessário)
- [x] ~~Implementar processamento assíncrono~~ (Removido - não necessário)
- [x] ~~Configurar retry automático~~ (Removido - não necessário)

### 5. **Integração com DRG**

- [x] Implementar autenticação JWT
- [x] Criar serviço de envio para DRG
- [x] Implementar tratamento de respostas
- [x] Configurar headers de autenticação

### 6. **API e Testes**

- [x] Implementar rotas da API (status, monitoramento)
- [x] Criar serviços de negócio
- [x] Criar testes unitários
- [x] Testes de integração completos
- [x] **MIGRAÇÃO FLASK → FASTAPI CONCLUÍDA**

## ⚠️ Lembretes Importantes

- **SEMPRE** pedir permissão antes de criar arquivos
- **SEMPRE** explicar o contexto e motivo
- **SEMPRE** testar cada etapa antes de prosseguir
- **SEMPRE** manter código simples e funcional
- **SEMPRE** documentar decisões importantes

## 📝 Log de Decisões

### Data: 2024-12-19

- **Decisão**: Estabelecer regras de desenvolvimento
- **Motivo**: Garantir controle e qualidade do desenvolvimento
- **Impacto**: Metodologia clara e colaborativa

### Data: 2024-12-19

- **Decisão**: Integração com DRG Brasil via API REST
- **Motivo**: Especificação oficial do DRG Brasil
- **Impacto**: Sistema deve enviar dados para API externa com autenticação JWT

### Data: 2024-12-19

- **Decisão**: Padrão de nomenclatura de tabelas Inovamed
- **Motivo**: Padrão da empresa (inovemed*tbl*[nome])
- **Impacto**: Tabelas seguem nomenclatura específica da Inovamed

### Data: 2024-12-19

- **Decisão**: ~~Arquitetura com fila no banco + Celery Workers~~ (REVOGADA)
- **Motivo**: ~~Fluxo real identificado: Cliente → Tabela → API consome → DRG~~ (Simplificado)
- **Impacto**: ~~Necessário Celery + Redis para processamento assíncrono da fila~~ (Removido - não necessário)

### Data: 2024-12-19

- **Decisão**: Integração DRG testada e validada com Insomnia
- **Motivo**: Confirmar formato correto de autenticação e envio de dados
- **Impacto**: Serviços DRGService e GuiaService implementados com formato correto

### Data: 2024-12-19

- **Decisão**: URLs de teste/homologação para DRG
- **Motivo**: Testar integração sem afetar ambiente de produção
- **Impacto**: Sistema configurado para ambiente de teste da DRG Brasil

### Data: 2025-09-23

- **Decisão**: MIGRAÇÃO COMPLETA FLASK → FASTAPI
- **Motivo**: Framework mais moderno, performance superior, documentação automática
- **Impacto**:
  - ✅ 8/8 testes passando (100% sucesso)
  - ✅ Todas as rotas funcionando
  - ✅ Schemas Pydantic v2 implementados
  - ✅ Documentação automática (Swagger/ReDoc)
  - ✅ Dependency injection para banco
  - ✅ Sistema pronto para produção

### Data: 2025-09-23

- **Decisão**: SQLite para testes e desenvolvimento
- **Motivo**: Facilita testes locais e desenvolvimento
- **Impacto**: Banco de teste funcionando com dados fictícios

### Data: 2025-09-23

- **Decisão**: LIMPEZA CELERY/REDIS - Sistema Simplificado
- **Motivo**: Processamento assíncrono desnecessário para o volume atual
- **Impacto**:
  - ✅ Sistema mais simples e direto
  - ✅ Menos dependências para instalar
  - ✅ Deploy mais fácil
  - ✅ Manutenção simplificada
  - ✅ 8/8 testes passando (100% sucesso)

### Data: 2025-09-23

- **Decisão**: MONITORAMENTO AUTOMÁTICO DA TABELA
- **Motivo**: Processar guias em tempo real sem intervenção manual
- **Impacto**:
  - ✅ Monitoramento automático configurável via ENV
  - ✅ Controle via API (start/stop/status)
  - ✅ Logs detalhados de monitoramento
  - ✅ Processamento em tempo real
  - ✅ Sistema 100% automatizado

---

_Este arquivo deve ser atualizado sempre que novas regras forem estabelecidas ou modificadas._
