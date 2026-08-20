"""Document loaders for PDF, DOCX, and plain TXT/MD files."""

import re
from pathlib import Path

from pypdf import PdfReader
from docx import Document


def _clean_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join(lines).strip()


def load_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return _clean_text("\n".join(pages))


def load_docx(file_path: str) -> str:
    document = Document(file_path)
    paragraphs = [p.text for p in document.paragraphs]
    return _clean_text("\n".join(paragraphs))


def load_text(file_path: str) -> str:
    text = Path(file_path).read_text(encoding="utf-8")
    return _clean_text(text)


_LOADERS = {
    ".pdf": load_pdf,
    ".docx": load_docx,
    ".txt": load_text,
    ".md": load_text,
}


def load_document(file_path: str) -> str:
    extension = Path(file_path).suffix.lower()
    loader = _LOADERS.get(extension)
    if loader is None:
        raise ValueError(
            f"Unsupported file type '{extension}'. Supported types: "
            f"{', '.join(sorted(_LOADERS))}"
        )
    return loader(file_path)
