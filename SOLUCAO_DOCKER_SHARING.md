# 🔧 Solução: Erro de Compartilhamento de Diretório no Docker

## ❌ Erro Encontrado

```
Error response from daemon: user declined directory sharing 
C:\DRG-INOVEMED\DRG_GUIAS\drg_guias_integracao\drg_ingracao_guias\logs
```

## 🔍 Causa

O Docker Desktop no Windows precisa de permissão explícita para compartilhar diretórios locais com os containers. Quando você usa volumes no `docker-compose.yml`, o Docker precisa acessar esses diretórios.

## ✅ Solução Passo a Passo

### Método 1: Aceitar o Prompt (Mais Rápido)

1. **Execute o script novamente:**
   ```bash
   start_drg_api_docker.bat
   ```

2. **Quando aparecer o prompt do Docker Desktop:**
   - Clique em **"Share it"** ou **"Compartilhar"**
   - Aguarde o Docker processar

3. **Execute o script novamente** após aceitar

### Método 2: Configurar Manualmente no Docker Desktop

1. **Abra o Docker Desktop**

2. **Vá em Settings (Configurações):**
   - Clique no ícone de engrenagem ⚙️ no canto superior direito
   - Ou vá em **Settings** no menu

3. **Navegue até Resources > File Sharing:**
   - No menu lateral, clique em **Resources**
   - Depois clique em **File Sharing**

4. **Adicione o diretório:**
   - Clique em **"+"** ou **"Add"**
   - Digite ou navegue até: `C:\DRG-INOVEMED`
   - Clique em **"Apply & Restart"**

5. **Aguarde o Docker reiniciar**

6. **Execute o script novamente:**
   ```bash
   start_drg_api_docker.bat
   ```

### Método 3: Adicionar Diretório Específico

Se preferir compartilhar apenas o diretório do projeto:

1. **No Docker Desktop > Settings > Resources > File Sharing**

2. **Adicione:**
   ```
   C:\DRG-INOVEMED\DRG_GUIAS\drg_guias_integracao\drg_ingracao_guias
   ```

3. **Apply & Restart**

## 🔍 Verificar se Está Configurado

1. Abra Docker Desktop
2. Vá em **Settings > Resources > File Sharing**
3. Verifique se `C:\DRG-INOVEMED` (ou o diretório do projeto) está na lista

## ⚠️ Observações Importantes

- **Permissões de Administrador:** Se ainda der erro, tente executar o Docker Desktop como Administrador
- **Reinício:** Após adicionar um diretório, o Docker Desktop precisa reiniciar
- **Segurança:** Compartilhar diretórios grandes pode afetar a performance

## 🚀 Após Configurar

Depois de configurar o compartilhamento, execute:

```bash
start_drg_api_docker.bat
```

O container deve iniciar normalmente! 🎉

## 📝 Nota Técnica

O `docker-compose.yml` usa volumes para:
- `./logs:/app/logs` - Compartilhar logs entre host e container
- `./.env:/app/.env` - Compartilhar variáveis de ambiente

Esses volumes permitem que você veja os logs no diretório `logs/` localmente e mantenha o `.env` sincronizado.

