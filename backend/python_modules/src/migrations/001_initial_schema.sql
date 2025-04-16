-- 001_initial_schema.sql
-- Initial database schema for classroom chatbot application
-- Created as part of Task 3

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create courses table
-- Stores information about educational courses
CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pilar TEXT NOT NULL, -- Knowledge area/pillar
    tipo TEXT NOT NULL, -- Course type
    nome TEXT NOT NULL, -- Course name
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure no duplicate courses
    UNIQUE(pilar, tipo, nome)
);

-- Create lessons table
-- Stores individual lessons and their transcriptions
CREATE TABLE lessons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID NOT NULL, -- Reference to the parent course
    modulo TEXT NOT NULL, -- Module name
    nome TEXT NOT NULL, -- Lesson name
    youtube_link TEXT, -- URL to YouTube video
    transcription TEXT, -- Full lesson transcription text
    video_summary TEXT, -- Summary of video content
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign key reference to courses table
    CONSTRAINT fk_course
        FOREIGN KEY (course_id)
        REFERENCES courses(id)
        ON DELETE CASCADE,
    
    -- Ensure no duplicate lessons within a course/module
    UNIQUE(course_id, modulo, nome)
);

-- Create index for optimizing queries by course_id
CREATE INDEX idx_lessons_course_id ON lessons(course_id);

-- Comments for documentation
COMMENT ON TABLE courses IS 'Educational courses information';
COMMENT ON TABLE lessons IS 'Individual lessons with transcriptions linked to courses';
COMMENT ON COLUMN courses.pilar IS 'Knowledge area/pillar';
COMMENT ON COLUMN courses.tipo IS 'Course type/category';
COMMENT ON COLUMN courses.nome IS 'Course name';
COMMENT ON COLUMN lessons.course_id IS 'Reference to parent course';
COMMENT ON COLUMN lessons.modulo IS 'Module name within course';
COMMENT ON COLUMN lessons.nome IS 'Lesson name';
COMMENT ON COLUMN lessons.transcription IS 'Full text transcription of lesson content';
COMMENT ON COLUMN lessons.video_summary IS 'AI-generated summary of video content'; 