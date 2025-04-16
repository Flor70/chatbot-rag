#!/usr/bin/env python
"""
Data Import Script for Supabase.
This script imports processed data into the Supabase database.
"""

from src.tools.data_importer import main as importer_main
import os
import sys
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the data importer module

if __name__ == "__main__":
    importer_main()
