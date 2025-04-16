#!/usr/bin/env python
"""
Database Migration Script for Classroom Chatbot Application

This script applies SQL migration files to a Supabase database.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional

# Add parent directory to Python path to be able to import from other modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from src.config.environment import load_env_vars
    from src.services.database import get_supabase_client
except ImportError:
    print("Error: Unable to import required modules. Make sure the project structure is correct.")
    sys.exit(1)


def get_migration_files() -> List[str]:
    """Get all SQL migration files in the migrations directory sorted by name."""
    current_dir = Path(__file__).parent
    return sorted([
        str(file) for file in current_dir.glob("*.sql")
        if file.is_file() and file.name.endswith(".sql")
    ])


def apply_migration(file_path: str) -> bool:
    """Apply a single migration file to the database."""
    print(f"Applying migration: {os.path.basename(file_path)}")

    try:
        # Read the SQL file
        with open(file_path, 'r') as file:
            sql = file.read()

        # Get Supabase client
        supabase = get_supabase_client()

        # Execute the SQL
        result = supabase.rpc("exec_sql", {"query": sql}).execute()

        # Check if there was an error
        if result.data:
            print(
                f"Migration applied successfully: {os.path.basename(file_path)}")
            return True
        else:
            print(f"Error applying migration: {result.error}")
            return False

    except Exception as e:
        print(
            f"Error applying migration {os.path.basename(file_path)}: {str(e)}")
        return False


def apply_all_migrations() -> None:
    """Apply all migration files in the migrations directory."""
    # Load environment variables
    load_env_vars()

    # Get all migration files
    migration_files = get_migration_files()

    if not migration_files:
        print("No migration files found.")
        return

    print(f"Found {len(migration_files)} migration files.")

    # Apply each migration
    for file_path in migration_files:
        success = apply_migration(file_path)
        if not success:
            print(f"Failed to apply migration: {os.path.basename(file_path)}")
            break

    print("Migration process completed.")


if __name__ == "__main__":
    apply_all_migrations()
