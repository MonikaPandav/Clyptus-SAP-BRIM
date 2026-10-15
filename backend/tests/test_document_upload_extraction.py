from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.schemas.message import DocumentAttachment, MessageCreate
from backend.app.services.document_extractor import extract_document
from backend.app.services.llm_service import LLMService
from backend.app.services.rag_service import RAGService


def _png_bytes():
    import io

    output = io.BytesIO()
    Image.new("RGB", (80, 40), "white").save(output, format="PNG")
    return output.getvalue()


def test_png_upload_ocr_text_becomes_llm_evidence():
    fake_output = SimpleNamespace(
        boxes=np.asarray([[[5, 5], [70, 5], [70, 20], [5, 20]]], dtype=float),
        txts=("Invoice total: 125.00",),
    )
    with patch("backend.app.services.document_extractor._get_ocr_engine", return_value=lambda _image: fake_output):
        extracted = extract_document("invoice.png", _png_bytes())

    attachment = DocumentAttachment(
        name=extracted["filename"],
        file_type=extracted["file_type"],
        size_bytes=extracted["size_bytes"],
        page_count=extracted["page_count"],
        text=extracted["text"],
    )
    passages = RAGService._attachment_passages("What is the invoice total?", [attachment.model_dump()])
    llm_context = LLMService._format_evidence_context(passages)

    assert extracted["file_type"] == "png"
    assert "Invoice total: 125.00" in extracted["text"]
    assert "125.00" in llm_context
    assert "Attached Document: invoice.png" in llm_context


def test_png_upload_endpoint_returns_ocr_content():
    fake_output = SimpleNamespace(
        boxes=np.asarray([[[5, 5], [70, 5], [70, 20], [5, 20]]], dtype=float),
        txts=("Invoice total: 125.00",),
    )
    client = TestClient(app)
    with patch("backend.app.services.document_extractor._get_ocr_engine", return_value=lambda _image: fake_output):
        response = client.post(
            "/api/chats/extract-document",
            files={"file": ("invoice.png", _png_bytes(), "image/png")},
        )

    assert response.status_code == 200, response.text
    assert response.json()["file_type"] == "png"
    assert "Invoice total: 125.00" in response.json()["text"]


def test_image_without_readable_text_and_invalid_png_fail_cleanly():
    with patch("backend.app.services.document_extractor._get_ocr_engine", return_value=lambda _image: None):
        with pytest.raises(ValueError, match="No readable text"):
            extract_document("empty.png", _png_bytes())
    with pytest.raises(ValueError, match="valid PNG"):
        extract_document("fake.png", b"not an image")


def test_attachment_payload_limits_and_supported_format_validation():
    with pytest.raises(ValueError):
        DocumentAttachment(name="empty.txt", text="")
    with pytest.raises(ValueError, match="Unsupported file format"):
        extract_document("legacy.doc", b"not supported")
    with pytest.raises(ValueError):
        MessageCreate(content="Question", attachments=[
            DocumentAttachment(name=f"{index}.txt", text="text") for index in range(6)
        ])

    extracted = extract_document("large.txt", ("SAP BRIM details. " * 10000).encode())
    assert extracted["char_count"] <= 150000
    assert len(extracted["text"]) <= 150000


def test_long_file_selects_question_relevant_text_instead_of_only_the_start():
    early = "Unrelated introductory notes about the project. " * 80
    target = "Order process status: the FAILED invoice transfer is waiting for reconciliation."
    passages = RAGService._attachment_passages(
        "Why did the invoice transfer fail?",
        [{"name": "operations.txt", "page_count": 1, "text": early + target}],
    )
    context = LLMService._format_evidence_context(passages)

    assert "FAILED invoice transfer" in context
