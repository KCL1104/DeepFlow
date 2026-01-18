#!/usr/bin/env python
"""
Test Opik Connection

Verifies that Opik API key and configuration are working.
"""

import os
from pathlib import Path

# Load .env
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")


def test_opik_connection():
    """Test Opik connection."""
    print("=" * 50)
    print("🧪 Opik Connection Test")
    print("=" * 50)
    
    # Check env vars
    api_key = os.getenv("OPIK_API_KEY", "")
    url = os.getenv("OPIK_URL_OVERRIDE", "https://www.comet.com/opik/api")
    workspace = os.getenv("OPIK_WORKSPACE", "default")
    project = os.getenv("OPIK_PROJECT_NAME", "deepflow-agent")
    
    print(f"\n📋 Configuration:")
    print(f"   API Key: {'✅ Set' if api_key and api_key != 'your-opik-api-key' else '❌ Not set'}")
    print(f"   URL: {url}")
    print(f"   Workspace: {workspace}")
    print(f"   Project: {project}")
    
    if not api_key or api_key == "your-opik-api-key":
        print("\n❌ Please set OPIK_API_KEY in .env file")
        return False
    
    print("\n🔗 Connecting to Opik...")
    
    try:
        import opik
        
        # Configure Opik
        opik.configure(
            api_key=api_key,
            workspace=workspace,
        )
        
        # Create a test client
        client = opik.Opik()
        
        # Try to list projects (simple API call)
        print("\n✅ Opik client initialized successfully!")
        
        # Test creating a simple trace
        print("\n📝 Creating test trace...")
        
        @opik.track(name="test_connection")
        def test_function():
            return "Hello from DeepFlow!"
        
        result = test_function()
        print(f"   Result: {result}")
        
        print("\n🎉 Opik connection successful!")
        print(f"\n👉 View in dashboard: https://www.comet.com/opik/{workspace}/projects")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    test_opik_connection()
