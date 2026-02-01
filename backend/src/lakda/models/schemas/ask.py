from pydantic import BaseModel, Field
from typing import List, Optional

class AskRequest(BaseModel):
    id: str = Field(..., description="Unique identifier for the ask request")
    text: str = Field(..., description="The question text to be interpreted")
    timestamp: Optional[str] = Field(None, description="Timestamp of the request")

class InterpretationResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the interpretation response")
    question_id: str = Field(..., description="Identifier of the original question")
    original_question: str = Field(..., description="The original question text")
    interpreted_query: str = Field(..., description="The interpreted query text")
    keywords: List[str] = Field(..., description="List of keywords extracted from the question")
    intent: str = Field(..., description="The intent behind the question")
    timestamp: Optional[str] = Field(None, description="Timestamp of the interpretation response")
    confidence_score: Optional[float] = Field(None, description="Confidence score of the interpretation")
