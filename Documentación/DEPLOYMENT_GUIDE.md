# Guía de Despliegue - Sistema de Procesamiento de Facturas XML

## Arquitectura del Sistema

![Diagrama de Arquitectura](/Diagramas/Arquitectura.png)

##  Flujo de Datos Detallado

1. **Usuario sube archivo ZIP** → Frontend React
2. **Frontend codifica a Base64** → Envía POST al Webhook n8n
3. **n8n valida CORS** → Verifica origen permitido
4. **n8n extrae datos** → filename + content (base64)
5. **n8n → Backend** → POST a `/unzip-xml` con el ZIP
6. **Backend descomprime** → Extrae y parsea archivos XML
7. **Backend → n8n** → Devuelve array de XMLs parseados a JSON
8. **n8n procesa datos** → Split items, extrae campos de factura
9. **n8n genera archivo** → Code node crea formato FPBATCH.txt
10. **n8n → Backend** → POST a `/save-txt` con contenido
11. **Backend guarda archivo** → Crea archivo físico en `temp_txt/`
12. **Backend → n8n** → Devuelve URL de descarga
13. **n8n → Frontend** → Responde con URL completa
14. **Usuario descarga** → GET a `/download/:filename`

---

##  Componentes del Sistema

### 1. Frontend (excel-drop-webhook-37694)
- **Tecnología**: React + TypeScript + Vite
- **Framework UI**: Shadcn/ui + Tailwind CSS
- **Función**: Interfaz para subir archivos ZIP con XMLs
- **Dependencias**: Ver `package.json`

### 2. Backend (unzip_api)
- **Tecnología**: Python + FastAPI + Uvicorn
- **Función**: API REST para procesar ZIPs y generar archivos TXT
- **Dependencias**: Ver `requirements.txt`

### 3. n8n Workflow (XML invoice to TXT.json)
- **Plataforma**: n8n (self-hosted o cloud)
- **Función**: Orquestación del flujo de procesamiento
- **Archivo**: `XML invoice to TXT.json`

---

##  Instrucciones de Despliegue

### OPCIÓN A: Despliegue Local

#### 1. Backend (unzip_api)

```bash
# Navegar al directorio
cd unzip_api

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# URL local: http://localhost:8000
# Documentación: http://localhost:8000/docs
```

#### 2. Frontend (excel-drop-webhook-37694)

```bash
# Navegar al directorio
cd excel-drop-webhook-37694

# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm run dev

# URL local: http://localhost:5173
```

#### 3. n8n (Local)

```bash
# Instalar n8n globalmente
npm install -g n8n

# Ejecutar n8n
n8n start

# Acceder a: http://localhost:5678
```

**Importar workflow:**
1. Ir a n8n UI → Workflows
2. Click en "Import from File"
3. Seleccionar `XML invoice to TXT.json`
4. Workflow se carga automáticamente

---

### OPCIÓN B: Despliegue en la Nube

#### 1. Backend en Render.com

```bash
# 1. Crear cuenta en https://render.com
# 2. Conectar repositorio GitHub/GitLab
# 3. Crear nuevo "Web Service"
# 4. Configurar:
```

**Configuración Render:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`
- **Runtime**: Python 3
- **Environment**: 
  - `PYTHON_VERSION=3.11.0` (o superior)
- **Plan**: Free tier OK para pruebas

**URL de ejemplo**: `https://tu-backend.onrender.com`

#### 2. Frontend en Vercel/Netlify/Render

**Opción Vercel:**
```bash
# Instalar Vercel CLI
npm install -g vercel

# Desplegar
cd excel-drop-webhook-37694
vercel --prod
```

**Opción Netlify:**
```bash
# Instalar Netlify CLI
npm install -g netlify-cli

# Build
npm run build

# Desplegar
netlify deploy --prod --dir=dist
```

**Opción Lovable (actual):**
- Ya desplegado en: https://lovable.dev
- Configurar dominio custom si es necesario

#### 3. n8n Cloud o Self-hosted

**Opción A - n8n Cloud:**
1. Crear cuenta en https://n8n.io
2. Importar workflow desde `XML invoice to TXT.json`
3. URL webhook: `https://tu-cuenta.app.n8n.cloud/webhook/dian-xml-process`

**Opción B - n8n Self-hosted (Docker):**
```bash
# Con Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# Con Docker Compose
version: '3.8'
services:
  n8n:
    image: n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=password
      - N8N_HOST=0.0.0.0
      - WEBHOOK_URL=https://tu-dominio.com
    volumes:
      - ~/.n8n:/home/node/.n8n
```

**Opción C - n8n en Render/Railway:**
```yaml
# render.yaml para n8n
services:
  - type: web
    name: n8n
    runtime: docker
    dockerfilePath: ./Dockerfile
    envVars:
      - key: N8N_HOST
        value: 0.0.0.0
      - key: N8N_PORT
        value: 5678
      - key: WEBHOOK_URL
        sync: false
```

---

## 🔧 Configuración de URLs

### URLs Actuales (NO FUNCIONALES)
```javascript
// ESTAS URLs YA NO FUNCIONAN - DEBEN SER REEMPLAZADAS:

Backend antiguo: https://unzip-api.onrender.com
Frontend antiguo: https://zip-to-txt-wizard.lovable.app
Railway endpoint: https://primary-production-38db.up.railway.app
```

### URLs que DEBES CONFIGURAR

#### 1. Actualizar Backend en n8n Workflow

**Archivo**: `XML invoice to TXT.json`

**Buscar y reemplazar:**

```json
// Línea 7 - Nodo "Enviar ZIP al Webhook"
{
  "url": "https://unzip-api.onrender.com/unzip-xml"
}
// CAMBIAR A:
{
  "url": "https://TU-BACKEND-NUEVO.com/unzip-xml"
}

// Línea 198 - Nodo "HTTP Request" (save-txt)
{
  "url": "https://unzip-api.onrender.com/save-txt"
}
// CAMBIAR A:
{
  "url": "https://TU-BACKEND-NUEVO.com/save-txt"
}

// Línea 261 - Nodo "Respond to Webhook"
{
  "download_url": "https://unzip-api.onrender.com{{$json.download_url}}"
}
// CAMBIAR A:
{
  "download_url": "https://TU-BACKEND-NUEVO.com{{$json.download_url}}"
}
```

#### 2. Actualizar Frontend en n8n Webhook

**Archivo**: `XML invoice to TXT.json`

**Buscar y reemplazar:**

```json
// Línea 229 - Nodo "Webhook" - allowedOrigins
{
  "allowedOrigins": "https://zip-to-txt-wizard.lovable.app"
}
// CAMBIAR A:
{
  "allowedOrigins": "https://TU-FRONTEND-NUEVO.com"
}

// Líneas 234, 345 - Headers CORS
{
  "name": "Access-Control-Allow-Origin",
  "value": "https://zip-to-txt-wizard.lovable.app"
}
// CAMBIAR A:
{
  "name": "Access-Control-Allow-Origin",
  "value": "https://TU-FRONTEND-NUEVO.com"
}
```

#### 3. Actualizar Webhook URL en Frontend

**Archivo**: `excel-drop-webhook-37694/src/components/ExcelUploadForm.tsx`

Este archivo tiene un webhook diferente (Railway), pero si quieres usar n8n:

```typescript
// Línea 55 - Cambiar endpoint
const response = await fetch('https://primary-production-38db.up.railway.app/webhook-test/recibir-archivo-excel', {
// SI USAS n8n, CAMBIAR A:
const response = await fetch('https://TU-N8N-URL.com/webhook/dian-xml-process', {
```

**O crear un componente nuevo para el procesamiento de XMLs:**

```typescript
// Archivo: src/components/XMLUploadForm.tsx
const response = await fetch('https://TU-N8N-URL.com/webhook/dian-xml-process', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    filename: file.name,
    content: base64Content
  })
});
```

---

## Pruebas Manuales

### 1. Probar Backend Directamente

```bash
# Test 1: Health check
curl https://TU-BACKEND.com/docs

# Test 2: Procesar XML (con archivo de prueba)
curl -X POST https://TU-BACKEND.com/unzip-xml \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "test.zip",
    "content": "UEsDBAoAAAAAAA..."  # base64 del ZIP
  }'

# Test 3: Listar archivos
curl https://TU-BACKEND.com/files
```

### 2. Probar n8n Webhook

```bash
# Test con curl
curl -X POST https://TU-N8N.com/webhook/dian-xml-process \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "factura.zip",
    "content": "UEsDBAoAAAAAAA..."
  }'
```

### 3. Probar Frontend
1. Abrir `https://TU-FRONTEND.com`
2. Seleccionar archivo ZIP con XMLs
3. Verificar que se sube correctamente
4. Verificar que se descarga el TXT

---

## Troubleshooting

### Error: CORS Blocked
**Solución:**
1. Verificar que el frontend esté en la lista `allowedOrigins` del webhook n8n
2. Verificar headers CORS en las respuestas
3. Agregar el dominio correcto en los 3 lugares del workflow

### Error: Backend no responde
**Solución:**
1. Verificar que el servicio esté corriendo
2. Revisar logs del servidor
3. Verificar URL y puerto correctos
4. Verificar firewall/seguridad

### Error: n8n no recibe datos
**Solución:**
1. Activar el workflow (toggle ON)
2. Verificar que el webhook esté en modo "Production"
3. Revisar logs de ejecución en n8n
4. Verificar formato del JSON enviado

### Error: Archivo no se descarga
**Solución:**
1. Verificar que `/save-txt` creó el archivo
2. Verificar permisos del directorio `temp_txt/`
3. Revisar URL de descarga en la respuesta
4. Verificar que el backend esté accesible públicamente

---

## Tabla de Configuración Rápida

| Componente | Servicio Sugerido | URL de Ejemplo | Variable de Entorno |
|------------|-------------------|----------------|---------------------|
| **Backend** | Render.com | `https://xml-processor.onrender.com` | N/A |
| **Frontend** | Vercel | `https://xml-upload.vercel.app` | `VITE_WEBHOOK_URL` |
| **n8n** | n8n Cloud | `https://empresa.app.n8n.cloud` | `WEBHOOK_URL` |

---

## Seguridad y Producción

### Recomendaciones:

1. **Autenticación**: Agregar API keys o JWT
2. **HTTPS**: Usar siempre SSL/TLS
3. **Rate Limiting**: Limitar requests por IP
4. **Validación**: Validar archivos antes de procesar
5. **Logs**: Implementar logging centralizado
6. **Backups**: Respaldar archivos generados
7. **Monitoreo**: Configurar alertas y uptime checks

### Variables de Entorno Recomendadas:

```bash
# Backend (.env)
PORT=8000
ALLOWED_ORIGINS=https://tu-frontend.com
TEMP_DIR=temp_txt
MAX_FILE_SIZE=10485760  # 10MB

# Frontend (.env)
VITE_WEBHOOK_URL=https://tu-n8n.com/webhook/dian-xml-process
VITE_API_URL=https://tu-backend.com

# n8n
WEBHOOK_URL=https://tu-n8n.com
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=tu-password-seguro
```

## Notas Importantes

- **CRÍTICO**: Actualizar TODAS las URLs antes de hacer pruebas
- **CORS**: Debe estar configurado en backend y n8n
- **Archivos**: El backend guarda archivos en `temp_txt/` (crear si no existe)
- **Seguridad**: Las URLs actuales ya no funcionan por suscripciones vencidas
- **Costos**: Considerar planes free vs paid según volumen

---

