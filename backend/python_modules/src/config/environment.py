"""
Environment configuration for chatbot-rag

This module loads environment variables from .env file
and provides them throughout the application.
"""

import logging
import os
from typing import Optional, List, Dict

# Import dotenv if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logging.warning(
        "dotenv not installed. Using environment variables directly.")

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

# OpenAI configuration
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

# Application configuration
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"

# Data directory
DATA_DIR = os.getenv('DATA_DIR', 'data')

# Validate required environment variables


def validate_env() -> bool:
    """
    Validate that all required environment variables are set.

    Returns:
        bool: True if all required variables are set, False otherwise
    """
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "OPENAI_API_KEY"
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(
            f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        return False

    return True
