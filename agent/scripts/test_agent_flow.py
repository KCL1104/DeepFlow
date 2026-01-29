
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from deepflow_agent.agents.react_agent import process_message
from deepflow_agent.tools.base import get_redis_client

# Load env vars
load_dotenv()

async def test_critical_flow_interruption():
    """
    Test Case:
    User is in FLOW state.
    Incoming message is CRITICAL (Urgency 10).
    
    Expected Behavior:
    1. Agent detects high urgency.
    2. Agent calls 'add_to_queue' with urgency=10/critical.
    3. Agent calls 'send_telegram_notification' (since it's critical).
    """
    print("\n=== Test: Critical Flow Interruption ===")
    
    user_id = "test-user-flow"
    user_state = "FLOW"
    message = "SERVER DOWN: Production database is unreachable. Customers are impacted immediately."
    sender = "PagerDuty"
    
    print(f"Input: User={user_id}, State={user_state}")
    print(f"Message: {message}")
    
    result = await process_message(
        user_id=user_id,
        user_state=user_state,
        message_content=message,
        sender=sender,
        source="system",
        verbose=True
    )
    
    print("\n--- Agent Result ---")
    print(f"Output: {result['output']}")
    
    print("\n--- Tool Calls ---")
    tool_calls = result.get("tool_calls", [])
    
    has_queue = False
    has_notify = False
    
    for tc in tool_calls:
        print(f"- Tool: {tc.get('name')}")
        args = tc.get('args', {})
        print(f"  Args: {args}")
        
        if tc.get('name') == 'add_to_queue':
            if args.get('category') == 'critical' or args.get('urgency_score') >= 9:
                has_queue = True
        
        if tc.get('name') == 'send_telegram_notification':
            has_notify = True
            
    print("\n--- Verification ---")
    if has_queue and has_notify:
        print("✅ SUCCESS: Agent added to queue AND sent notification.")
    else:
        print("❌ FAILURE: Missing required actions.")
        print(f"   Queue: {has_queue}")
        print(f"   Notify: {has_notify}")

async def test_casual_flow_ignore():
    """
    Test Case:
    User is in FLOW state.
    Incoming message is CASUAL (Urgency ~2).
    
    Expected Behavior:
    1. Agent detects low urgency.
    2. Agent calls 'add_to_queue' (low priority) OR 'send_auto_reply'.
    3. Agent DOES NOT call 'send_telegram_notification'.
    """
    print("\n=== Test: Casual Message in Flow ===")
    
    user_id = "test-user-flow"
    user_state = "FLOW"
    message = "Hey, are we still on for lunch tomorrow?"
    sender = "Friend"
    
    print(f"Input: User={user_id}, State={user_state}")
    print(f"Message: {message}")
    
    result = await process_message(
        user_id=user_id,
        user_state=user_state,
        message_content=message,
        sender=sender,
        source="telegram",
        verbose=True
    )
    
    print("\n--- Agent Result ---")
    print(f"Output: {result['output']}")
    
    tool_calls = result.get("tool_calls", [])
    has_notify = False
    
    for tc in tool_calls:
        if tc.get('name') == 'send_telegram_notification':
            has_notify = True
            
    if not has_notify:
        print("✅ SUCCESS: Agent did NOT interrupt.")
    else:
        print("❌ FAILURE: Agent interrupted unnecessarily.")

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not set")
        sys.exit(1)
        
    asyncio.run(test_critical_flow_interruption())
    asyncio.run(test_casual_flow_ignore())
