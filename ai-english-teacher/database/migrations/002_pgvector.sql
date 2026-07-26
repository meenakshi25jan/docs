-- pgvector extension and embedding columns for semantic search

CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding columns for semantic mistake memory and vocabulary
ALTER TABLE error_tracking ADD COLUMN IF NOT EXISTS embedding vector(1536);
ALTER TABLE vocabulary_entries ADD COLUMN IF NOT EXISTS embedding vector(1536);

-- IVFFlat indexes for approximate nearest neighbor search
CREATE INDEX IF NOT EXISTS idx_errors_embedding ON error_tracking
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_vocab_embedding ON vocabulary_entries
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Helper function: find similar errors for a learner
CREATE OR REPLACE FUNCTION find_similar_errors(
    p_learner_id UUID,
    p_embedding vector(1536),
    p_limit INTEGER DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    error_category VARCHAR,
    error_type VARCHAR,
    error_text TEXT,
    correction TEXT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.error_category,
        e.error_type,
        e.error_text,
        e.correction,
        1 - (e.embedding <=> p_embedding) AS similarity
    FROM error_tracking e
    WHERE e.learner_id = p_learner_id
      AND e.embedding IS NOT NULL
    ORDER BY e.embedding <=> p_embedding
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Helper function: find related vocabulary
CREATE OR REPLACE FUNCTION find_related_vocabulary(
    p_learner_id UUID,
    p_embedding vector(1536),
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    id UUID,
    word VARCHAR,
    mastery_level VARCHAR,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        v.id,
        v.word,
        v.mastery_level,
        1 - (v.embedding <=> p_embedding) AS similarity
    FROM vocabulary_entries v
    WHERE v.learner_id = p_learner_id
      AND v.embedding IS NOT NULL
    ORDER BY v.embedding <=> p_embedding
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;
