import enum


class KnowledgeType(str, enum.Enum):
    """App-level enum for knowledge_embedding.knowledge_type (not a DB constraint)."""

    LESSON_KNOWLEDGE = "lesson_knowledge"
    GRAMMAR_RULE = "grammar_rule"
    VOCABULARY_KNOWLEDGE = "vocabulary_knowledge"


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
