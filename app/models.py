# app/models.py
from pydantic import BaseModel
from typing import Optional

class URL(BaseModel):
    id: int
    original_url: str
    short_name: str
    description: Optional[str] = None
    created_by: str
