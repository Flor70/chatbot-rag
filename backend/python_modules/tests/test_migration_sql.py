#!/usr/bin/env python
"""
Test script for validating SQL migration files
"""

import os
import re
import unittest
from pathlib import Path


class TestMigrationSQL(unittest.TestCase):
    """Test case for validating SQL migration files."""

    @classmethod
    def setUpClass(cls):
        """Set up test case."""
        # Get the path to the migrations directory
        cls.migrations_dir = Path(
            __file__).parent.parent / "src" / "migrations"
        # Get the first migration file
        migration_files = sorted([
            file for file in cls.migrations_dir.glob("*.sql")
            if file.is_file() and file.name.endswith(".sql")
        ])
        cls.initial_migration = migration_files[0] if migration_files else None

    def test_migration_directory_exists(self):
        """Test that the migrations directory exists."""
        self.assertTrue(
            self.migrations_dir.exists(),
            f"Migrations directory does not exist: {self.migrations_dir}"
        )

    def test_initial_migration_exists(self):
        """Test that at least one migration file exists."""
        self.assertIsNotNone(
            self.initial_migration,
            "No migration files found"
        )

    def test_migration_sql_syntax(self):
        """Test that the SQL syntax is valid."""
        if not self.initial_migration:
            self.skipTest("No migration files found")

        # Read the migration file
        with open(self.initial_migration, "r") as file:
            sql = file.read()

        # Basic syntax checks

        # Check that CREATE TABLE statements have a closing parenthesis
        create_table_statements = re.findall(
            r"CREATE TABLE\s+(\w+)\s*\(([^;]+)\);", sql, re.DOTALL)
        self.assertTrue(
            len(create_table_statements) >= 2,
            f"Expected at least 2 CREATE TABLE statements, found {len(create_table_statements)}"
        )

        # Check that each table has the required columns
        for table_name, table_content in create_table_statements:
            self.assertIn(
                "id UUID PRIMARY KEY",
                table_content,
                f"Table {table_name} does not have id UUID PRIMARY KEY"
            )
            self.assertIn(
                "created_at TIMESTAMP",
                table_content,
                f"Table {table_name} does not have created_at TIMESTAMP"
            )

        # Check for courses table with required columns
        courses_pattern = r"CREATE TABLE\s+courses\s*\([^;]+pilar TEXT[^;]+tipo TEXT[^;]+nome TEXT[^;]+\);"
        self.assertTrue(
            re.search(courses_pattern, sql, re.DOTALL),
            "courses table does not have required columns: pilar, tipo, nome"
        )

        # Check for lessons table with required columns
        lessons_pattern = r"CREATE TABLE\s+lessons\s*\([^;]+course_id UUID[^;]+modulo TEXT[^;]+nome TEXT[^;]+transcription TEXT[^;]+\);"
        self.assertTrue(
            re.search(lessons_pattern, sql, re.DOTALL),
            "lessons table does not have required columns: course_id, modulo, nome, transcription"
        )

        # Check for foreign key constraint
        fk_pattern = r"FOREIGN KEY\s*\(\s*course_id\s*\)\s*REFERENCES\s+courses\s*\(\s*id\s*\)"
        self.assertTrue(
            re.search(fk_pattern, sql, re.DOTALL),
            "No foreign key constraint found linking lessons to courses"
        )

        # Check for index on lessons.course_id
        index_pattern = r"CREATE INDEX\s+idx_lessons_course_id\s+ON\s+lessons\s*\(\s*course_id\s*\);"
        self.assertTrue(
            re.search(index_pattern, sql, re.DOTALL),
            "No index found on lessons.course_id"
        )

        # Check for uniqueness constraints
        uniqueness_pattern_courses = r"UNIQUE\s*\(\s*pilar\s*,\s*tipo\s*,\s*nome\s*\)"
        self.assertTrue(
            re.search(uniqueness_pattern_courses, sql, re.DOTALL),
            "No uniqueness constraint found for courses table"
        )

        uniqueness_pattern_lessons = r"UNIQUE\s*\(\s*course_id\s*,\s*modulo\s*,\s*nome\s*\)"
        self.assertTrue(
            re.search(uniqueness_pattern_lessons, sql, re.DOTALL),
            "No uniqueness constraint found for lessons table"
        )


if __name__ == "__main__":
    unittest.main()
