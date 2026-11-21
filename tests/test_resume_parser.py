import fitz
import pytest
from backend.resume_parser import extract_resume_text, ResumeParseError


def make_pdf(text="Sarthak Pal\nPython C++ Machine Learning\nEducation and projects " * 5):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    data = doc.tobytes()
    doc.close()
    return data


def test_extract_text_from_valid_pdf():
    text = extract_resume_text(make_pdf())
    assert "Sarthak Pal" in text
    assert "Python" in text


def test_reject_empty_pdf_bytes():
    with pytest.raises(ResumeParseError):
        extract_resume_text(b"")


def test_reject_non_pdf():
    with pytest.raises(ResumeParseError):
        extract_resume_text(b"not a pdf")
