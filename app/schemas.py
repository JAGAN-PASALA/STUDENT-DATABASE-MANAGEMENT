from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class StudentBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50, example="Alex")
    last_name: str = Field(..., min_length=1, max_length=50, example="Johnson")
    email: str = Field(..., min_length=3, max_length=100, example="alex.johnson@example.edu")
    major: str = Field(..., example="Computer Science")
    gpa: float = Field(..., ge=0.0, le=4.0, example=3.75)
    enrollment_year: int = Field(..., ge=1900, le=2100, example=2024)

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[str] = None
    major: Optional[str] = None
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    enrollment_year: Optional[int] = Field(None, ge=1900, le=2100)

class StudentResponse(StudentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ChatQueryRequest(BaseModel):
    query: str = Field(..., example="How many students are enrolled in Computer Science?")

class ChatQueryResponse(BaseModel):
    query: str
