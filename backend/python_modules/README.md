# Chatbot RAG Python Module

This Python module provides database access and integration with the Supabase backend for the classroom chatbot prototype.

## Setup

The project uses Poetry for dependency management.

### Prerequisites

- Python 3.9 or higher
- Poetry

### Installation

1. Clone the repository
2. Install dependencies:

```bash
poetry install
```

### Environment Variables

Make sure to set up the following environment variables in a `.env` file:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
OPENAI_API_KEY=your-openai-api-key
```

You can copy `.env.example` to `.env` and fill in the values.

## Usage

To test the environment setup:

```bash
poetry run python -m backend.python_modules.src.main
```

## Structure

- `src/config/`: Configuration modules
- `src/services/`: Service modules for database access and external APIs

## Development

Run tests:

```bash
poetry run pytest
``` 