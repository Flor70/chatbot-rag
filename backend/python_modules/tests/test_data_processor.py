#!/usr/bin/env python
# -*- coding: utf-8 -*-

from src.tools.data_processor import clean_text, process_csv, export_to_json
import os
import sys
import unittest
from unittest.mock import patch, mock_open
import pandas as pd
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


class TestDataProcessor(unittest.TestCase):
    """Test cases for the data processor module."""

    def test_clean_text(self):
        """Test the text cleaning function."""
        # Test with normal text
        self.assertEqual(clean_text("Sample text"), "Sample text")

        # Test with extra spaces
        self.assertEqual(clean_text("  Sample   text  "), "Sample text")

        # Test with non-printable characters
        self.assertEqual(clean_text("Sample\x00text"), "Sampletext")

        # Test with None/NaN
        self.assertEqual(clean_text(pd.NA), "")
        self.assertEqual(clean_text(None), "")

    @patch('pandas.read_csv')
    def test_process_csv(self, mock_read_csv):
        """Test the CSV processing function."""
        # Mock CSV data
        mock_data = {
            'Pilar': ['Conteúdos', 'Conteúdos', 'Conteúdos'],
            'Tipo': ['Cursos', 'Cursos', 'Masterclass'],
            'Nome': ['IA para Marketing', 'IA para Marketing', 'IA no Marketing'],
            'Módulo': ['Módulo 1', 'Módulo 2', 'Módulo 1'],
            'Aula': ['Aula 1', 'Aula 2', 'Aula 1'],
            'youtube_link': ['link1', 'link2', 'link3'],
            'transcription': ['transcript1', 'transcript2', 'transcript3'],
            'video_summary': ['summary1', 'summary2', 'summary3']
        }
        mock_df = pd.DataFrame(mock_data)
        mock_read_csv.return_value = mock_df

        # Call the function
        courses, lessons = process_csv('mock_path.csv')

        # Verify results
        self.assertEqual(len(courses), 2)  # Only 2 unique courses
        self.assertEqual(len(lessons), 3)  # 3 lessons

        # Check course data
        self.assertEqual(courses[0]['pilar'], 'Conteúdos')
        self.assertEqual(courses[0]['tipo'], 'Cursos')
        self.assertEqual(courses[0]['nome'], 'IA para Marketing')

        self.assertEqual(courses[1]['pilar'], 'Conteúdos')
        self.assertEqual(courses[1]['tipo'], 'Masterclass')
        self.assertEqual(courses[1]['nome'], 'IA no Marketing')

        # Check lesson data
        self.assertEqual(lessons[0]['modulo'], 'Módulo 1')
        self.assertEqual(lessons[0]['nome'], 'Aula 1')
        self.assertEqual(lessons[0]['course_idx'], 0)

        self.assertEqual(lessons[1]['modulo'], 'Módulo 2')
        self.assertEqual(lessons[1]['nome'], 'Aula 2')
        self.assertEqual(lessons[1]['course_idx'], 0)

        self.assertEqual(lessons[2]['modulo'], 'Módulo 1')
        self.assertEqual(lessons[2]['nome'], 'Aula 1')
        self.assertEqual(lessons[2]['course_idx'], 1)

    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_export_to_json(self, mock_json_dump, mock_file, mock_makedirs):
        """Test the JSON export function."""
        # Sample data
        courses = [
            {'pilar': 'Conteúdos', 'tipo': 'Cursos', 'nome': 'IA para Marketing'},
            {'pilar': 'Conteúdos', 'tipo': 'Masterclass', 'nome': 'IA no Marketing'}
        ]

        lessons = [
            {
                'course_idx': 0,
                'modulo': 'Módulo 1',
                'nome': 'Aula 1',
                'youtube_link': 'link1',
                'transcription': 'transcript1',
                'video_summary': 'summary1'
            }
        ]

        # Call the function
        courses_file, lessons_file = export_to_json(
            courses, lessons, 'mock_dir')

        # Verify directory creation
        mock_makedirs.assert_called_once_with('mock_dir', exist_ok=True)

        # Verify file opening
        self.assertEqual(mock_file.call_count, 2)

        # Verify json.dump was called with the correct data
        calls = mock_json_dump.call_args_list

        # First call should be for courses
        courses_call = calls[0]
        # First arg is the courses list
        self.assertEqual(len(courses_call.args[0]), 2)
        self.assertEqual(courses_call.args[0][0]['pilar'], 'Conteúdos')
        self.assertEqual(courses_call.args[0][0]['tipo'], 'Cursos')

        # Second call should be for lessons with transformed course_id
        lessons_call = calls[1]
        # First arg is the lessons list
        self.assertEqual(len(lessons_call.args[0]), 1)
        self.assertEqual(lessons_call.args[0][0]['modulo'], 'Módulo 1')
        self.assertEqual(lessons_call.args[0][0]['course_id'], '{course_0}')


if __name__ == '__main__':
    unittest.main()
