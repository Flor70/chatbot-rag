"""
Test the environment setup
"""

from src.config.environment import validate_env
import os
import sys
from unittest import mock

import pytest

# Adicione o diretório pai ao sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)


@pytest.fixture
def mock_env_variables():
    """Mock environment variables for testing"""
    with mock.patch.dict(os.environ, {
        "SUPABASE_URL": "https://test-url.supabase.co",
        "SUPABASE_ANON_KEY": "test-key",
        "OPENAI_API_KEY": "test-openai-key"
    }):
        yield


def test_validate_env_success(mock_env_variables):
    """Test that validate_env returns True when all required variables are set"""
    assert validate_env() is True


@pytest.fixture
def mock_missing_env_variables():
    """Mock environment with missing variables"""
    with mock.patch.dict(os.environ, {
        "SUPABASE_URL": "https://test-url.supabase.co",
        # Missing SUPABASE_ANON_KEY
        "OPENAI_API_KEY": "test-openai-key"
    }):
        yield


def test_validate_env_failure(mock_missing_env_variables):
    """Test that validate_env returns False when required variables are missing"""
    assert validate_env() is False
