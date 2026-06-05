from typing import Optional

def extract_text_from_pdf(path_or_bytes) -> str:
	try:
		from PyPDF2 import PdfReader
	except Exception:
		return ""

	text = []
	try:
		if isinstance(path_or_bytes, (bytes, bytearray)):
			from io import BytesIO

			reader = PdfReader(BytesIO(path_or_bytes))
		else:
			reader = PdfReader(path_or_bytes)
		for p in reader.pages:
			page_text = p.extract_text() or ""
			text.append(page_text)
	except Exception:
		return ""
	return "\n".join(text)
