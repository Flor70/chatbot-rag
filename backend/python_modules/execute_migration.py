#!/usr/bin/env python
"""
Direct migration script to apply SQL schema to Supabase.
This is a simplified version for Task 4 execution.
"""

import os
import requests
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
# Using service role key for database operations
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")


def apply_migration():
    """Apply the SQL migration to Supabase"""
    print("Starting migration process...")

    # Check if environment variables are set
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment variables")
        return

    print(f"Connecting to Supabase: {SUPABASE_URL}")

    # Create Supabase client with service role key
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Path to SQL file
    sql_file_path = Path(__file__).parent / "src" / \
        "migrations" / "001_initial_schema.sql"

    # Check if file exists
    if not sql_file_path.exists():
        print(f"Error: SQL file not found at {sql_file_path}")
        return

    # Read SQL file
    with open(sql_file_path, 'r') as file:
        sql = file.read()

    print(f"Loaded SQL migration file: {sql_file_path.name}")
    print("Executing SQL...")

    try:
        # For Supabase, we need to use the SQL API directly
        # This requires constructing a REST API call
        sql_url = f"{SUPABASE_URL}/rest/v1/sql"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        response = requests.post(sql_url, json={"query": sql}, headers=headers)

        if response.status_code == 200:
            print("Migration applied successfully!")
            print("Tables created:")
            print("- courses")
            print("- lessons")
        else:
            print(
                f"Error executing SQL: {response.status_code} - {response.text}")

        # Verify tables were created
        print("\nVerifying table creation:")
        try:
            courses = supabase.table('courses').select('*').limit(1).execute()
            print(f"- courses table accessible: Yes")
        except Exception as e:
            print(f"- courses table accessible: No - {str(e)}")

        try:
            lessons = supabase.table('lessons').select('*').limit(1).execute()
            print(f"- lessons table accessible: Yes")
        except Exception as e:
            print(f"- lessons table accessible: No - {str(e)}")

    except Exception as e:
        print(f"Error executing SQL: {str(e)}")

    print("Migration process completed.")


if __name__ == "__main__":
    apply_migration()
