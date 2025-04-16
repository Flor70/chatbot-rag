"""
CLI interface for chatbot-rag

This module provides a command-line interface for interacting with the chatbot agent.
"""

import argparse
import sys
from typing import List, Optional

from .services.agent import ChatbotAgent
from .services.database import get_all_lessons, get_lesson_transcription
from .config.environment import validate_env


def display_lessons(lessons: List[dict]) -> None:
    """
    Display a list of available lessons.

    Args:
        lessons: List of lesson dictionaries
    """
    print("\nAvailable lessons:")
    print("-" * 80)
    print(f"{'ID':<36} | {'Course':<20} | {'Module':<15} | {'Lesson'}")
    print("-" * 80)

    for idx, lesson in enumerate(lessons):
        course = lesson.get('courses', {})
        print(f"{lesson.get('lesson_id'):<36} | {course.get('curso', ''):<20} | "
              f"{lesson.get('modulo', ''):<15} | {lesson.get('aula', '')}")


def select_lesson(lessons: List[dict]) -> Optional[str]:
    """
    Let the user select a lesson from the list.

    Args:
        lessons: List of lesson dictionaries

    Returns:
        str: Selected lesson ID or None if canceled
    """
    display_lessons(lessons)

    print("\nEnter the ID of the lesson you want to query (or 'q' to quit):")
    lesson_id = input("> ")

    if lesson_id.lower() == 'q':
        return None

    # Validate the lesson ID exists
    valid_ids = [lesson.get('lesson_id') for lesson in lessons]
    if lesson_id not in valid_ids:
        print(f"Invalid lesson ID. Please try again.")
        return select_lesson(lessons)

    return lesson_id


def interactive_chat(agent: ChatbotAgent, lesson_id: str) -> None:
    """
    Start an interactive chat session with the agent about a specific lesson.

    Args:
        agent: The ChatbotAgent instance
        lesson_id: The ID of the selected lesson
    """
    # Get the lesson transcription
    lesson_data = get_lesson_transcription(lesson_id)
    if not lesson_data:
        print(f"Error: Lesson with ID {lesson_id} not found.")
        return

    transcription = lesson_data.get('transcription', '')
    if not transcription:
        print(f"Error: No transcription available for this lesson.")
        return

    # Display lesson info
    course_info = lesson_data.get('courses', {})
    print("\n" + "=" * 80)
    print(f"Selected Lesson: {lesson_data.get('aula_nome', '')}")
    print(f"Module: {lesson_data.get('modulo', '')}")
    print(f"Course: {course_info.get('curso_nome', '')}")
    print(f"Area: {course_info.get('pilar', '')}")
    print(f"Type: {course_info.get('tipo', '')}")
    print("=" * 80)

    # Start interactive chat
    print("\nYou can now ask questions about this lesson. Type 'q' to quit or 'reset' to reset the conversation.")

    while True:
        print("\nYour question:")
        question = input("> ")

        if question.lower() == 'q':
            break
        elif question.lower() == 'reset':
            agent.reset_conversation()
            print("Conversation history has been reset.")
            continue

        # Process the question
        print("\nProcessing your question...")
        response = agent.process_question(question, transcription, lesson_data)

        # Display the response
        print("\nAgent response:")
        print("-" * 80)
        print(response)
        print("-" * 80)


def main() -> int:
    """
    Main function for the CLI.

    Returns:
        int: Exit code (0 for success, non-zero for failure)
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Chatbot RAG CLI")
    parser.add_argument('--lesson-id', help="Lesson ID to query directly")
    parser.add_argument('--model', default="openai/gpt-4o",
                        help="Model to use (default: openai/gpt-4o)")
    args = parser.parse_args()

    # Validate environment
    if not validate_env():
        print("Environment validation failed. Please check your .env file.")
        return 1

    try:
        # Initialize the agent
        agent = ChatbotAgent()

        # Get all lessons
        lessons = get_all_lessons()
        if not lessons:
            print("No lessons found in the database.")
            return 1

        # If lesson ID is provided, use it directly
        lesson_id = args.lesson_id

        # Otherwise, let the user select a lesson
        if not lesson_id:
            lesson_id = select_lesson(lessons)

        # Exit if no lesson selected
        if not lesson_id:
            print("Exiting.")
            return 0

        # Start interactive chat
        interactive_chat(agent, lesson_id)

        return 0

    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
