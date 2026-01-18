#!/usr/bin/env python
"""
LLM Connection Test Script

Tests that the OpenAI-compatible LLM connection is working.
"""

import os
from pathlib import Path

# Load .env file
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


def test_llm_connection():
    """Test basic LLM connection."""
    print("=" * 50)
    print("🧪 LLM Connection Test")
    print("=" * 50)
    
    # Get config from env
    api_key = os.getenv("OPENAI_API_KEY", "")
    api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    model = os.getenv("LLM_MODEL", "gpt-4-turbo")
    
    print(f"\n📋 Configuration:")
    print(f"   API Base: {api_base}")
    print(f"   Model: {model}")
    print(f"   API Key: {'✅ Set' if api_key and api_key != 'your-api-key' else '❌ Not set'}")
    
    if not api_key or api_key == "your-api-key":
        print("\n❌ Please set OPENAI_API_KEY in .env file")
        return False
    
    # Create LLM client
    print(f"\n🔗 Connecting to LLM...")
    
    try:
        llm = ChatOpenAI(
            model=model,
            temperature=0,
            api_key=api_key,
            base_url=api_base if api_base != "https://api.openai.com/v1" else None,
        )
        
        # Test simple call
        messages = [
            SystemMessage(content="You are a helpful assistant. Respond briefly."),
            HumanMessage(content="Say 'Hello DeepFlow!' and nothing else.")
        ]
        
        response = llm.invoke(messages)
        
        print(f"\n✅ LLM Response: {response.content}")
        print("\n🎉 Connection successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_json_output():
    """Test JSON structured output."""
    print("\n" + "=" * 50)
    print("🧪 JSON Output Test")
    print("=" * 50)
    
    api_key = os.getenv("OPENAI_API_KEY", "")
    api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    model = os.getenv("LLM_MODEL", "gpt-4-turbo")
    
    try:
        llm = ChatOpenAI(
            model=model,
            temperature=0,
            api_key=api_key,
            base_url=api_base if api_base != "https://api.openai.com/v1" else None,
        )
        
        messages = [
            SystemMessage(content="Respond with JSON only. Format: {\"urgency\": <int 0-10>, \"reason\": \"<string>\"}"),
            HumanMessage(content="Rate the urgency of: 'Production server is down!'")
        ]
        
        response = llm.invoke(messages)
        
        print(f"\n📤 Response:\n{response.content}")
        
        # Try to parse JSON
        import json
        try:
            data = json.loads(response.content)
            print(f"\n✅ Valid JSON parsed:")
            print(f"   Urgency: {data.get('urgency')}")
            print(f"   Reason: {data.get('reason')}")
            return True
        except json.JSONDecodeError:
            print("\n⚠️ Response is not valid JSON")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    success1 = test_llm_connection()
    
    if success1:
        test_json_output()
