-- Knowledge chunks for RAG (pgvector) + voice analysis storage

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id   UUID REFERENCES tenants(id) ON DELETE CASCADE,
    topic       VARCHAR(200) NOT NULL,
    source      VARCHAR(200) NOT NULL,
    content     TEXT NOT NULL,
    embedding   vector(1536),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_knowledge_topic ON knowledge_chunks(topic);
CREATE INDEX IF NOT EXISTS idx_knowledge_tenant ON knowledge_chunks(tenant_id);

CREATE TABLE IF NOT EXISTS voice_analyses (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id           UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    learner_id          UUID NOT NULL REFERENCES learner_profiles(id) ON DELETE CASCADE,
    conversation_id     UUID REFERENCES conversations(id) ON DELETE SET NULL,
    transcript          TEXT NOT NULL,
    duration_seconds    NUMERIC(8, 2),
    pronunciation_score NUMERIC(5, 2),
    fluency_score       NUMERIC(5, 2),
    grammar_score       NUMERIC(5, 2),
    vocabulary_score    NUMERIC(5, 2),
    overall_score       NUMERIC(5, 2),
    speech_quality      JSONB NOT NULL DEFAULT '{}',
    details             JSONB NOT NULL DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_voice_learner ON voice_analyses(learner_id, created_at DESC);

CREATE TABLE IF NOT EXISTS learner_memories (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id   UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    learner_id  UUID NOT NULL REFERENCES learner_profiles(id) ON DELETE CASCADE,
    memory_type VARCHAR(50) NOT NULL,
    content     TEXT NOT NULL,
    weight      NUMERIC(3, 2) DEFAULT 0.5,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_learner_memories ON learner_memories(learner_id, memory_type);

-- Seed global curriculum (embeddings added by seed script when AI is configured)
INSERT INTO knowledge_chunks (tenant_id, topic, source, content)
SELECT NULL, v.topic, v.source, v.content
FROM (VALUES
('present perfect', 'Grammar Unit 4',
 'Present perfect connects past actions to now: have/has + past participle. Use for life experience, unfinished time, and recent past with present relevance.'),
('articles', 'Grammar Unit 2',
 'Use a/an for non-specific singular nouns; the for specific nouns; omit articles with general plural or uncountable nouns in general statements.'),
('conditionals', 'Grammar Unit 7',
 'Zero conditional: if + present, present (facts). First: if + present, will (real future). Second: if + past, would (hypothetical). Third: if + past perfect, would have (past hypothetical).'),
('restaurant', 'Conversation Scenario',
 'Useful phrases: Could I see the menu?, I would like to order..., Could we have the bill please?, Is service included?'),
('job interview', 'Conversation Scenario',
 'Structure answers with STAR: Situation, Task, Action, Result. Use professional vocabulary and past tense for experience questions.'),
('ielts writing', 'IELTS Prep',
 'Task 2 essay: introduction with paraphrased question and thesis, two body paragraphs with topic sentences and examples, conclusion without new ideas.'),
('travel', 'Conversation Scenario',
 'At the airport: Where is the check-in counter?, I have a connecting flight., My luggage did not arrive on the carousel.'),
('business meeting', 'Conversation Scenario',
 'Open with agenda review, use phrases like Let us move on to..., Could you clarify..., I suggest we table this for now.')
) AS v(topic, source, content)
WHERE NOT EXISTS (SELECT 1 FROM knowledge_chunks LIMIT 1);
