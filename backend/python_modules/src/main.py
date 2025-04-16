"""
Main entry point for the chatbot-rag Python module
"""

import sys
from typing import List

from backend.python_modules.src.config.environment import validate_env
from backend.python_modules.src.services.database import get_all_lessons, get_lesson_transcription
from backend.python_modules.src.services.agent import ChatbotAgent


def test_database_connection() -> bool:
    """
    Test the database connection.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Test database connection
        lessons = get_all_lessons()
        print(
            f"Successfully connected to database. Found {len(lessons)} lessons.")

        if lessons:
            # Test retrieving a transcript
            lesson_id = lessons[0].get('lesson_id')
            lesson_data = get_lesson_transcription(lesson_id)
            if lesson_data and lesson_data.get('transcription'):
                print(
                    f"Successfully retrieved transcription for lesson: {lesson_data.get('aula_nome')}")
            else:
                print("Failed to retrieve transcription.")
                return False

        return True
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False


def test_agent() -> bool:
    """
    Test the chatbot agent.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Initialize the agent
        agent = ChatbotAgent()
        print("Successfully initialized chatbot agent.")

        # Get a sample lesson
        lessons = get_all_lessons()
        if not lessons:
            print("No lessons found in the database.")
            return False

        lesson_id = lessons[0].get('lesson_id')
        lesson_data = get_lesson_transcription(lesson_id)
        if not lesson_data:
            print(f"Lesson with ID {lesson_id} not found.")
            return False

        # Test a simple question
        print(f"Testing agent with lesson: {lesson_data.get('aula_nome')}")
        transcription = lesson_data.get('transcription', '')

        test_question = "What is this lecture about?"
        print(f"Test question: {test_question}")

        # Generate a response
        response = agent.process_question(
            test_question, transcription, lesson_data)
        print(f"Agent response: {response[:200]}...")  # Show first 200 chars

        return True
    except Exception as e:
        print(f"Error testing agent: {e}")
        return False


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

    # Test database connection
    print("\n=== Testing Database Connection ===")
    if not test_database_connection():
        return 1

    # Test agent
    print("\n=== Testing Chatbot Agent ===")
    if not test_agent():
        return 1

    print("\n=== All tests passed successfully ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
