# unzip_api.py
from fastapi import FastAPI, File, UploadFile
import zipfile, io

app = FastAPI()

@app.post("/unzip-xml")
async def unzip_and_return_xml(file: UploadFile = File(...)):
    contents = await file.read()
    with zipfile.ZipFile(io.BytesIO(contents)) as zf:
        # Suponemos que solo hay 1 XML dentro
        xml_name = [f for f in zf.namelist() if f.endswith(".xml")][0]
        with zf.open(xml_name) as xml_file:
            xml_content = xml_file.read().decode("utf-8")
    return {"xml": xml_content}