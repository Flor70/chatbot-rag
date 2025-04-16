# Tools Directory

This directory contains utility scripts for data processing and other operations needed for the chatbot application.

## Data Processor (`data_processor.py`)

A script to process the source CSV file containing course and lesson information.

### Functionality

- Reads and processes data from `docs/internal_docs/cursos_classplay.csv`
- Filters out records with empty transcriptions
- Cleans data by removing special characters and normalizing formatting
- Extracts unique course information (Pilar, Tipo, Nome combinations)
- Prepares data structures for the database tables: courses and lessons
- Exports processed data to JSON files for database import
- Generates statistics about the processed data

### Usage

Run the script from the `backend/python_modules` directory:

```bash
python -m src.tools.data_processor
```

### Output

The script will generate two JSON files in the `data/processed` directory:

- `courses.json`: Contains unique course data (pilar, tipo, nome)
- `lessons.json`: Contains lesson data with references to corresponding courses

### Testing

Unit tests for the data processor are in `tests/test_data_processor.py`. Run the tests with:

```bash
python -m unittest tests/test_data_processor.py
```

## How to Add New Tools

To add new tools to this directory:

1. Create a new Python file in the `tools` directory
2. Add any necessary imports and functions
3. Include the tool in the `__init__.py` file to make it available for import
4. Add unit tests in the `tests` directory
5. Document the tool in this README file 