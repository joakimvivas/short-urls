# app/models.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import uuid4

class URL(BaseModel):
    id: str = str(uuid4())  # Genera un UUID único para cada instancia
    original_url: str
    short_name: str
    description: Optional[str] = None
    created_by: str
    expirable: bool
    created_at: Optional[datetime] = None  # Optional for edit_url

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }