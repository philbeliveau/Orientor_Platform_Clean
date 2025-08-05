from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReflectionQuestionBase(BaseModel):
    id: int
    question: str
    category: str

class ReflectionResponseBase(BaseModel):
    question_id: int
    response: Optional[str] = None

class ReflectionResponseCreate(ReflectionResponseBase):
    pass

class ReflectionResponseUpdate(BaseModel):
    response: Optional[str] = None

class ReflectionResponseBatch(BaseModel):
    responses: list[ReflectionResponseCreate]

class ReflectionResponse(ReflectionResponseBase):
    id: int
    user_id: int
    prompt_text: str
    response_time_ms: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ReflectionResponseWithQuestion(ReflectionResponse):
    question: ReflectionQuestionBase

    class Config:
        from_attributes = True