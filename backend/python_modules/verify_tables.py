#!/usr/bin/env python
"""
Verify Supabase Tables Script.
This script checks the existing tables in Supabase and their structure.
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Using anon key for read operations


def verify_tables():
    """Verify the existing tables and their structure"""
    print("Starting table verification...")

    # Check if environment variables are set
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        return

    print(f"Connecting to Supabase: {SUPABASE_URL}")

    # Create Supabase client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    try:
        # Check courses table
        print("\nChecking 'courses' table:")
        courses = supabase.table('courses').select('*').limit(5).execute()

        if hasattr(courses, 'data'):
            print(f"- Table exists with {len(courses.data)} records")
            if len(courses.data) > 0:
                print("- Sample column names:", list(courses.data[0].keys()))
        else:
            print("- Table exists but no data returned")

        # Check lessons table
        print("\nChecking 'lessons' table:")
        lessons = supabase.table('lessons').select('*').limit(5).execute()

        if hasattr(lessons, 'data'):
            print(f"- Table exists with {len(lessons.data)} records")
            if len(lessons.data) > 0:
                print("- Sample column names:", list(lessons.data[0].keys()))
        else:
            print("- Table exists but no data returned")

        # Verify foreign key relationship
        print("\nVerifying relationship between tables:")
        if len(courses.data) > 0:
            course_id = courses.data[0].get('id')
            related_lessons = supabase.table('lessons').select(
                '*').eq('course_id', course_id).execute()
            print(f"- Course ID: {course_id}")
            print(
                f"- Related lessons: {len(related_lessons.data) if hasattr(related_lessons, 'data') else 0}")

        print("\nTables verification completed successfully!")

    except Exception as e:
        print(f"Error verifying tables: {str(e)}")


if __name__ == "__main__":
    verify_tables()
