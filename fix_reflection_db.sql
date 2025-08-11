-- Fix reflection table auto-increment sequence
-- This script fixes the strengths_reflection_responses table to have proper auto-increment

-- Create the sequence if it doesn't exist
CREATE SEQUENCE IF NOT EXISTS strengths_reflection_responses_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

-- Set the column default to use the sequence
ALTER TABLE strengths_reflection_responses 
    ALTER COLUMN id SET DEFAULT nextval('strengths_reflection_responses_id_seq');

-- Set the sequence ownership
ALTER SEQUENCE strengths_reflection_responses_id_seq 
    OWNED BY strengths_reflection_responses.id;

-- Get the current maximum ID and set sequence to start from there
SELECT setval('strengths_reflection_responses_id_seq', 
    COALESCE((SELECT MAX(id) FROM strengths_reflection_responses), 0) + 1, false);

-- Verify the setup
\d+ strengths_reflection_responses;