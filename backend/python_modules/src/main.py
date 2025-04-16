"""
Main entry point for the chatbot-rag Python module
"""

import sys
from typing import List

from backend.python_modules.src.config.environment import validate_env
from backend.python_modules.src.services.database import get_all_lessons, get_lesson_transcription


def main() -> int:
    """
    Main function to test the environment setup.

    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    # Validate environment variables
    if not validate_env():
        print("Environment validation failed")
        return 1

    print("Environment validation successful")
    print("Test connection to Supabase...")

    try:
        # Test database connection
        lessons = get_all_lessons()
        print(
            f"Successfully connected to database. Found {len(lessons)} lessons.")
        return 0
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
