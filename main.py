import base64, zipfile, io, re, chardet, xmltodict, binascii, logging
from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
app = FastAPI()


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
        z        = zipfile.ZipFile(io.BytesIO(zip_bytes))

        logging.info(f"→ Recibido ZIP {filename}, {len(zip_bytes)} bytes")
        logging.info(f"   Contiene: {z.namelist()}")

        extracted = []
        for fname in z.namelist():
            if not fname.lower().endswith(".xml"):
                continue

            raw = z.read(fname)

            logging.info(f"{fname}: primeros 16 bytes = {binascii.hexlify(raw[:16])}")

            enc = detect_encoding(raw)
            logging.info(f"{fname}: encoding detectado = {enc}")

            try:
                xml_str = raw.decode(enc, errors="strict").lstrip("\ufeff")
                data    = xmltodict.parse(xml_str)
                extracted.append({"filename": fname, "content": data})
            except Exception as e:
                logging.error(f"{fname}: error al parsear → {e}")
                continue

        if not extracted:
            return JSONResponse(
                status_code=400,
                content={"error": "No se pudo parsear ningún XML. Revisa los logs."},
            )

        return {"status": "ok", "data": extracted}

    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
