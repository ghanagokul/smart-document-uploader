import io
from unittest.mock import patch, MagicMock

import pytest
from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas

from app.utils.extraction import extract_text


def make_test_image_bytes(text: str) -> bytes:
    """Renders real text onto a real PNG image, for genuine OCR testing."""
    img = Image.new("RGB", (400, 100), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((10, 40), text, fill="black")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def make_test_pdf_bytes(text: str) -> bytes:
    """Renders real text into a real single-page PDF, for genuine OCR testing."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(72, 700, text)
    c.save()
    return buf.getvalue()


def mock_s3_get_object(file_bytes: bytes):
    """Builds a fake boto3 get_object() response shaped like the real one,
    so extract_text's `obj["Body"].read()` call works unmodified."""
    mock_body = MagicMock()
    mock_body.read.return_value = file_bytes
    return {"Body": mock_body}


@patch("app.utils.extraction.s3_client")
def test_extract_text_from_txt_file(mock_s3):
    mock_s3.get_object.return_value = mock_s3_get_object(b"Hello FastAPI world")

    result = extract_text("documents/user-1/notes.txt")

    assert result == "Hello FastAPI world"
    mock_s3.get_object.assert_called_once()


@patch("app.utils.extraction.s3_client")
def test_extract_text_from_image_file_real_ocr(mock_s3):
    image_bytes = make_test_image_bytes("HELLO OCR TEST")
    mock_s3.get_object.return_value = mock_s3_get_object(image_bytes)

    result = extract_text("documents/user-1/scan.png")

    assert "HELLO" in result.upper()


@patch("app.utils.extraction.s3_client")
def test_extract_text_from_pdf_file_real_ocr(mock_s3):
    pdf_bytes = make_test_pdf_bytes("QUARTERLY REPORT INVOICE")
    mock_s3.get_object.return_value = mock_s3_get_object(pdf_bytes)

    result = extract_text("documents/user-1/report.pdf")

    assert "QUARTERLY" in result.upper() or "REPORT" in result.upper()


@patch("app.utils.extraction.s3_client")
def test_extract_text_empty_txt_file(mock_s3):
    mock_s3.get_object.return_value = mock_s3_get_object(b"")

    result = extract_text("documents/user-1/empty.txt")

    assert result == ""


@patch("app.utils.extraction.s3_client")
def test_extract_text_jpeg_extension_also_supported(mock_s3):
    image_bytes = make_test_image_bytes("JPEG TEST")
    mock_s3.get_object.return_value = mock_s3_get_object(image_bytes)

    result = extract_text("documents/user-1/scan.jpeg")

    assert "JPEG" in result.upper() or "TEST" in result.upper()


@patch("app.utils.extraction.s3_client")
def test_extract_text_doc_file_misparsed_as_image_raises(mock_s3):
    """Your current extract_text has no .doc branch -- it falls through to
    the image path and PIL will fail to open non-image bytes as a picture.
    This documents that known limitation rather than hiding it."""
    mock_s3.get_object.return_value = mock_s3_get_object(b"fake legacy word doc bytes, not an image")

    with pytest.raises(Exception):
        extract_text("documents/user-1/resume.doc")