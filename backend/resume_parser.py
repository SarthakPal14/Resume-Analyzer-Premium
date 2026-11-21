"""Safe PDF text extraction."""
from io import BytesIO
import fitz

MAX_PDF_MB = 10
MAX_PAGES = 20


class ResumeParseError(ValueError):
    pass


def extract_resume_text(pdf_bytes: bytes) -> str:
    if not pdf_bytes:
        raise ResumeParseError("The uploaded file is empty.")
    if len(pdf_bytes) > MAX_PDF_MB * 1024 * 1024:
        raise ResumeParseError(f"Please upload a PDF smaller than {MAX_PDF_MB} MB.")

    try:
        with fitz.open(stream=BytesIO(pdf_bytes), filetype="pdf") as doc:
            if doc.is_encrypted:
                raise ResumeParseError("This PDF is password-protected. Upload an unlocked PDF.")
            if len(doc) > MAX_PAGES:
                raise ResumeParseError(f"Please upload a resume with {MAX_PAGES} pages or fewer.")
            text = "\n".join(page.get_text("text") for page in doc)
    except ResumeParseError:
        raise
    except Exception as exc:
        raise ResumeParseError("We could not read this PDF. Please check that it is valid.") from exc

    cleaned = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if len(cleaned) < 80:
        raise ResumeParseError(
            "Very little selectable text was found. This may be a scanned PDF; run OCR first "
            "or upload a text-based PDF."
        )
    return cleaned[:30000]
