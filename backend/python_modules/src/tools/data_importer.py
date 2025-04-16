#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.tools.data_processor import process_csv, export_to_json
from src.services.database import get_supabase_client
from src.config.environment import validate_env, SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY
import argparse
import json
import logging
import os
import sys
import time
from typing import Dict, List, Optional, Tuple, Any
from uuid import UUID
from supabase import create_client
from supabase.client import Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('data_importer')

# Add root directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

# Import from local modules


def get_service_client():
    """
    Get a Supabase client with service role permissions.

    Returns:
        Client: A Supabase client with service role permissions
    """
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise ValueError(
            "Supabase URL and Service Key must be set in environment variables")

    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def load_json_data(file_path: str) -> List[Dict]:
    """
    Load data from a JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        List of dictionaries with the data
    """
    logger.info(f"Loading data from {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(
            f"Successfully loaded {len(data)} records from {file_path}")
        return data
    except Exception as e:
        logger.error(f"Error loading JSON file: {e}")
        raise


def insert_course(course, update=False):
    """
    Insert a course into the database.

    Args:
        course: Course data dictionary
        update: Whether to update existing records

    Returns:
        dict: Course data with ID
    """
    client = get_supabase_client()

    try:
        # Check if course already exists to avoid duplicate key errors
        result = client.table('courses').select(
            'id').eq('nome', course['nome']).execute()
        existing_course = result.data[0] if result.data else None

        if existing_course:
            logger.info(
                f"Course '{course['nome']}' already exists with ID: {existing_course['id']}")
            if update:
                # Update the existing course
                logger.info(f"Updating course: {course['nome']}")
                result = client.table('courses').update(course).eq(
                    'id', existing_course['id']).execute()
                if not result.data:
                    logger.error(f"Failed to update course: {course['nome']}")
                    return None
                course_with_id = result.data[0]
                logger.info(
                    f"Updated course: {course_with_id['nome']} with ID: {course_with_id['id']}")
                return course_with_id
            else:
                # Return the existing course ID without updating
                course['id'] = existing_course['id']
                return course
        else:
            # Insert as new course
            logger.info(f"Inserting new course: {course['nome']}")
            result = client.table('courses').insert(course).execute()
            course_with_id = result.data[0]
            logger.info(
                f"Inserted course: {course_with_id['nome']} with ID: {course_with_id['id']}")
            return course_with_id

    except Exception as e:
        logger.error(
            f"Error inserting/updating course {course['nome']}: {str(e)}")
        return None


def insert_lesson(lesson, update=False):
    """
    Insert a lesson into the database.

    Args:
        lesson: Lesson data dictionary
        update: Whether to update existing records

    Returns:
        dict: Lesson data with ID
    """
    client = get_supabase_client()

    try:
        # Check if lesson already exists to avoid duplicate key errors
        result = client.table('lessons').select('id').eq(
            'nome', lesson['nome']).eq('course_id', lesson['course_id']).execute()
        existing_lesson = result.data[0] if result.data else None

        if existing_lesson:
            logger.info(
                f"Lesson '{lesson['nome']}' already exists with ID: {existing_lesson['id']}")
            if update:
                # Update the existing lesson
                logger.info(f"Updating lesson: {lesson['nome']}")
                result = client.table('lessons').update(lesson).eq(
                    'id', existing_lesson['id']).execute()
                if not result.data:
                    logger.error(f"Failed to update lesson: {lesson['nome']}")
                    return None
                lesson_with_id = result.data[0]
                logger.info(
                    f"Updated lesson: {lesson_with_id['nome']} with ID: {lesson_with_id['id']}")
                return lesson_with_id
            else:
                # Return the existing lesson ID without updating
                lesson['id'] = existing_lesson['id']
                return lesson
        else:
            # Insert as new lesson
            logger.info(f"Inserting new lesson: {lesson['nome']}")
            result = client.table('lessons').insert(lesson).execute()
            lesson_with_id = result.data[0]
            logger.info(
                f"Inserted lesson: {lesson_with_id['nome']} with ID: {lesson_with_id['id']}")
            return lesson_with_id

    except Exception as e:
        logger.error(
            f"Error inserting/updating lesson {lesson['nome']}: {str(e)}")
        return None


def insert_courses(courses: List[Dict], dry_run: bool = False, update_existing: bool = False) -> Dict[int, str]:
    """
    Insert courses into the Supabase database.

    Args:
        courses: List of course dictionaries
        dry_run: If True, only simulate the operation without making actual changes
        update_existing: If True, update existing records instead of failing on conflicts

    Returns:
        Dictionary mapping course indices to their database IDs
    """
    logger.info(f"Inserting {len(courses)} courses into database")

    if dry_run:
        logger.info("DRY RUN: Would insert courses into database")
        # Return fake IDs for dry run
        return {idx: f"fake-id-{idx}" for idx, _ in enumerate(courses)}

    client = get_service_client()
    course_id_map = {}

    for course in courses:
        try:
            # Get the original index from the processed data
            original_idx = course.get('original_idx', None)
            if original_idx is None:
                logger.warning(
                    f"Course {course.get('nome', 'unknown')} has no original_idx")
                continue

            # Mapear para as colunas corretas do esquema
            course_data = {
                'pilar': course.get('pilar', 'Outros'),
                'tipo': course.get('tipo', 'Curso'),
                'nome': course.get('nome', '')
            }

            # Check if course already exists
            response = client.table('courses').select(
                'id').eq('nome', course_data['nome']).execute()

            course_id = None

            if response.data and len(response.data) > 0 and update_existing:
                # Course exists and we want to update
                course_id = response.data[0]['id']
                update_response = client.table('courses').update(
                    course_data).eq('id', course_id).execute()

                logger.info(
                    f"Updated existing course {course_data['nome']} with ID {course_id}")
            elif response.data and len(response.data) > 0:
                # Course exists but we don't want to update
                course_id = response.data[0]['id']
                logger.info(
                    f"Course {course_data['nome']} already exists with ID {course_id}")
            else:
                # Insert new course
                insert_response = client.table(
                    'courses').insert(course_data).execute()

                if insert_response.data and len(insert_response.data) > 0:
                    course_id = insert_response.data[0]['id']
                    logger.info(
                        f"Inserted new course {course_data['nome']} with ID {course_id}")
                else:
                    logger.warning(
                        f"No data returned for course {course_data['nome']}")

            # Map original index to database ID if we got an ID
            if course_id:
                # Map course index to database ID
                course_id_map[original_idx] = course_id

                if original_idx == -1:
                    logger.info(
                        f"Mapped placeholder course (index {original_idx}) to ID {course_id}")

        except Exception as e:
            logger.error(
                f"Error inserting course {course.get('nome', 'unknown')}: {e}")

        # Sleep briefly between operations to avoid rate limits
        time.sleep(0.5)

    logger.info(
        f"Successfully mapped {len(course_id_map)} courses of {len(courses)} total")
    return course_id_map


def insert_lessons(
    supabase: Client,
    lessons: List[Dict],
    course_map: Dict[int, UUID],
    create_placeholder_course: bool = True
) -> bool:
    """
    Insert lessons into the database.

    Args:
        supabase: Supabase client
        lessons: List of lesson dictionaries
        course_map: Mapping of course index to UUID (key: original_idx, value: UUID)
        create_placeholder_course: Whether to create a placeholder course for orphaned lessons

    Returns:
        bool: Success status
    """
    start_time = time.time()
    supabase_errors = []
    success_count = 0

    # Create a placeholder course for orphaned lessons if needed
    placeholder_course_id = None
    orphaned_lessons = [lesson for lesson in lessons if lesson.get(
        'course_idx') == -1 or lesson.get('placeholder_course')]

    if orphaned_lessons and create_placeholder_course:
        placeholder_course = {
            'pilar': 'Other',
            'tipo': 'Other',
            'nome': 'Placeholder Course for Orphaned Lessons',
            'descricao': 'Automatically created to hold lessons with missing course references'
        }
        placeholder_data = supabase.table(
            'courses').insert(placeholder_course).execute()
        if not placeholder_data.data:
            logger.error(
                "Failed to create placeholder course for orphaned lessons")
            return False
        placeholder_course_id = placeholder_data.data[0]['id']
        logger.info(
            f"Created placeholder course for orphaned lessons with ID: {placeholder_course_id}")

    # Insert lessons
    for i, lesson in enumerate(lessons):
        try:
            course_idx = lesson.get('course_idx')

            # Use placeholder course for orphaned lessons
            if (course_idx == -1 or lesson.get('placeholder_course')) and placeholder_course_id:
                course_id = placeholder_course_id
                logger.debug(
                    f"Associating orphaned lesson '{lesson.get('nome')}' with placeholder course")
            else:
                # Get course ID from map
                course_id = course_map.get(course_idx)

                # Skip if no course ID found
                if not course_id:
                    logger.warning(
                        f"Skipping lesson '{lesson.get('nome')}' due to missing course ID for idx {course_idx}")
                    continue

            # Create lesson data
            lesson_data = {
                'course_id': course_id,
                'modulo': lesson.get('modulo', ''),
                'nome': lesson.get('nome', ''),
                'youtube_link': lesson.get('youtube_link', ''),
                'transcription': lesson.get('transcricao', ''),
                'video_summary': lesson.get('video_summary', '')
            }

            # Insert lesson
            result = supabase.table('lessons').insert(lesson_data).execute()
            if result.data:
                success_count += 1
                logger.debug(f"Inserted lesson: {lesson.get('nome')}")
            else:
                logger.warning(
                    f"Empty response when inserting lesson: {lesson.get('nome')}")

        except Exception as e:
            error_msg = f"Error inserting lesson '{lesson.get('nome')}': {str(e)}"
            logger.error(error_msg)
            supabase_errors.append(error_msg)

    end_time = time.time()
    elapsed_time = round(end_time - start_time, 2)

    logger.info(
        f"Successfully inserted {success_count} lessons in {elapsed_time} seconds")

    if supabase_errors:
        logger.error(
            f"Encountered {len(supabase_errors)} errors during lesson insertion")
        for error in supabase_errors[:5]:  # Log first 5 errors
            logger.error(error)
        if len(supabase_errors) > 5:
            logger.error(f"... and {len(supabase_errors) - 5} more errors")

    return success_count > 0


def import_data(data: Dict, dry_run: bool = False, update_existing: bool = False, include_courses: bool = True, include_lessons: bool = True) -> Dict[str, Any]:
    """
    Import a dataset into the Supabase database.

    Args:
        data: The dataset to import
        dry_run: If True, only simulate the import without making actual changes
        update_existing: If True, update existing records instead of failing on conflicts
        include_courses: If True, import courses
        include_lessons: If True, import lessons

    Returns:
        Dictionary with statistics about the import process
    """
    start_time = time.time()
    stats = {
        "courses_processed": 0,
        "lessons_processed": 0,
        "errors": []
    }

    # Get Supabase client
    supabase = get_service_client() if not dry_run else None

    # Process courses
    if include_courses and "cursos" in data:
        processed_courses = []
        for idx, curso in enumerate(data["cursos"]):
            try:
                # Store the original index for mapping
                processed_course = {
                    "original_idx": idx,
                    "nome": curso.get("nome", ""),
                    "description": curso.get("description", "")
                }
                processed_courses.append(processed_course)
            except Exception as e:
                error_msg = f"Error processing course at index {idx}: {e}"
                logger.error(error_msg)
                stats["errors"].append(error_msg)

        # Add a placeholder course for orphaned lessons if it doesn't exist
        placeholder_exists = False
        for course in processed_courses:
            if course.get("nome") == "Placeholder Course for Orphaned Lessons":
                placeholder_exists = True
                # Ensure it has the special index
                course["original_idx"] = -1
                break

        if not placeholder_exists:
            logger.info("Adding placeholder course for orphaned lessons")
            processed_courses.append({
                "original_idx": -1,  # Special index for the placeholder
                "nome": "Placeholder Course for Orphaned Lessons",
                "description": "This course contains lessons that weren't associated with any existing course"
            })

        # Insert courses and get ID mapping
        course_id_map = insert_courses(
            processed_courses, dry_run, update_existing)
        stats["courses_processed"] = len(processed_courses)
    else:
        course_id_map = {}

    # Process lessons
    if include_lessons and "licoes" in data:
        processed_lessons = []
        for idx, licao in enumerate(data["licoes"]):
            try:
                course_idx = licao.get("course_idx")
                processed_lesson = {
                    "original_idx": idx,
                    "course_idx": course_idx,
                    "nome": licao.get("nome", ""),
                    "description": licao.get("description", ""),
                    "content": licao.get("content", ""),
                    "type": licao.get("type", "text"),
                    "placeholder_course": licao.get("placeholder_course", False)
                }
                processed_lessons.append(processed_lesson)
            except Exception as e:
                error_msg = f"Error processing lesson at index {idx}: {e}"
                logger.error(error_msg)
                stats["errors"].append(error_msg)

        # Insert lessons using the updated function signature
        if dry_run:
            logger.info(
                f"DRY RUN: Would insert {len(processed_lessons)} lessons")
            stats["lessons_processed"] = len(processed_lessons)
        else:
            success = insert_lessons(
                supabase, processed_lessons, course_id_map)
            stats["lessons_processed"] = len(
                processed_lessons) if success else 0

    duration = time.time() - start_time
    stats["duration_seconds"] = duration
    return stats


def process_and_import(csv_path: str, output_dir: str = None, dry_run: bool = False, update_existing: bool = False) -> bool:
    """
    Process CSV file and import data into Supabase in one operation.

    Args:
        csv_path: Path to the CSV file
        output_dir: Directory to save processed JSON files (optional)
        dry_run: If True, only simulate the operation without making actual changes
        update_existing: If True, update existing records instead of failing on conflicts

    Returns:
        True if processing and import were successful, False otherwise
    """
    try:
        # Process the CSV file
        courses, lessons = process_csv(csv_path)

        logger.info(
            f"Processed {len(courses)} courses and {len(lessons)} lessons from CSV")

        # Determine output directory
        if not output_dir:
            output_dir = os.path.join(os.path.dirname(csv_path), "processed")

        # Make sure the directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Export to JSON for reference/backup
        courses_file, lessons_file = export_to_json(
            courses, lessons, output_dir)

        logger.info(f"Exported processed data to {output_dir}")

        if dry_run:
            logger.info(
                f"DRY RUN: Would import {len(courses)} courses and {len(lessons)} lessons")
            return True

        # Create a data dictionary for import
        data = {
            "cursos": courses,
            "licoes": lessons
        }

        # Import the data
        import_result = import_data(data, dry_run, update_existing)

        # Check if there were any errors
        if import_result.get("errors", []):
            logger.warning(
                f"Import completed with {len(import_result['errors'])} errors")
            for error in import_result["errors"][:5]:  # Show first 5 errors
                logger.warning(f"Error: {error}")

        logger.info(f"Import statistics: {import_result}")

        # Consider the import successful if we processed all courses and at least 90% of lessons
        if (import_result.get("courses_processed", 0) == len(courses) and
                import_result.get("lessons_processed", 0) >= len(lessons) * 0.9):
            return True
        else:
            logger.warning("Import completed but did not process all data")
            return False

    except Exception as e:
        logger.error(f"Error during processing and import: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Import data from CSV or JSON into Supabase')
    parser.add_argument('--dry-run', action='store_true',
                        help='Simulate the import without making any changes')
    parser.add_argument('--update', action='store_true',
                        help='Update existing records instead of failing on conflicts')
    parser.add_argument('--csv', help='Path to CSV file to process and import')
    parser.add_argument(
        '--courses', help='Path to courses JSON file to import')
    parser.add_argument(
        '--lessons', help='Path to lessons JSON file to import')
    parser.add_argument('--reprocess', action='store_true',
                        help='Force reprocessing of CSV file even if JSON files exist')
    return parser.parse_args()


def main():
    """Main function to import data into Supabase."""
    # Parse command line arguments
    args = parse_args()

    # Validate environment variables
    if not validate_env():
        logger.error(
            "Environment validation failed. Please check your .env file.")
        sys.exit(1)

    # Set paths relative to project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".."))

    # Handle specific file paths if provided
    if args.csv:
        csv_path = args.csv
        logger.info(f"Using provided CSV file: {csv_path}")
        success = process_and_import(
            csv_path, dry_run=args.dry_run, update_existing=args.update)
    elif args.courses and args.lessons:
        courses_file = args.courses
        lessons_file = args.lessons
        logger.info(
            f"Using provided JSON files: {courses_file} and {lessons_file}")

        # Load the JSON data
        courses = load_json_data(courses_file)
        lessons = load_json_data(lessons_file)

        # Create data dictionary for import
        data = {
            "cursos": courses,
            "licoes": lessons
        }

        # Import the data
        import_result = import_data(
            data, dry_run=args.dry_run, update_existing=args.update)

        # Consider the import successful if we processed data without errors
        success = len(import_result.get("errors", [])) == 0
    else:
        # Use default paths
        csv_path = os.path.join(project_root, "docs",
                                "internal_docs", "cursos_classplay.csv")
        processed_dir = os.path.join(project_root, "data", "processed")

        # Check if processed data already exists
        courses_file = os.path.join(processed_dir, 'courses.json')
        lessons_file = os.path.join(processed_dir, 'lessons.json')

        # Force reprocessing if --reprocess flag is set
        if args.reprocess:
            logger.info(
                "Reprocessing flag set. Processing CSV regardless of existing JSON files.")
            success = process_and_import(
                csv_path, processed_dir, dry_run=args.dry_run, update_existing=args.update)
        elif os.path.exists(courses_file) and os.path.exists(lessons_file):
            logger.info("Processed data already exists. Importing directly.")

            # Load the JSON data
            courses = load_json_data(courses_file)
            lessons = load_json_data(lessons_file)

            # Create data dictionary for import
            data = {
                "cursos": courses,
                "licoes": lessons
            }

            # Import the data
            import_result = import_data(
                data, dry_run=args.dry_run, update_existing=args.update)

            # Consider the import successful if we processed data without errors
            success = len(import_result.get("errors", [])) == 0
        else:
            logger.info(
                "Processed data not found. Processing CSV and importing.")
            success = process_and_import(
                csv_path, processed_dir, dry_run=args.dry_run, update_existing=args.update)

    if success:
        logger.info("Data import completed successfully!")
    else:
        logger.error("Data import failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
