from fastapi import APIRouter, UploadFile, File, HTTPException
import io
from pypdf import PdfReader

router = APIRouter(prefix="/pdf", tags=["PDF Tools"])

@router.post("/extract-text")
async def extract_pdf_text(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    contents = await file.read()
    reader = PdfReader(io.BytesIO(contents))
    text = "".join([page.extract_text() or "" for page in reader.pages])

    return {
        "filename": file.filename,
        "total_pages": len(reader.pages),
        "text": text
    }
  
