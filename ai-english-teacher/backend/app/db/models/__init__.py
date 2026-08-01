"""
SQLAlchemy ORM models for the AI English Teacher MVP schema.

Deferred (future phase — do not implement here):
  vocabulary_mastery, achievement, user_achievement, grammar_rule,
  vocabulary_knowledge, tenant, teacher, organization, course, assignment,
  report, audit_log, subscription, payment.

Embeddings: Grok (xAI) does NOT generate RAG vectors. A separate embedding
pipeline/provider (default: sentence-transformers/all-MiniLM-L6-v2) is required.
"""

from app.db.models.band_score import BandScore
from app.db.models.conversation import ConversationMessage, ConversationSession
from app.db.models.feedback import GrammarFeedback
from app.db.models.knowledge_chunk import KnowledgeChunk
from app.db.models.knowledge_document import KnowledgeDocument
from app.db.models.knowledge_embedding import KnowledgeEmbedding
from app.db.models.knowledge_source import KnowledgeSource
from app.db.models.learning_plan import LearningPlan
from app.db.models.lesson_knowledge import LessonKnowledge
from app.db.models.user import User
from app.db.models.user_mistake_memory import UserMistakeMemory
from app.db.models.user_profile import UserProfile
from app.db.models.user_progress import UserProgress
from app.db.models.voice_settings import VoiceSettings

__all__ = [
    "BandScore",
    "ConversationMessage",
    "ConversationSession",
    "GrammarFeedback",
    "KnowledgeChunk",
    "KnowledgeDocument",
    "KnowledgeEmbedding",
    "KnowledgeSource",
    "LearningPlan",
    "LessonKnowledge",
    "User",
    "UserMistakeMemory",
    "UserProfile",
    "UserProgress",
    "VoiceSettings",
]
