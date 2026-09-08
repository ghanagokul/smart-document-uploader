from unittest.mock import patch
from tests.conftest import client, create_test_user, TestingSessionLocal, auth_user, no_auth
from app.models.document import Document, DocumentStatus


# ==========================================================================
# UPLOAD -- file presence
# ==========================================================================

@patch("app.routers.documents.upload_file_to_s3")
def test_upload_with_file_succeeds(mock_upload, auth_user):
    files = {"file": ("test.txt", b"hello world", "text/plain")}
    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 201
    mock_upload.assert_called_once()


def test_upload_without_file_returns_422(auth_user):
    response = client.post("/api/v1/documents/upload")
    assert response.status_code == 422


# ==========================================================================
# UPLOAD -- authorization
# ==========================================================================

@patch("app.routers.documents.upload_file_to_s3")
def test_upload_with_authorization_succeeds(mock_upload, auth_user):
    files = {"file": ("test.txt", b"hello world", "text/plain")}
    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 201


def test_upload_without_authorization_rejected(no_auth):
    files = {"file": ("test.txt", b"hello world", "text/plain")}
    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code in (401, 403)


# ==========================================================================
# UPLOAD -- file formats
# ==========================================================================

@patch("app.routers.documents.upload_file_to_s3")
def test_upload_txt_file(mock_upload, auth_user):
    files = {"file": ("notes.txt", b"plain text content", "text/plain")}
    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 201
    assert response.json()["filename"] == "notes.txt"


@patch("app.routers.documents.upload_file_to_s3")
def test_upload_pdf_file(mock_upload, auth_user):
    fake_pdf_bytes = b"%PDF-1.4 fake content"
    files = {"file": ("document.pdf", fake_pdf_bytes, "application/pdf")}
    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 201
    assert response.json()["filename"] == "document.pdf"


@patch("app.routers.documents.upload_file_to_s3")
def test_upload_image_file(mock_upload, auth_user):
    fake_image_bytes = b"\x89PNG\r\n\x1a\n fake image content"
    files = {"file": ("scan.png", fake_image_bytes, "image/png")}
    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 201
    assert response.json()["filename"] == "scan.png"


@patch("app.routers.documents.upload_file_to_s3")
def test_upload_doc_file(mock_upload, auth_user):
    fake_doc_bytes = b"fake legacy word doc bytes"
    files = {"file": ("resume.doc", fake_doc_bytes, "application/msword")}
    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 201
    assert response.json()["filename"] == "resume.doc"


@patch("app.routers.documents.upload_file_to_s3")
def test_upload_docx_file(mock_upload, auth_user):
    fake_docx_bytes = b"fake docx bytes"
    files = {"file": ("resume.docx", fake_docx_bytes,
                       "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 201
    assert response.json()["filename"] == "resume.docx"


# ==========================================================================
# SEARCH -- query length boundary
# ==========================================================================

def test_search_query_length_exactly_min_length_1(auth_user):
    response = client.get("/api/v1/documents/search", params={"q": "a"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_search_query_length_zero_fails_validation(auth_user):
    response = client.get("/api/v1/documents/search", params={"q": ""})
    assert response.status_code == 422


def test_search_query_length_more_than_one_char(auth_user):
    with TestingSessionLocal() as db:
        db.add(Document(
            filename="report.txt",
            s3_key=f"documents/{auth_user.id}/report.txt",
            status=DocumentStatus.COMPLETED,
            owner_id=auth_user.id,
            content_text="Quarterly revenue report for FastAPI project.",
        ))
        db.commit()

    response = client.get("/api/v1/documents/search", params={"q": "FastAPI"})
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["filename"] == "report.txt"


def test_search_query_missing_param_fails_validation(auth_user):
    response = client.get("/api/v1/documents/search")
    assert response.status_code == 422


# ==========================================================================
# SEARCH -- authorization
# ==========================================================================

def test_search_with_authorization_succeeds(auth_user):
    response = client.get("/api/v1/documents/search", params={"q": "test"})
    assert response.status_code == 200


def test_search_without_authorization_rejected(no_auth):
    response = client.get("/api/v1/documents/search", params={"q": "test"})
    assert response.status_code in (401, 403)


# ==========================================================================
# SEARCH -- tenant isolation / status filtering (bonus coverage)
# ==========================================================================

def test_search_excludes_other_users_documents(auth_user):
    with TestingSessionLocal() as db:
        other_user = create_test_user(db, email="someone-else@example.com")
        db.add(Document(
            filename="secret.txt",
            s3_key=f"documents/{other_user.id}/secret.txt",
            status=DocumentStatus.COMPLETED,
            owner_id=other_user.id,
            content_text="This also mentions FastAPI but isn't yours.",
        ))
        db.commit()

    response = client.get("/api/v1/documents/search", params={"q": "FastAPI"})
    assert response.status_code == 200
    assert response.json() == []


def test_search_excludes_pending_documents(auth_user):
    with TestingSessionLocal() as db:
        db.add(Document(
            filename="draft.txt",
            s3_key=f"documents/{auth_user.id}/draft.txt",
            status=DocumentStatus.PENDING,
            owner_id=auth_user.id,
            content_text="FastAPI content still being processed.",
        ))
        db.commit()

    response = client.get("/api/v1/documents/search", params={"q": "FastAPI"})
    assert response.status_code == 200
    assert response.json() == []


# ==========================================================================
# GET DOCUMENT URL -- authorization
# ==========================================================================

@patch("app.routers.documents.generate_presigned_url")
def test_get_document_url_with_authorization_succeeds(mock_presigned, auth_user):
    mock_presigned.return_value = "https://fake-bucket.s3.amazonaws.com/signed"

    with TestingSessionLocal() as db:
        doc = Document(
            filename="listed.pdf",
            s3_key=f"documents/{auth_user.id}/listed.pdf",
            status=DocumentStatus.COMPLETED,
            owner_id=auth_user.id,
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        doc_id = doc.id

    response = client.get(f"/api/v1/documents/{doc_id}/url")
    assert response.status_code == 200
    assert response.json()["url"] == "https://fake-bucket.s3.amazonaws.com/signed"


def test_get_document_url_without_authorization_rejected(no_auth):
    response = client.get("/api/v1/documents/some-id/url")
    assert response.status_code in (401, 403)


# ==========================================================================
# GET DOCUMENT URL -- existing vs non-existing document
# ==========================================================================

@patch("app.routers.documents.generate_presigned_url")
def test_get_document_url_for_listed_document(mock_presigned, auth_user):
    mock_presigned.return_value = "https://fake-bucket.s3.amazonaws.com/signed"

    with TestingSessionLocal() as db:
        doc = Document(
            filename="existing.pdf",
            s3_key=f"documents/{auth_user.id}/existing.pdf",
            status=DocumentStatus.COMPLETED,
            owner_id=auth_user.id,
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        doc_id = doc.id

    response = client.get(f"/api/v1/documents/{doc_id}/url")
    assert response.status_code == 200
    assert response.json()["id"] == doc_id


def test_get_document_url_for_unlisted_nonexistent_document(auth_user):
    response = client.get("/api/v1/documents/does-not-exist-id/url")
    assert response.status_code == 404


def test_get_document_url_for_another_users_document_returns_404(auth_user):
    with TestingSessionLocal() as db:
        other_user = create_test_user(db, email="someone-else@example.com")
        doc = Document(
            filename="not-mine.pdf",
            s3_key=f"documents/{other_user.id}/not-mine.pdf",
            status=DocumentStatus.COMPLETED,
            owner_id=other_user.id,
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        doc_id = doc.id

    response = client.get(f"/api/v1/documents/{doc_id}/url")
    assert response.status_code == 404