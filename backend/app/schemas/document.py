# app/schemas/document.py
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    filename: str
    status: str
    owner_id: int

    class Config:
        from_attributes = True  # Pydantic v2; use orm_mode = True if you're on v1


class DocumentSearchResult(BaseModel):
    id: int
    filename: str
    snippet: str


class DocumentURLResponse(BaseModel):
    id: int
    filename: str
    url: str