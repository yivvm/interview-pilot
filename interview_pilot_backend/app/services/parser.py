"""Resume text extraction.
Turns an uploaded resume (PDF or DOCX) into plain text for the LLM.
DOCX support is added in the next step.
"""

from io import BytesIO

from pypdf import PdfReader
from docx import Document

def extract_text_from_pdf(data: bytes) -> str:
    """Extract plain text from PDF file bytes.

    Args:
        data: Raw bytes of the uploaded PDF.
    
    Returns:
        The concatenated text of all pages, stripped of leading/trailing
        whitespace. Pages with no extractable text contribute nothing.
    """
    reader = PdfReader(BytesIO(data))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()

def extract_text_from_docx(data: bytes) -> str:
    """Extract plain text from DOCX file bytes.
    
    Reads every paragraph in document order and joins them with newlines.
    """
    document = Document(BytesIO(data))
    paragraphs = [para.text for para in document.paragraphs]
    return "\n".join(paragraphs).strip()

def extract_text(filename: str, data: bytes) -> str:
    """Dispatch to the right extractor based on the file extension.
    
    Args:
        filename: Original upload name, used only to read the extension.
        data: Raw file bytes.
    
    Returns:
        Extracted plain text.
    
    Raises:
        ValueError: If the extension is not .pdf or .docx.
    """
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return extract_text_from_pdf(data)
    if lower.endswith(".docx"):
        return extract_text_from_docx(data)
    raise ValueError(f"Unsupported file type: {filename!r}. Use PDF or DOCX.")