# 🚀 Alternativas Docker Sem Compartilhamento de Diretório

## ✅ Solução Implementada

Criei **3 alternativas** que não precisam de compartilhamento de diretório no Windows:

### 1. **Volumes Nomeados** (Recomendado - `docker-compose.yml`)
- ✅ Não precisa de compartilhamento de diretório
- ✅ Logs ficam em volume Docker gerenciado
- ✅ Para copiar logs: `copiar_logs_docker.bat`

### 2. **Sem Volumes** (`docker-compose.sem-volumes.yml`)
- ✅ Funciona sempre, sem nenhuma permissão
- ⚠️ Logs ficam apenas dentro do container
- ✅ Para ver logs: `docker logs drg-api` ou `copiar_logs_docker.bat`

### 3. **Script Inteligente** (`start_drg_api_docker.bat`)
- ✅ Tenta volumes nomeados primeiro
- ✅ Se falhar, usa versão sem volumes automaticamente
- ✅ Funciona mesmo sem permissões!

## 🎯 Como Usar

### Opção Simples (Recomendada)

```bash
start_drg_api_docker.bat
```

O script vai:
1. Tentar iniciar com volumes nomeados (sem precisar de permissão)
2. Se falhar, tentar sem volumes automaticamente
3. Funcionar de qualquer forma!

### Ver Logs

**Se usar volumes nomeados:**
```bash
copiar_logs_docker.bat
```

**Se usar sem volumes:**
```bash
# Ver logs em tempo real
docker logs -f drg-api

# Ou copiar para sua máquina
copiar_logs_docker.bat
```

## 📋 Arquivos Criados

1. **`docker-compose.yml`** - Usa volumes nomeados (sem compartilhamento)
2. **`docker-compose.sem-volumes.yml`** - Versão sem volumes
3. **`copiar_logs_docker.bat`** - Copia logs do container para sua máquina
4. **`copiar_logs_docker.sh`** - Versão Linux/Mac

## 🔍 Diferenças

| Método | Compartilhamento? | Logs Acessíveis? | Recomendado? |
|--------|------------------|------------------|--------------|
| **Volumes Nomeados** | ❌ Não precisa | ✅ Sim (via script) | ⭐⭐⭐ |
| **Sem Volumes** | ❌ Não precisa | ⚠️ Apenas no container | ⭐⭐ |
| **Bind Mounts** (antigo) | ✅ Precisa | ✅ Sim | ❌ Problema! |

## 💡 Vantagens

✅ **Não precisa configurar nada no Docker Desktop**  
✅ **Funciona mesmo sem permissões de administrador**  
✅ **Scripts automáticos fazem tudo**  
✅ **Logs sempre acessíveis via `copiar_logs_docker.bat`**

## 🚀 Próximos Passos

1. Execute: `start_drg_api_docker.bat`
2. Se funcionar com volumes nomeados → use `copiar_logs_docker.bat` para ver logs
3. Se funcionar sem volumes → use `docker logs drg-api` ou `copiar_logs_docker.bat`

**Pronto! Sem precisar configurar compartilhamento!** 🎉

