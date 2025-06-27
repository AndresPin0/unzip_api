from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
import base64, zipfile, io, re
import chardet, xmltodict

app = FastAPI()

def bytes_to_xml_str(raw: bytes) -> str:
    """
    Devuelve el contenido XML como str
    detectando la codificación declarada o, si falta,
    usando chardet como respaldo.
    """
    if raw.startswith(b'\xef\xbb\xbf'):
        raw = raw[3:]
    header = raw[:200].decode('ascii', errors='ignore')
    m = re.search(r'encoding=[\'"]([^\'"]+)[\'"]', header, re.I)
    if m:
        encoding = m.group(1).lower()
    else:
        encoding = chardet.detect(raw)['encoding'] or 'utf-8'

    try:
        return raw.decode(encoding, errors='strict')
    except UnicodeDecodeError:
        return raw.decode(encoding, errors='replace')

@app.post("/unzip-xml")
async def unzip_xml(
    filename: str = Body(...),
    content: str = Body(...)
):
    try:
        zip_bytes = base64.b64decode(content)
        zip_file  = zipfile.ZipFile(io.BytesIO(zip_bytes))

        extracted = []
        for fname in zip_file.namelist():
            if not fname.lower().endswith(".xml"):
                continue

            raw_bytes = zip_file.read(fname)
            xml_str   = bytes_to_xml_str(raw_bytes)
            data_dict = xmltodict.parse(xml_str)

            extracted.append({"filename": fname, "content": data_dict})

        if not extracted:
            return JSONResponse(status_code=400,
                                content={"error": "No se encontró XML válido en el ZIP"})

        return {"status": "ok", "data": extracted}

    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
