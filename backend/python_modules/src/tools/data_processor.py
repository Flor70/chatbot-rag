#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.config.environment import validate_env
import json
import logging
import os
import pandas as pd
import re
import sys
from typing import Dict, List, Tuple

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('data_processor')


def clean_text(text: str) -> str:
    """Clean text by removing special characters and normalizing formatting."""
    if pd.isna(text):
        return ""

    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', str(text))
    # Remove any non-printable characters
    text = re.sub(r'[^\x20-\x7E\x80-\xFF]', '', text)
    # Trim whitespace
    text = text.strip()

    return text


def process_csv(file_path: str) -> Tuple[List[Dict], List[Dict]]:
    """
    Process a CSV file containing course and lesson data.

    Args:
        file_path: Path to the CSV file

    Returns:
        Tuple[List[Dict], List[Dict]]: Tuple containing processed courses and lessons
    """
    logger.info(f"Processing CSV file: {file_path}")

    # Read CSV
    try:
        df = pd.read_csv(file_path)
        total_rows = len(df)
        logger.info(f"Read {total_rows} rows from CSV file")
    except Exception as e:
        logger.error(f"Error reading CSV file: {str(e)}")
        return [], []

    # Filter records with empty transcriptions
    has_transcription = df['transcription'].notna() & (
        df['transcription'] != '')
    filtered_df = df[has_transcription]
    filtered_rows = len(filtered_df)
    dropped_rows = total_rows - filtered_rows

    logger.info(f"Filtered out {dropped_rows} rows with empty transcriptions")
    logger.info(f"Processing {filtered_rows} rows with valid transcriptions")

    # Extract unique course information
    # Create a mapping of course indices to course names
    course_info = {}
    course_map = {}  # Maps course name to index

    # Check for test data format vs. production format
    has_test_format = all(col in df.columns for col in [
                          'Pilar', 'Tipo', 'Nome'])

    for idx, row in filtered_df.iterrows():
        if has_test_format:
            # Test data format
            course_name = row.get('Nome', '')
            pilar = row.get('Pilar', '')
            tipo = row.get('Tipo', '')
        else:
            # Production data format
            course_name = row.get('course_name', '')
            pilar = row.get('pilar', '')
            tipo = row.get('tipo', '')

        if course_name and course_name.strip():
            if course_name not in course_map:
                course_idx = len(course_map)
                course_map[course_name] = course_idx

                course_info[course_idx] = {
                    'pilar': pilar,
                    'tipo': tipo,
                    'nome': course_name.strip(),
                    'descricao': f'Course imported from CSV: {course_name.strip()}',
                    'original_idx': course_idx
                }

    logger.info(f"Extracted {len(course_info)} unique courses from the CSV")

    # Prepare courses for insertion
    courses = list(course_info.values())

    # Create a placeholder course for orphaned lessons
    if not courses:
        logger.warning(
            "No valid courses found in CSV. Creating a placeholder course.")
        missing_course_placeholder = {
            'pilar': 'Other',
            'tipo': 'Other',
            'nome': 'Placeholder Course for Orphaned Lessons',
            'descricao': 'Automatically created to hold lessons with missing course references',
            'original_idx': -1
        }
        courses.append(missing_course_placeholder)

    # Process lessons
    lessons = []
    orphaned_lessons = []
    orphaned_course_indices = set()

    for idx, row in filtered_df.iterrows():
        if has_test_format:
            # Test data format
            course_name = row.get('Nome', '')
            lesson_name = row.get('Aula', '')
            modulo = row.get('Módulo', '')
        else:
            # Production data format
            course_name = row.get('course_name', '')
            lesson_name = row.get('lesson_name', '')
            modulo = row.get('module', '')

        if not (lesson_name and lesson_name.strip()):
            logger.warning(f"Skipping lesson with empty name: {row.to_dict()}")
            continue

        # Get course index from the course map
        course_idx = course_map.get(course_name, None)

        lesson = {
            'nome': lesson_name.strip(),
            'modulo': modulo,
            'transcricao': row.get('transcription', ''),
            'youtube_link': row.get('youtube_link', ''),
            'video_summary': row.get('video_summary', ''),
            'course_idx': course_idx
        }

        # Check if we have a valid course reference
        if course_idx is not None and course_idx in course_info:
            lessons.append(lesson)
        else:
            # This is an orphaned lesson - its course is missing
            orphaned_course_indices.add(str(course_name))
            # Explicitly set course_idx to -1 for orphaned lessons
            lesson['course_idx'] = -1
            # Add flag to indicate this belongs to placeholder course
            lesson['placeholder_course'] = True
            orphaned_lessons.append(lesson)

    # Add placeholder course if we have orphaned lessons
    if orphaned_lessons:
        missing_course_placeholder = None
        for course in courses:
            if course.get('original_idx') == -1:
                missing_course_placeholder = course
                break

        if missing_course_placeholder is None:
            # Create placeholder now if we haven't yet
            missing_course_placeholder = {
                'pilar': 'Other',
                'tipo': 'Other',
                'nome': 'Placeholder Course for Orphaned Lessons',
                'descricao': f'Automatically created to hold lessons with missing course references from courses: {sorted(list(orphaned_course_indices))}',
                'original_idx': -1
            }
            courses.append(missing_course_placeholder)

        logger.warning(
            f"Found {len(orphaned_lessons)} orphaned lessons from missing courses: {sorted(list(orphaned_course_indices))}")
        logger.info("Adding orphaned lessons to placeholder course")

        # Add orphaned lessons to the main list
        lessons.extend(orphaned_lessons)

    logger.info(f"Processed {len(courses)} courses and {len(lessons)} lessons")
    return courses, lessons


def export_to_json(courses: List[Dict], lessons: List[Dict], output_dir: str) -> Tuple[str, str]:
    """
    Export processed data to JSON files.

    Args:
        courses: List of course dictionaries
        lessons: List of lesson dictionaries with course_idx references
        output_dir: Directory to save the JSON files

    Returns:
        Tuple with paths to the courses and lessons JSON files
    """
    os.makedirs(output_dir, exist_ok=True)

    # Convert course_idx to course_id for database insertion
    db_lessons = []
    for lesson in lessons:
        db_lesson = lesson.copy()

        # Ensure course_idx is an integer and a valid index
        if 'course_idx' in db_lesson:
            # Convert to int if it's a string
            if isinstance(db_lesson['course_idx'], str) and db_lesson['course_idx'].isdigit():
                db_lesson['course_idx'] = int(db_lesson['course_idx'])

            # Log warning if course_idx is out of range
            if db_lesson['course_idx'] >= len(courses):
                logger.warning(
                    f"Lesson {db_lesson['nome']} has course_idx {db_lesson['course_idx']} which is out of range (max: {len(courses)-1})")
        else:
            logger.warning(f"Lesson {db_lesson['nome']} has no course_idx")
            # Try to find matching course based on name pattern if possible
            db_lesson['course_idx'] = -1  # Set a sentinel value

        # Add a placeholder for the course_id that will be replaced during insertion
        if 'course_idx' in db_lesson and db_lesson['course_idx'] >= 0:
            # Format string that will be replaced with the actual ID during import
            db_lesson['course_id'] = f"{{course_{db_lesson['course_idx']}}}"
        else:
            db_lesson['course_id'] = None
            logger.warning(
                f"Lesson {db_lesson['nome']} will have null course_id")

        # Keep course_idx for reference during import
        db_lessons.append(db_lesson)

    courses_file = os.path.join(output_dir, 'courses.json')
    lessons_file = os.path.join(output_dir, 'lessons.json')

    with open(courses_file, 'w', encoding='utf-8') as f:
        json.dump(courses, f, ensure_ascii=False, indent=2)

    with open(lessons_file, 'w', encoding='utf-8') as f:
        json.dump(db_lessons, f, ensure_ascii=False, indent=2)

    logger.info(f"Exported courses to {courses_file}")
    logger.info(f"Exported lessons to {lessons_file}")

    return courses_file, lessons_file


def print_statistics(courses: List[Dict], lessons: List[Dict]) -> None:
    """Print statistics about the processed data."""
    logger.info("=== Data Processing Statistics ===")
    logger.info(f"Total unique courses: {len(courses)}")
    logger.info(f"Total lessons: {len(lessons)}")

    # Count lessons per course
    lessons_per_course = {}
    for lesson in lessons:
        course_idx = lesson['course_idx']
        if course_idx in lessons_per_course:
            lessons_per_course[course_idx] += 1
        else:
            lessons_per_course[course_idx] = 1

    avg_lessons = sum(lessons_per_course.values()) / \
        len(lessons_per_course) if lessons_per_course else 0
    logger.info(f"Average lessons per course: {avg_lessons:.2f}")

    # Count courses per pilar
    courses_per_pilar = {}
    for course in courses:
        pilar = course['pilar']
        if pilar in courses_per_pilar:
            courses_per_pilar[pilar] += 1
        else:
            courses_per_pilar[pilar] = 1

    logger.info("Courses per pilar:")
    for pilar, count in courses_per_pilar.items():
        logger.info(f"  - {pilar}: {count}")


def main():
    """Main function to process the CSV and export the data."""
    # Validate environment variables
    validate_env()

    # Set paths relative to project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".."))
    csv_path = os.path.join(project_root, "docs",
                            "internal_docs", "cursos_classplay.csv")
    output_dir = os.path.join(project_root, "data", "processed")

    logger.info(f"CSV path: {csv_path}")
    logger.info(f"Output directory: {output_dir}")

    # Process CSV
    courses, lessons = process_csv(csv_path)

    # Print statistics
    print_statistics(courses, lessons)

    # Export to JSON
    export_to_json(courses, lessons, output_dir)

    logger.info("Data processing completed successfully!")


if __name__ == "__main__":
    main()
