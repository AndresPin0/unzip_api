# Unzip API - Procesador de Archivos XML

## Descripción

API REST desarrollada con FastAPI para el procesamiento automatizado de archivos ZIP que contienen documentos XML, especialmente diseñada para el manejo de documentos de facturación electrónica y documentos fiscales. La API extrae, parsea y convierte archivos XML a formato JSON para su fácil integración con sistemas web.

## Características Principales

-  **Procesamiento de ZIP**: Extrae automáticamente archivos XML de archivos ZIP codificados en base64
-  **Detección Inteligente de Encoding**: Reconoce automáticamente la codificación de caracteres de los archivos XML
-  **Manejo de CDATA**: Procesa contenido XML embebido en secciones CDATA
-  **Documentos AttachedDocument**: Soporte especializado para documentos de facturación electrónica
-  **Gestión de Archivos**: Sistema completo de guardado, descarga y eliminación de archivos TXT
-  **API RESTful**: Endpoints bien estructurados con documentación automática
-  **CORS Habilitado**: Acceso desde cualquier origen para integración frontend
-  **Logging Detallado**: Registro completo de operaciones para debugging y monitoreo

##  Tecnologías Utilizadas

- **FastAPI** - Framework web moderno para Python
- **Uvicorn** - Servidor ASGI de alto rendimiento
- **xmltodict** - Conversión eficiente de XML a diccionarios Python
- **chardet** - Detección automática de codificación de caracteres
- **python-multipart** - Manejo de formularios y body requests

##  Instalación

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Instalación Local

1. **Clonar o descargar el proyecto**
   ```bash
   git clone <repository-url>
   cd unzip_api
   
   # O simplemente navega al directorio del proyecto
   cd unzip_api
   ```

2. **Crear entorno virtual (recomendado)**
   ```bash
   python -m venv venv
   
   # En Windows
   venv\Scripts\activate
   
   # En macOS/Linux
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Verificar instalación**
   - Abrir navegador en: `http://localhost:8000`
   - Documentación automática: `http://localhost:8000/docs`
   - Documentación alternativa: `http://localhost:8000/redoc`

##  Despliegue en Producción

### Despliegue en Render.com (Recomendado)

El proyecto incluye configuración para despliegue automático en Render.com:

1. **Crear cuenta en Render.com**
   - Registrarse en [render.com](https://render.com)

2. **Conectar repositorio**
   - Crear nuevo "Web Service"
   - Conectar repositorio de GitHub/GitLab
   - Seleccionar rama principal

3. **Configuración automática**
   - Render detectará automáticamente el `render.yaml`
   - Configuración incluida:
     - Runtime: Python
     - Puerto: 10000
     - Comando de inicio: `uvicorn main:app --host 0.0.0.0 --port 10000`
     - Plan: Free

4. **Deploy**
   - Render desplegará automáticamente
   - URL pública será proporcionada

### Despliegue Manual en Servidor

```bash
# Instalar dependencias del sistema
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Configurar aplicación
git clone <repository-url>
cd unzip_api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Ejecutar con Gunicorn (producción)
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Variables de Entorno (Opcional)

```bash
# Crear archivo .env si necesitas configuraciones específicas
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO
```

##  Documentación de la API

### Endpoints Principales

#### 1. Procesar ZIP con XML
```http
POST /unzip-xml
Content-Type: application/json

{
    "filename": "documento.zip",
    "content": "UEsDBAoAAAAAAA..." // base64 encoded ZIP
}
```

**Respuesta:**
```json
{
    "status": "ok",
    "data": [
        {
            "filename": "factura.xml",
            "content": {
                // Contenido XML convertido a JSON
            }
        }
    ]
}
```

#### 2. Guardar archivo TXT
```http
POST /save-txt
Content-Type: application/json

{
    "filename": "documento.txt",
    "content": "Contenido del archivo..."
}
```

#### 3. Listar archivos
```http
GET /files
```

#### 4. Descargar archivo
```http
GET /download/{filename}
```

#### 5. Eliminar archivo
```http
DELETE /files/{filename}
```

## 🔧 Configuración

### Estructura de Directorios

```
unzip_api/
├── main.py              # Código principal de la API
├── requirements.txt     # Dependencias Python
├── render.yaml         # Configuración de despliegue Render
├── README.md           # Este archivo
└── temp_txt/           # Directorio temporal (se crea automáticamente)
```

### Configuraciones Importantes

- **Puerto por defecto**: 8000 (local), 10000 (Render)
- **CORS**: Habilitado para todos los orígenes
- **Directorio temporal**: `temp_txt/` para archivos generados
- **Logging**: Nivel INFO por defecto

##  Casos de Uso

### 1. Procesamiento de Facturas Electrónicas
```python
import requests
import base64

# Leer archivo ZIP
with open('facturas.zip', 'rb') as f:
    zip_content = base64.b64encode(f.read()).decode()

# Enviar a API
response = requests.post('http://localhost:8000/unzip-xml', json={
    'filename': 'facturas.zip',
    'content': zip_content
})

facturas = response.json()['data']
```

### 2. Integración con Frontend
```javascript
// JavaScript/TypeScript
const processZip = async (file) => {
    const base64 = await fileToBase64(file);
    
    const response = await fetch('/unzip-xml', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            filename: file.name,
            content: base64
        })
    });
    
    return await response.json();
};
```

##  Troubleshooting

### Problemas Comunes

1. **Error de encoding**
   - La API detecta automáticamente el encoding
   - Revisa los logs para detalles específicos

2. **Archivo ZIP corrupto**
   - Verifica que el archivo esté correctamente codificado en base64
   - Comprueba que el ZIP no esté dañado

3. **Puerto ocupado**
   ```bash
   # Cambiar puerto
   uvicorn main:app --port 8001
   ```

4. **Permisos de archivos**
   ```bash
   # Asegurar permisos correctos
   chmod 755 temp_txt/
   ```

### Logs y Debugging

Los logs incluyen información detallada sobre:
- Archivos recibidos y procesados
- Encoding detectado
- Errores de parsing
- Operaciones de archivos

Ejemplo de logs:
```
INFO: → Recibido ZIP factura.zip, 1024 bytes
INFO: factura.xml: encoding detectado = utf-8
INFO: factura.xml: Documento tipo AttachedDocument detectado
```

##  Consideraciones de Seguridad

- **Validación de archivos**: Solo procesa archivos XML dentro de ZIPs
- **Límites de tamaño**: Límite ajustado a la capacidad del servidor
- **Autenticación**: No implementada
- **Limpieza de archivos**: Función disponible para limpiar archivos temporales
