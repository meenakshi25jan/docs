import enum


class KnowledgeType(str, enum.Enum):
    """App-level enum for knowledge_embedding.knowledge_type (not a DB constraint)."""

    LESSON_KNOWLEDGE = "lesson_knowledge"
    KNOWLEDGE_CHUNK = "knowledge_chunk"
    GRAMMAR_RULE = "grammar_rule"
    VOCABULARY_KNOWLEDGE = "vocabulary_knowledge"


class SourceType(str, enum.Enum):
    PDF = "pdf"
    BOOK = "book"
    WEBSITE = "website"
    IMAGE = "image"
    DOCX = "docx"
    MANUAL = "manual"


class IngestionStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ConversationMode(str, enum.Enum):
    GRAMMAR = "grammar"
    CONVERSATION = "conversation"
    PRONUNCIATION = "pronunciation"


class SessionStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
