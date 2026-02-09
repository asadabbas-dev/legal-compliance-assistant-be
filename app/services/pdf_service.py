from pathlib import Path

from pypdf import PdfReader


def extract_text_from_pdf(file_path: Path) -> list[tuple[str, int]]:
    """Extract text from PDF, returning list of (text, page_number)."""
    reader = PdfReader(str(file_path))
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            pages.append((text.strip(), i + 1))
    return pages


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
    return chunks
