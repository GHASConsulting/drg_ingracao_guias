# PUT para DRG - Guia Aprovada com Senha

## 📋 Requisito Futuro

### Fluxo Atual

1. Guia é consultada externamente
2. Se aprovada, `situacao_guia = "A"`
3. Trigger no banco preenche `senha_autorizacao`
4. Monitoramento detecta mudança
5. **PENDENTE**: Enviar PUT para DRG com a senha

### Implementação Necessária

#### 1. Detecção de Senha Preenchida

```python
# No MonitorCamposService
def _detectar_senha_preenchida(self, guia: Guia) -> bool:
    """
    Detecta se a senha_autorizacao foi preenchida por trigger
    """
    return (
        guia.situacao_guia == "A" and
        guia.senha_autorizacao is not None and
        guia.senha_autorizacao.strip() != ""
    )
```

#### 2. Envio de JSON Completo

```python
# Usando o método existente para montar JSON completo
def _enviar_put_guia_aprovada(self, db: Session, guia: Guia) -> Dict[str, Any]:
    """
    Envia guia aprovada completa com senha via POST para a rota principal
    """
    # Montar JSON completo da guia usando o método existente
    json_completo = self.guia_service.montar_json_drg(guia)

    # Adicionar tipo de operação para identificar que é guia aprovada
    if "loteGuias" in json_completo and "guia" in json_completo["loteGuias"]:
        for guia_item in json_completo["loteGuias"]["guia"]:
            guia_item["tipoOperacao"] = "PUT_APROVADA"
            # Garantir que a senha de autorização está incluída
            if guia.senha_autorizacao:
                guia_item["senhaAutorizacao"] = guia.senha_autorizacao

    # Enviar JSON completo para DRG usando o método existente
    return self.drg_service.enviar_guia(json_completo)
```

#### 3. Integração no Monitoramento

```python
# No MonitorCamposService._processar_guia
if self._detectar_senha_preenchida(guia):
    # Enviar PUT para DRG
    resultado_put = await self._enviar_put_drg_aprovada(db, guia)

    if resultado_put["sucesso"]:
        guia.status_monitoramento = "F"  # Finalizar
        guia.tp_status = "T"  # Transmitida
        db.commit()
```

### Campos Críticos para Monitoramento

- `situacao_guia` = "A" (Aprovada)
- `senha_autorizacao` != null/empty (Preenchida por trigger)

### Configurações Necessárias

```env
# Usando a mesma rota principal
DRG_API_URL=https://api-hospitalar.iagsaude.com/integracao/guias/save

# Timeout para envio de guia aprovada
DRG_PUT_TIMEOUT_MS=30000

# Tentativas para envio
DRG_PUT_MAX_TENTATIVAS=3
```

### Status de Monitoramento

- **N**: Não monitorando
- **M**: Monitorando (aguardando senha)
- **F**: Finalizado (PUT enviado com sucesso)

### Logs Esperados

```
INFO - 🔍 Detectada guia aprovada com senha: R679541
INFO - 📡 Enviando guia aprovada completa para DRG - R679541
INFO - ✅ Guia aprovada completa enviada com sucesso para R679541
INFO - 🏁 Monitoramento finalizado para guia R679541
```

### Testes Necessários

1. Simular trigger preenchendo `senha_autorizacao`
2. Verificar detecção pelo monitoramento
3. Testar envio de PUT para DRG
4. Validar finalização do monitoramento

### Dependências

- ✅ Campo `senha_autorizacao` já existe
- ✅ Monitoramento de campos já implementado
- ✅ Rota principal do DRG já configurada
- ✅ Detecção de senha preenchida implementada
- ✅ Integração no monitoramento implementada

### Prioridade

**ALTA** - Funcionalidade crítica para fluxo completo

### Estimativa

- ✅ Detecção de senha: Implementado
- ✅ Envio via rota principal: Implementado
- ✅ Integração: Implementado
- ✅ Testes: Implementado

**Total**: ✅ CONCLUÍDO

### Vantagens do Envio Completo

✅ **Consistência**: Usa o mesmo método de montagem do JSON
✅ **Completude**: Todos os campos da guia são enviados
✅ **Confiabilidade**: Evita erros de campos faltando
✅ **Manutenibilidade**: Reutiliza código existente
✅ **Rastreabilidade**: Mantém histórico completo da guia
