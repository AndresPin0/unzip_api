# Configuración de URLs - Guía Visual

## Diagrama de URLs y Conexiones

![Diagrama de URLs](/Diagramas/URL.png)

---

## URLs que DEBES Cambiar

### 1️En n8n Workflow (`XML invoice to TXT.json`)

#### Ubicación 1: Nodo "Enviar ZIP al Webhook" (línea 7)
```json
 ANTIGUO:
"url": "https://unzip-api.onrender.com/unzip-xml"

 NUEVO:
"url": "https://TU-BACKEND.com/unzip-xml"
```

####  Ubicación 2: Nodo "HTTP Request" (línea 198)
```json
ANTIGUO:
"url": "https://unzip-api.onrender.com/save-txt"

NUEVO:
"url": "https://TU-BACKEND.com/save-txt"
```

####  Ubicación 3: Nodo "Respond to Webhook" (línea 261)
```json
ANTIGUO:
"download_url": "https://unzip-api.onrender.com{{$json.download_url}}"

NUEVO:
"download_url": "https://TU-BACKEND.com{{$json.download_url}}"
```

####  Ubicación 4: Webhook CORS - allowedOrigins (línea 229)
```json
ANTIGUO:
"allowedOrigins": "https://zip-to-txt-wizard.lovable.app"

NUEVO:
"allowedOrigins": "https://TU-FRONTEND.com"
```

####  Ubicación 5: Webhook Headers - Access-Control-Allow-Origin (líneas 234 y 345)
```json
 ANTIGUO:
{
  "name": "Access-Control-Allow-Origin",
  "value": "https://zip-to-txt-wizard.lovable.app"
}

 NUEVO:
{
  "name": "Access-Control-Allow-Origin",
  "value": "https://TU-FRONTEND.com"
}
```

---

### 2️ En Frontend 

**Archivo**: `excel-drop-webhook-37694/src/components/ExcelUploadForm.tsx` (línea 55)

```typescript
 ANTIGUO (Railway - para otro sistema):
const response = await fetch('https://primary-production-38db.up.railway.app/webhook-test/recibir-archivo-excel', {

NUEVO (para usar n8n con XMLs):
const response = await fetch('https://TU-N8N.com/webhook/dian-xml-process', {
```

---

##  Resumen de Cambios Requeridos

### Archivo: `XML invoice to TXT.json` (n8n workflow)

| Línea | Nodo | Campo | Valor Anterior | Valor Nuevo |
|-------|------|-------|----------------|-------------|
| 7 | Enviar ZIP al Webhook | url | `unzip-api.onrender.com/unzip-xml` | `TU-BACKEND.com/unzip-xml` |
| 198 | HTTP Request | url | `unzip-api.onrender.com/save-txt` | `TU-BACKEND.com/save-txt` |
| 229 | Webhook | allowedOrigins | `zip-to-txt-wizard.lovable.app` | `TU-FRONTEND.com` |
| 234 | Webhook | Access-Control-Allow-Origin | `zip-to-txt-wizard.lovable.app` | `TU-FRONTEND.com` |
| 261 | Respond to Webhook | download_url | `unzip-api.onrender.com{{...}}` | `TU-BACKEND.com{{...}}` |
| 345 | Respond to Webhook1 | Access-Control-Allow-Origin | `zip-to-txt-wizard.lovable.app` | `TU-FRONTEND.com` |

### Archivo: Frontend (opcional)

| Archivo | Línea | Cambio |
|---------|-------|--------|
| `src/components/ExcelUploadForm.tsx` | 55 | Actualizar webhook URL a tu n8n |

---

##  Buscar y Reemplazar (Find & Replace)

### En el archivo JSON de n8n:

```bash
# Reemplazo 1: Backend
Buscar:    unzip-api.onrender.com
Reemplazar: TU-BACKEND.com

# Reemplazo 2: Frontend
Buscar:    zip-to-txt-wizard.lovable.app
Reemplazar: TU-FRONTEND.com
```

### Usando sed (Linux/Mac):

```bash
# Backup del archivo original
cp "XML invoice to TXT.json" "XML invoice to TXT.json.backup"

# Reemplazar URLs del backend
sed -i 's|unzip-api.onrender.com|TU-BACKEND.com|g' "XML invoice to TXT.json"

# Reemplazar URLs del frontend
sed -i 's|zip-to-txt-wizard.lovable.app|TU-FRONTEND.com|g' "XML invoice to TXT.json"
```

### Usando PowerShell (Windows):

```powershell
# Backup
Copy-Item "XML invoice to TXT.json" "XML invoice to TXT.json.backup"

# Leer contenido
$content = Get-Content "XML invoice to TXT.json" -Raw

# Reemplazar URLs
$content = $content -replace 'unzip-api.onrender.com', 'TU-BACKEND.com'
$content = $content -replace 'zip-to-txt-wizard.lovable.app', 'TU-FRONTEND.com'

# Guardar
Set-Content "XML invoice to TXT.json" $content
```

---


##  Tabla de Endpoints

### Backend Endpoints:

| Método | Endpoint | Descripción | Usado por |
|--------|----------|-------------|-----------|
| POST | `/unzip-xml` | Descomprime ZIP y parsea XMLs | n8n (nodo "Enviar ZIP") |
| POST | `/save-txt` | Guarda archivo TXT generado | n8n (nodo "HTTP Request") |
| GET | `/download/:filename` | Descarga archivo generado | Frontend / Usuario |
| GET | `/files` | Lista archivos disponibles | (Opcional) Frontend |
| DELETE | `/files/:filename` | Elimina archivo específico | (Opcional) Frontend |
| GET | `/docs` | Documentación Swagger | Desarrolladores |

### n8n Endpoints:

| Método | Endpoint | Descripción | Usado por |
|--------|----------|-------------|-----------|
| POST | `/webhook/dian-xml-process` | Recibe ZIP desde frontend | Frontend |
| OPTIONS | `/webhook/dian-xml-process` | CORS preflight | Browser |

---

### Probar Webhooks:

```bash
# curl
curl -X POST https://TU-N8N.com/webhook/dian-xml-process \
  -H "Content-Type: application/json" \
  -d @test-payload.json

# httpie
http POST https://TU-N8N.com/webhook/dian-xml-process < test-payload.json
```

### Validar JSON:

```bash
# Validar sintaxis del workflow
cat "XML invoice to TXT.json" | jq '.'

# Extraer solo las URLs
cat "XML invoice to TXT.json" | jq '.. | .url? // empty'
```

### Monitoreo:

```bash
# Logs del backend (si es local)
tail -f logs/app.log

# Logs de n8n
# Ver en UI: Executions → Click en ejecución → Ver detalles
```

---

