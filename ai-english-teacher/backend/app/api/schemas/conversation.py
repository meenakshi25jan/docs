from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ConversationRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    mode: Literal["grammar", "conversation"] = "grammar"


class GrammarCorrectionResult(BaseModel):
    original_text: str
    corrected_text: str
    explanation: str
    mistakes: list[str]
    score: int
    teacher_response: str


class VoiceOutput(BaseModel):
    voice: str
    voice_name: str | None = None
    text: str
    audio_base64: str | None = None
    audio_mime_type: str | None = None


class ConversationResponse(BaseModel):
    input_type: Literal["text", "audio"]
    mode: str
    result: GrammarCorrectionResult
    voice_output: VoiceOutput
    feedback_id: UUID | None = None


class AudioConversationResponse(ConversationResponse):
    transcribed_text: str


class BandScoreResponse(BaseModel):
    grammar_score: int
    estimated_cefr: str
    estimated_ielts_band: float
    note: str


class FeedbackItem(BaseModel):
    id: UUID
    original_text: str
    corrected_text: str
    explanation: str
    teacher_response: str
    mistake_type: str | None
    score: int
    mode: str
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedbackListResponse(BaseModel):
    items: list[FeedbackItem]
    count: int
