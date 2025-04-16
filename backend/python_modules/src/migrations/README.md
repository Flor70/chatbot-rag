# Database Migrations

This directory contains SQL migration scripts for setting up and maintaining the database schema for the classroom chatbot application.

## Files

- `001_initial_schema.sql` - Initial schema creation with courses and lessons tables

## Usage

These migration scripts can be applied to a Supabase project using the Supabase CLI or directly through the Supabase dashboard SQL editor.

### Using Supabase CLI

```bash
# Example command to run a migration file
supabase db execute --file backend/python_modules/src/migrations/001_initial_schema.sql
```

### Using Supabase Dashboard

1. Log into your Supabase project
2. Navigate to the SQL Editor
3. Create a new query
4. Copy and paste the content of the migration file
5. Execute the SQL

## Schema Overview

The database consists of two primary tables:

1. **courses** - Stores information about educational courses 
2. **lessons** - Stores individual lessons with their transcriptions

For detailed schema information, see `docs/instructions/database-schema.md`.

## Guidelines for Creating New Migrations

When creating new migration scripts:

1. Name files with sequential numbering: `002_*.sql`, `003_*.sql`, etc.
2. Include comments at the top explaining the purpose of the migration
3. Test migrations on a development database before applying to production
4. Document any schema changes in this README 