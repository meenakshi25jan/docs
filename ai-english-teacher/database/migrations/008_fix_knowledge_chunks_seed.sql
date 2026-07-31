-- Repair knowledge_chunks seed when 005 INSERT failed (NULL topic in VALUES bug).
-- Safe to re-run: only inserts when no valid seed rows exist.

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
WHERE NOT EXISTS (
    SELECT 1 FROM knowledge_chunks WHERE topic IS NOT NULL AND content IS NOT NULL LIMIT 1
);

-- Remove any corrupt rows from the broken 005 VALUES layout (NULL topic).
DELETE FROM knowledge_chunks WHERE topic IS NULL OR source IS NULL OR content IS NULL;
