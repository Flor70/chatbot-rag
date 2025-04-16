"""
Database service for chatbot-rag

This module provides functions to interact with the Supabase database.
"""

from typing import Any, Dict, List, Optional

from supabase import Client, create_client

from ..config.environment import SUPABASE_ANON_KEY, SUPABASE_URL


def get_supabase_client() -> Client:
    """
    Get a Supabase client instance.

    Returns:
        Client: A Supabase client
    """
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise ValueError(
            "Supabase URL and Anon Key must be set in environment variables")

    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def get_all_lessons() -> List[Dict[str, Any]]:
    """
    Get all lessons with course information.

    Returns:
        List[Dict[str, Any]]: A list of lessons with course information
    """
    client = get_supabase_client()

    response = client.table("lessons").select(
        "id:lesson_id, modulo, nome:aula, youtube_link, courses(pilar, tipo, nome:curso)"
    ).execute()

    return response.data


def get_lesson_transcription(lesson_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific lesson with its transcription.

    Args:
        lesson_id: The ID of the lesson

    Returns:
        Optional[Dict[str, Any]]: The lesson data with transcription, or None if not found
    """
    client = get_supabase_client()

    response = client.table("lessons").select(
        "transcription, video_summary, nome:aula_nome, modulo, courses(nome:curso_nome, pilar, tipo)"
    ).eq("id", lesson_id).execute()

    if not response.data:
        return None

    return response.data[0]
