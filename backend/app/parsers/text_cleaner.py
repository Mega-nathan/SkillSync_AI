import re
from typing import List


def clean_text(text: str) -> str:
	if not text:
		return ""
	# normalize whitespace
	text = re.sub(r"\s+", " ", text)
	# remove non-printable
	text = re.sub(r"[^\x20-\x7E\n]", "", text)
	return text.strip()


def split_sentences(text: str) -> List[str]:
	# naive sentence split
	parts = re.split(r"(?<=[.!?])\s+", text)
	return [p.strip() for p in parts if p.strip()]
