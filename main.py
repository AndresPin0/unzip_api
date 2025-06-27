from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
import base64
import zipfile
import io
import xmltodict

app = FastAPI()

@app.post("/unzip-xml")
async def unzip_xml(
    filename: str = Body(...),
    content: str = Body(...)
):
    try:
        zip_bytes = base64.b64decode(content)
        zip_file = zipfile.ZipFile(io.BytesIO(zip_bytes))
        extracted_data = []
        for file in zip_file.namelist():
            if file.lower().endswith(".xml"):
                raw_bytes = zip_file.read(file)
                json_data = xmltodict.parse(raw_bytes)
                extracted_data.append({
                    "filename": file,
                    "content": json_data
                })

        return {"status": "ok", "data": extracted_data}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
