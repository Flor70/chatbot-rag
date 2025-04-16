"""
Test script for the ChatbotAgent

This script tests the basic functionality of the ChatbotAgent.
"""

import sys
import logging
from typing import Dict, Any, List

from .services.agent import ChatbotAgent
from .services.database import get_all_lessons, get_lesson_transcription
from .config.environment import validate_env

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_sample_lesson() -> Dict[str, Any]:
    """
    Get a sample lesson for testing.

    Returns:
        Dict[str, Any]: A sample lesson or None if no lessons are available
    """
    # Get all lessons
    lessons = get_all_lessons()
    if not lessons:
        logger.error("No lessons found in the database")
        return None

    # Pick the first lesson
    lesson_id = lessons[0].get('lesson_id')
    logger.info(f"Using lesson ID: {lesson_id}")

    # Get the lesson transcription
    lesson_data = get_lesson_transcription(lesson_id)
    if not lesson_data:
        logger.error(f"Lesson with ID {lesson_id} not found")
        return None

    return lesson_data


def test_prompt_creation() -> bool:
    """
    Test the prompt creation functionality.

    Returns:
        bool: True if the test passes, False otherwise
    """
    logger.info("Testing prompt creation...")

    # Get a sample lesson
    lesson_data = get_sample_lesson()
    if not lesson_data:
        return False

    # Initialize the agent
    try:
        agent = ChatbotAgent()
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        return False

    # Test prompt creation
    try:
        transcription = lesson_data.get('transcription', '')[
            :500]  # Use first 500 chars for testing
        messages = agent.create_prompt_with_context(
            "What is this lecture about?",
            transcription,
            lesson_data
        )

        # Verify the messages structure
        if not isinstance(messages, list) or len(messages) < 3:
            logger.error(f"Invalid messages structure: {messages}")
            return False

        logger.info("Prompt creation successful")
        logger.info(f"Generated {len(messages)} messages")
        return True
    except Exception as e:
        logger.error(f"Error in prompt creation: {e}")
        return False


def test_question_processing() -> bool:
    """
    Test the question processing functionality.

    Returns:
        bool: True if the test passes, False otherwise
    """
    logger.info("Testing question processing...")

    # Get a sample lesson
    lesson_data = get_sample_lesson()
    if not lesson_data:
        return False

    # Initialize the agent
    try:
        agent = ChatbotAgent()
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        return False

    # Test question processing
    try:
        transcription = lesson_data.get('transcription', '')
        response = agent.process_question(
            "What is the main topic of this lecture?",
            transcription,
            lesson_data
        )

        # Verify the response
        if not response or not isinstance(response, str):
            logger.error(f"Invalid response: {response}")
            return False

        logger.info("Question processing successful")
        logger.info(f"Response: {response[:100]}...")  # Show first 100 chars
        return True
    except Exception as e:
        logger.error(f"Error in question processing: {e}")
        return False


def main() -> int:
    """
    Main function to run all tests.

    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    # Validate environment
    if not validate_env():
        logger.error("Environment validation failed")
        return 1

    # Run tests
    tests = [
        ("Prompt Creation", test_prompt_creation),
        ("Question Processing", test_question_processing)
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        logger.info(f"Running test: {name}")
        try:
            result = test_func()
            if result:
                logger.info(f"✅ {name}: PASSED")
                passed += 1
            else:
                logger.error(f"❌ {name}: FAILED")
                failed += 1
        except Exception as e:
            logger.error(f"❌ {name}: ERROR - {e}")
            failed += 1

    # Print summary
    logger.info(f"Test Summary: {passed} passed, {failed} failed")

    # Return success if all tests passed
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
