from __future__ import annotations

from pathlib import Path
from typing import Any

from pypdf import PdfReader


def parse_pdf(
    file_path: str | Path,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[dict[str, Any]]:
    """
    Parse PDF file and split into chunks.

    Args:
        file_path: Path to PDF file
        chunk_size: Size of each chunk in characters
        chunk_overlap: Overlap between chunks in characters

    Returns:
        List of document chunks with text and metadata
    """
    reader = PdfReader(str(file_path))
    chunks: list[dict[str, Any]] = []

    # Extract text from all pages
    full_text = ""
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if text.strip():
            full_text += f"\n\n--- Page {page_num} ---\n\n{text}"

    if not full_text.strip():
        return []

    # Split into chunks with overlap
    start = 0
    chunk_index = 0
    while start < len(full_text):
        end = start + chunk_size
        chunk_text = full_text[start:end].strip()

        if chunk_text:
            # Estimate page number from position
            estimated_page = (start // chunk_size) + 1

            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "source": Path(file_path).name,
                    "chunk_index": str(chunk_index),
                    "estimated_page": str(estimated_page),
                },
            })
            chunk_index += 1

        # Move start position with overlap
        start = end - chunk_overlap
        if start >= len(full_text):
            break

    return chunks



