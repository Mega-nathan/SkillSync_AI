from fastapi import APIRouter, UploadFile, File, HTTPException
from ..parsers.text_cleaner import clean_text
from ..parsers.docx_parser import extract_text_from_docx
from ..parsers.pdf_parser import extract_text_from_pdf

router = APIRouter(prefix="/resume", tags=["resume"])

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
	content = await file.read()
	name = file.filename or "uploaded"
	if name.lower().endswith(".pdf"):
		txt = extract_text_from_pdf(content)
	elif name.lower().endswith(('.docx', '.doc')):
		txt = extract_text_from_docx(content)
	else:
		# assume plain text
		try:
			txt = content.decode('utf8')
		except Exception:
			txt = ""
	cleaned = clean_text(txt)
	if not cleaned:
		raise HTTPException(status_code=400, detail="Could not extract text from file")
	print(name)
	print(cleaned)
	return {"filename": name, "content": cleaned}
