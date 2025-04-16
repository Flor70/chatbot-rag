# Supabase Project Information

## Project Details

- **Project Name**: chatbot-rag
- **Project ID**: qbfdwopiytnrufkwwway
- **Region**: sa-east-1
- **Database Engine**: Postgres 15
- **Status**: Active

## API Credentials

- **Project URL**: https://qbfdwopiytnrufkwwway.supabase.co
- **API Key (Anon/Public)**: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFiZmR3b3BpeXRucnVma3d3d2F5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM5Njc4MTgsImV4cCI6MjA1OTU0MzgxOH0.zW_65K4AU_dwu24qYc4zdBOdLvDiUU6Hqqp7CozbWaI

## Database Schema

### Tables

1. **courses**
   - `id`: UUID (Primary Key)
   - `pilar`: TEXT
   - `tipo`: TEXT
   - `nome`: TEXT
   - `created_at`: TIMESTAMP WITH TIME ZONE

2. **lessons**
   - `id`: UUID (Primary Key)
   - `course_id`: UUID (Foreign Key to courses.id)
   - `modulo`: TEXT
   - `nome`: TEXT
   - `youtube_link`: TEXT
   - `transcription`: TEXT
   - `video_summary`: TEXT
   - `created_at`: TIMESTAMP WITH TIME ZONE

### Relationships
- One course has many lessons (1:N relationship)

### Indexes
- `idx_lessons_course_id` on `lessons(course_id)`

### Security
- Row Level Security (RLS) is enabled on both tables
- Anonymous read access is allowed for both tables

## Example Queries

### Get all lessons with course information
```sql
SELECT 
    l.id AS lesson_id,
    c.pilar,
    c.tipo,
    c.nome AS curso,
    l.modulo,
    l.nome AS aula
FROM 
    lessons l
JOIN 
    courses c ON l.course_id = c.id
ORDER BY 
    c.pilar, c.tipo, c.nome, l.modulo, l.nome;
```

### Get a specific lesson with transcription
```sql
SELECT 
    l.transcription,
    l.video_summary,
    l.nome AS aula_nome,
    l.modulo,
    c.nome AS curso_nome,
    c.pilar,
    c.tipo
FROM 
    lessons l
JOIN 
    courses c ON l.course_id = c.id
WHERE 
    l.id = '[LESSON_ID]';
```

## Notes

- This Supabase project is used for the classroom chatbot prototype.
- The database is designed to store course information and lesson transcriptions.
- Data will be loaded from CSV files with course and lesson information. 