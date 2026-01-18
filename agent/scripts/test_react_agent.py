#!/usr/bin/env python
"""
Test script for DeepFlow ReAct Agent with Tools

This script tests the ReAct agent's ability to:
1. Analyze messages and determine urgency
2. Execute appropriate tools based on user state
3. Track actions via Opik
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load env
load_dotenv(Path(__file__).parent.parent / ".env")

# Check required env vars
required_vars = ["OPENAI_API_KEY", "OPENAI_API_BASE", "LLM_MODEL"]
for var in required_vars:
    if not os.getenv(var):
        print(f"❌ Missing required env var: {var}")
        exit(1)

print("=" * 60)
print("🤖 DeepFlow ReAct Agent Test")
print("=" * 60)


def test_tool_imports():
    """Test that all tools can be imported."""
    print("\n📦 Testing tool imports...")
    
    from deepflow_agent.tools import (
        add_to_queue,
        send_auto_reply,
        update_task_status,
        notify_user_tool,
        send_browser_notification,
    )
    
    tools = [
        add_to_queue,
        send_auto_reply,
        update_task_status,
        notify_user_tool,
        send_browser_notification,
    ]
    
    for tool in tools:
        print(f"   ✅ {tool.name}: {tool.description[:50]}...")
    
    print(f"\n   Total: {len(tools)} tools loaded")
    return tools


def test_agent_creation():
    """Test that agent can be created."""
    print("\n🏗️ Testing agent creation...")
    
    from deepflow_agent.agents import create_deepflow_agent
    
    agent = create_deepflow_agent(
        user_id="test-user-123",
        user_state="IDLE",
        verbose=True
    )
    
    print(f"   ✅ Agent created: {type(agent).__name__}")
    # Note: LangGraph CompiledStateGraph doesn't expose tools directly
    print(f"   Agent type: LangGraph CompiledStateGraph")
    
    return agent


async def test_agent_processing():
    """Test agent message processing (without actual Redis)."""
    print("\n🧪 Testing agent message processing...")
    print("   (Note: Redis operations may fail if not configured)")
    
    from deepflow_agent.agents import process_message
    
    # Test case: Urgent message in IDLE state
    test_case = {
        "user_id": "test-user-123",
        "user_state": "IDLE",
        "message_content": "🚨 URGENT: Production database is down! All services affected.",
        "sender": "DevOps Alert System",
        "source": "slack",
    }
    
    print(f"\n   📩 Test message: {test_case['message_content'][:50]}...")
    print(f"   👤 User state: {test_case['user_state']}")
    
    try:
        result = await process_message(
            user_id=test_case["user_id"],
            user_state=test_case["user_state"],
            message_content=test_case["message_content"],
            sender=test_case["sender"],
            source=test_case["source"],
            verbose=True
        )
        
        print(f"\n   📤 Agent output:")
        print(f"   {result.get('output', 'No output')[:200]}...")
        
        return result
        
    except Exception as e:
        print(f"\n   ⚠️ Agent processing error: {e}")
        print("   (This is expected if Redis is not configured)")
        return None


def test_priority_scoring():
    """Test priority score calculation."""
    print("\n📊 Testing priority scoring...")
    
    from deepflow_agent.tools.base import calculate_priority_score
    
    test_cases = [
        {"urgency": 10, "estimated_minutes": 5, "expected_high": True},
        {"urgency": 5, "estimated_minutes": 30, "expected_high": False},
        {"urgency": 1, "estimated_minutes": 60, "expected_high": False},
    ]
    
    for case in test_cases:
        score = calculate_priority_score(
            urgency=case["urgency"],
            estimated_minutes=case["estimated_minutes"]
        )
        status = "✅" if (score > 30) == case["expected_high"] else "❌"
        print(f"   {status} Urgency {case['urgency']}, {case['estimated_minutes']}min → Score: {score}")


def main():
    """Run all tests."""
    print(f"\n🔧 Config:")
    print(f"   API Base: {os.getenv('OPENAI_API_BASE')}")
    print(f"   Model: {os.getenv('LLM_MODEL')}")
    print(f"   Redis: {'Configured' if os.getenv('UPSTASH_REDIS_REST_URL') else 'Not configured'}")
    
    # Run tests
    test_tool_imports()
    test_priority_scoring()
    test_agent_creation()
    
    # Only run async test if Redis is configured
    if os.getenv("UPSTASH_REDIS_REST_URL"):
        asyncio.run(test_agent_processing())
    else:
        print("\n⚠️ Skipping agent processing test (Redis not configured)")
        print("   Set UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN to enable")
    
    print("\n" + "=" * 60)
    print("✅ Tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
