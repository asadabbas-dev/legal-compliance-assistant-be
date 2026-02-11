"""Text extraction for PDF/DOCX."""

from pathlib import Path

from pypdf import PdfReader


def extract_pdf(file_path: Path) -> list[tuple[str, int]]:
    pages: list[tuple[str, int]] = []
    reader = PdfReader(str(file_path))
    for idx, page in enumerate(reader.pages, start=1):
        txt = (page.extract_text() or "").strip()
        if txt:
            pages.append((txt, idx))
    return pages


def extract_docx(file_path: Path) -> list[tuple[str, int]]:
    from docx import Document as DocxDocument

    document = DocxDocument(str(file_path))
    paragraphs = [p.text.strip() for p in document.paragraphs if p.text and p.text.strip()]
    if not paragraphs:
        return []
    return [("\n\n".join(paragraphs), 1)]


def extract_text(file_path: Path, file_type: str) -> list[tuple[str, int]]:
    ft = (file_type or "").lower()
    suffix = file_path.suffix.lower()
    if "docx" in ft or suffix == ".docx":
        return extract_docx(file_path)
    return extract_pdf(file_path)
