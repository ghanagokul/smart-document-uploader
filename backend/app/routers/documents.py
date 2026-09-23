from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db,SessionLocal
from app.dependencies import get_current_user
from app.models.user import User
from app.models.document import Document, DocumentStatus
from app.schemas.document import DocumentResponse, DocumentSearchResult, DocumentURLResponse,DocumentStatusResponse
from app.utils.extraction import extract_text
from app.utils.s3 import upload_file_to_s3, generate_presigned_url

import uuid

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

def process_document_locally(document_id: str, s3_key: str):
   
    db = SessionLocal()
    try:
        text = extract_text(s3_key)
        doc = db.query(Document).filter(Document.id == document_id).first()
        if doc:
            doc.content_text = text
            doc.status = DocumentStatus.COMPLETED
            db.commit()
    except Exception as e:
        print(f"Extraction failed for {document_id}: {e}")
        doc = db.query(Document).filter(Document.id == document_id).first()
        if doc:
            doc.status = DocumentStatus.FAILED
            db.commit()
    finally:
        db.close()


@router.post("", response_model=DocumentResponse, status_code=201)
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    s3_key = f"documents/{current_user.id}/{uuid.uuid4()}_{file.filename}"

    upload_file_to_s3(file.file, s3_key)

    new_doc = Document(
        filename=file.filename,
        s3_key=s3_key,
        status=DocumentStatus.PENDING,
        owner_id=current_user.id
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    background_tasks.add_task(process_document_locally, new_doc.id, s3_key)
    
    return new_doc

@router.get("", response_model=list[DocumentSearchResult])
def search_documents(
    q: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    results = db.query(Document).filter(
        Document.owner_id == current_user.id,
        Document.status == DocumentStatus.COMPLETED,
        Document.content_text.ilike(f"%{q}%")
    ).all()

    return [
        DocumentSearchResult(id=doc.id, filename=doc.filename, snippet=(doc.content_text or "")[:200])
        for doc in results
    ]
@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
def get_document_status(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()

    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    return DocumentStatusResponse(id=doc.id, status=doc.status)

@router.get("/{document_id}/url", response_model=DocumentURLResponse)
def get_document_url(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()

    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    url = generate_presigned_url(doc.s3_key, doc.filename)

    return DocumentURLResponse(id=doc.id, filename=doc.filename, url=url)

