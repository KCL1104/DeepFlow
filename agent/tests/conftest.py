"""Pytest configuration for Agent tests."""

import pytest
import os

# Set mock environment variables
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("OPENAI_API_BASE", "https://api.openai.com/v1")
os.environ.setdefault("LLM_MODEL", "gpt-4-turbo")
