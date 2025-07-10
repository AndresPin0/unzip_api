import base64, zipfile, io, re, chardet, xmltodict, binascii, logging
from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os, time
from datetime import datetime

TEMP_DIR = "temp_txt"

logging.basicConfig(level=logging.INFO)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def cleanup_temp_txt(hours=24):
    now = time.time()
    for f in os.listdir("temp_txt"):
        path = os.path.join("temp_txt", f)
        if os.path.isfile(path) and now - os.path.getmtime(path) > hours * 3600:
            os.remove(path)


def detect_encoding(raw: bytes) -> str:
    """Busca ‘encoding="..."’ o usa chardet."""
    header = raw[:300].decode("ascii", "ignore")
    m = re.search(r'encoding=[\'"]([^\'"]+)[\'"]', header, re.I)
    if m:
        return m.group(1).lower()
    return chardet.detect(raw)["encoding"] or "utf-8"

@app.post("/unzip-xml")
async def unzip_xml(
    filename: str = Body(...),
    content: str = Body(...)
):
    try:
        zip_bytes = base64.b64decode(content)
        z = zipfile.ZipFile(io.BytesIO(zip_bytes))

        logging.info(f"→ Recibido ZIP {filename}, {len(zip_bytes)} bytes")
        logging.info(f"   Contiene: {z.namelist()}")

        extracted = []
        for fname in z.namelist():
            if not fname.lower().endswith(".xml"):
                continue

            raw = z.read(fname)
            enc = detect_encoding(raw)
            xml_str = raw.decode(enc, errors="strict").lstrip("\ufeff")
            data = xmltodict.parse(xml_str)

            root = next(iter(data))

            if root == 'AttachedDocument':
                logging.info(f"{fname}: contenedor AttachedDocument detectado")
                try:
                    cdata_raw = data['AttachedDocument']['cac:Attachment']['cac:ExternalReference']['cbc:Description']
                    cdata_clean = re.sub(r'^<!\[CDATA\[|\]\]>$', '', cdata_raw.strip())
                    inner = xmltodict.parse(cdata_clean)
                    extracted.append({
                        "filename": fname,
                        "content": inner
                    })
                    continue
                except Exception as e:
                    logging.warning(f"{fname}: fallo extrayendo Invoice embebido → {e}")

            extracted.append({
                "filename": fname,
                "content": data
            })

        if not extracted:
            return JSONResponse(
                status_code=400,
                content={"error": "No se pudo parsear ningún XML. Verifica los logs."},
            )

        return {"status": "ok", "data": extracted}

    except Exception as e:
        logging.error(f"Error general unzip-xml: {e}")
        return JSONResponse(status_code=400, content={"error": str(e)})
        
os.makedirs(TEMP_DIR, exist_ok=True)

@app.post("/save-txt")
async def save_txt(
    filename: str = Body(...),
    content: str = Body(...)
):
    try:
        date_str     = datetime.now().strftime('%d-%m-%y')
        safe_filename = f"{date_str}.txt"
        filepath = os.path.join(TEMP_DIR, safe_filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        logging.info(f"Archivo TXT guardado en: {filepath}")

        return {
            "status": "ok",
            "download_url": f"/download/{safe_filename}",
            "filename": safe_filename
        }
    except Exception as e:
        logging.error(f"Error guardando archivo TXT: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/download/{filename}")
async def download_txt(filename: str):
    filepath = os.path.join(TEMP_DIR, filename)
    if not os.path.exists(filepath):
        return JSONResponse(status_code=404, content={"error": "Archivo no encontrado"})

    return FileResponse(filepath, media_type="text/plain", filename=filename)


@app.get("/files")
async def list_files():
    try:
        files = []
        for filename in os.listdir(TEMP_DIR):
            if filename.endswith('.txt'):
                filepath = os.path.join(TEMP_DIR, filename)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    files.append({
                        "filename": filename,
                        "download_url": f"/download/{filename}",
                        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "size_bytes": stat.st_size,
                        "size_mb": round(stat.st_size / (1024 * 1024), 2)
                    })
        
        files.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "status": "ok",
            "files": files,
            "total_files": len(files)
        }
        
    except Exception as e:
        logging.error(f"Error listando archivos: {e}")
        return JSONResponse(
            status_code=500, 
            content={"error": "Error al listar archivos"}
        )

@app.delete("/files/{filename}")
async def delete_file(filename: str):
    try:
        filepath = os.path.join(TEMP_DIR, filename)
        if not os.path.exists(filepath):
            return JSONResponse(
                status_code=404, 
                content={"error": "Archivo no encontrado"}
            )
        
        os.remove(filepath)
        logging.info(f"Archivo eliminado: {filename}")
        
        return {"status": "ok", "message": f"Archivo {filename} eliminado"}
        
    except Exception as e:
        logging.error(f"Error eliminando archivo {filename}: {e}")
        return JSONResponse(
            status_code=500, 
            content={"error": "Error al eliminar archivo"}
        ) 


