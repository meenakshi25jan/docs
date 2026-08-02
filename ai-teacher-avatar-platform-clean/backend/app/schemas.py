from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    display_name: str = ""


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    display_name: str
    voice_pref: str


class VoicePrefRequest(BaseModel):
    voice_pref: Literal["male", "female"]


class AgentMessageRequest(BaseModel):
    mode: Literal["grammar", "conversation", "assessment"]
    text: str = Field(min_length=1, max_length=2000)
    session_id: Optional[str] = None


class AgentMessageResponse(BaseModel):
    session_id: str
    reply_text: str          # what the teacher should SAY (spoken back via TTS)
    correction: str = ""     # short written correction, if any
    level: Optional[int] = None
    band_score: Optional[float] = None
    details: Optional[dict] = None


class GrammarNextResponse(BaseModel):
    level: int
    exercise: str


# --- Student profile memory --------------------------------------------

class StudentProfileRequest(BaseModel):
    level: Literal["Beginner", "Intermediate", "Advanced"] = "Intermediate"
    target_band: Optional[float] = Field(default=None, ge=1.0, le=9.0)
    native_language: str = ""
    weaknesses: list[str] = Field(default_factory=list, max_length=10)


class StudentProfileResponse(BaseModel):
    level: str
    target_band: Optional[float] = None
    native_language: str
    weaknesses: list[str]


# --- Teacher persona / lesson flow -----------------------------------------

STAGE_ORDER = ["warmup", "vocabulary", "grammar", "speaking_test", "homework"]
STAGE_LABELS = {
    "warmup": "Warm-up Conversation",
    "vocabulary": "Vocabulary Practice",
    "grammar": "Grammar Lesson",
    "speaking_test": "Speaking Test",
    "homework": "Homework",
}


class LessonTodayResponse(BaseModel):
    session_id: str
    teacher_name: str = "Mr. David"
    student_name: str
    day_number: int
    lesson_topic: str
    stage: str
    stage_index: int
    total_stages: int
    stage_label: str
    goal_checklist: list[str]
    prompt_text: str  # what the teacher says first (spoken via TTS)
    homework_from_last_time: Optional[str] = None
    streak_days: int = 0
    words_learned: int = 0
    # Dashboard / profile-memory fields
    level: str = "Intermediate"
    target_band: Optional[float] = None
    latest_band_score: Optional[float] = None
    weaknesses: list[str] = Field(default_factory=list)
    focus_weakness: Optional[str] = None  # the weakness this session is nudging toward


class LessonMessageRequest(BaseModel):
    session_id: str
    text: str = Field(min_length=0, max_length=2000)


class LessonMessageResponse(BaseModel):
    session_id: str
    reply_text: str
    correction: str = ""
    stage: str
    stage_index: int
    total_stages: int
    stage_label: str
    stage_complete: bool = False
    lesson_complete: bool = False
    words_learned: int = 0
    homework_text: Optional[str] = None


class BookInfo(BaseModel):
    id: str
    title: str
    created_at: datetime


class BookUploadResponse(BaseModel):
    book: BookInfo
    chunk_count: int


class BookTopicRequest(BaseModel):
    book_id: str
    topic: str
    session_id: Optional[str] = None


class BookTopicResponse(BaseModel):
    session_id: str
    reply_text: str
    example: str = ""
    source_book: str
