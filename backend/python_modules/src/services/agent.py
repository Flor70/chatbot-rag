"""
Agent service for chatbot-rag

This module provides the agent service for the chatbot.
The agent uses OpenRouter to access LLMs and processes questions
based on lecture transcriptions.
"""

import logging
import json
from typing import Dict, List, Optional, Any

import openai
import requests

from ..config.environment import OPENROUTER_API_KEY

logger = logging.getLogger(__name__)


class ChatbotAgent:
    """
    Agent for processing questions about lecture transcriptions.

    This agent uses OpenRouter to access various LLMs and generates
    responses based on lecture transcription context.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the ChatbotAgent.

        Args:
            api_key: OpenRouter API key. If not provided, uses the one from environment.
        """
        self.api_key = api_key or OPENROUTER_API_KEY

        if not self.api_key:
            raise ValueError("OpenRouter API key is required")

        # We'll use the openai client with OpenRouter base URL
        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key
        )

        self.conversation_history = []

    def create_prompt_with_context(self, question: str, transcription: str,
                                   lesson_info: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Create a prompt with context for the agent.

        Args:
            question: The user's question
            transcription: The transcription of the lecture
            lesson_info: Metadata about the lesson (title, course, etc.)

        Returns:
            List of message dictionaries for the LLM
        """
        # Create a system prompt that instructs the model on its role
        system_message = {
            "role": "system",
            "content": f"""You are an educational assistant that helps answer questions about lectures.
You have access to the transcription of a specific lecture, and you should use this information to provide accurate answers.
If the answer cannot be found in the transcription, acknowledge that and provide the most helpful response you can.

Lecture Information:
- Title: {lesson_info.get('aula_nome', 'Unknown')}
- Module: {lesson_info.get('modulo', 'Unknown')}
- Course: {lesson_info.get('curso_nome', 'Unknown')}
- Area: {lesson_info.get('pilar', 'Unknown')}
- Type: {lesson_info.get('tipo', 'Unknown')}

Only use information from the transcription to answer questions about the lecture content.
Be concise and direct in your responses."""
        }

        # Create a context message with the transcription
        context_message = {
            "role": "user",
            "content": f"Here is the transcription of the lecture:\n\n{transcription}\n\nPlease help me answer questions about this lecture."
        }

        # Add the question
        question_message = {
            "role": "user",
            "content": question
        }

        # Construct the full message array
        messages = [system_message, context_message]

        # Add conversation history if any
        messages.extend(self.conversation_history)

        # Add the current question
        messages.append(question_message)

        return messages

    def process_question(self, question: str, transcription: str,
                         lesson_info: Dict[str, Any], model: str = "openai/gpt-4o") -> str:
        """
        Process a question about a lecture transcription.

        Args:
            question: The user's question
            transcription: The transcription of the lecture
            lesson_info: Metadata about the lesson
            model: The model to use for the query

        Returns:
            The agent's response
        """
        try:
            # Create the prompt with context
            messages = self.create_prompt_with_context(
                question, transcription, lesson_info)

            # Call the model through OpenRouter
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            # Extract the assistant's message
            assistant_message = response.choices[0].message.content

            # Update conversation history to include this exchange
            self.conversation_history.append(
                {"role": "user", "content": question})
            self.conversation_history.append(
                {"role": "assistant", "content": assistant_message})

            # Keep history limited to last 10 messages
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]

            return assistant_message

        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            return f"Sorry, I encountered an error while processing your question: {str(e)}"

    def reset_conversation(self):
        """
        Reset the conversation history.
        """
        self.conversation_history = []
