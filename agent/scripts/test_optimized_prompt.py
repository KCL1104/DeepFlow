#!/usr/bin/env python
"""
Simple test for optimized prompt

Tests the optimized prompt against a few cases to verify it works correctly.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load env
load_dotenv(Path(__file__).parent.parent / ".env")

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


def load_optimized_prompt():
    """Load the optimized prompt from JSON."""
    prompt_path = Path(__file__).parent / "optimized_prompt.json"
    with open(prompt_path) as f:
        return json.load(f)


def test_prompt():
    """Test the optimized prompt with a few cases."""
    print("=" * 60)
    print("🧪 Testing Optimized Prompt")
    print("=" * 60)
    
    # Load prompt
    prompt_data = load_optimized_prompt()
    system_content = prompt_data["messages"][0]["content"]
    user_template = prompt_data["messages"][1]["content"]
    
    print(f"✅ Loaded optimized prompt")
    print(f"   Key improvements: {prompt_data['key_improvements']}")
    
    # Initialize LLM
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    
    print(f"\n📡 Using model: {model}")
    print(f"   API Base: {api_base}")
    
    llm = ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=api_base,
        temperature=0,
    )
    
    # Test cases with expected category mapping
    test_cases = [
        {
            "name": "Critical (urgency 10)",
            "content": "🚨 URGENT: 生產環境資料庫全部掛了！無法連線！",
            "sender": "DevOps Alert",
            "user_state": "FLOW",
            "expected_category": "critical",
            "expected_urgency_range": (9, 10),
        },
        {
            "name": "Urgent (urgency 7)",
            "content": "CI/CD pipeline 失敗了，blocking PR merge",
            "sender": "GitHub Actions",
            "user_state": "SHALLOW",
            "expected_category": "urgent",
            "expected_urgency_range": (6, 8),
        },
        {
            "name": "Standard (urgency 5)",
            "content": "可以幫我 review 這個 PR 嗎？不急",
            "sender": "Colleague",
            "user_state": "IDLE",
            "expected_category": "standard",
            "expected_urgency_range": (4, 5),
        },
        {
            "name": "Low (urgency 2)",
            "content": "FYI: 下週五有部門聚餐",
            "sender": "HR Team",
            "user_state": "IDLE",
            "expected_category": "low",
            "expected_urgency_range": (2, 3),
        },
        {
            "name": "Discard (urgency 1)",
            "content": "限時特價！快來看看最新產品優惠！",
            "sender": "Marketing Newsletter",
            "user_state": "IDLE",
            "expected_category": "discard",
            "expected_urgency_range": (0, 1),
        },
    ]
    
    print(f"\n🔍 Running {len(test_cases)} test cases...\n")
    
    passed = 0
    failed = 0
    
    for i, case in enumerate(test_cases, 1):
        # Format messages
        formatted_system = system_content.format(user_state=case["user_state"])
        formatted_user = user_template.format(
            sender=case["sender"],
            user_state=case["user_state"],
            content=case["content"],
        )
        
        messages = [
            SystemMessage(content=formatted_system),
            HumanMessage(content=formatted_user),
        ]
        
        try:
            response = llm.invoke(messages)
            result = json.loads(response.content)
            
            urgency = result.get("urgency_score", -1)
            category = result.get("category", "unknown")
            
            # Check category mapping
            min_u, max_u = case["expected_urgency_range"]
            urgency_ok = min_u <= urgency <= max_u
            category_ok = category == case["expected_category"]
            
            if urgency_ok and category_ok:
                status = "✅ PASS"
                passed += 1
            else:
                status = "❌ FAIL"
                failed += 1
            
            print(f"{i}. {case['name']}")
            print(f"   {status}")
            print(f"   Urgency: {urgency} (expected {min_u}-{max_u})")
            print(f"   Category: {category} (expected {case['expected_category']})")
            print()
            
        except Exception as e:
            print(f"{i}. {case['name']}")
            print(f"   ❌ ERROR: {e}")
            print()
            failed += 1
    
    # Summary
    print("=" * 60)
    print(f"📊 Results: {passed}/{len(test_cases)} passed")
    if failed == 0:
        print("🎉 All tests passed! Optimized prompt is working correctly.")
    else:
        print(f"⚠️ {failed} tests failed. May need further tuning.")
    print("=" * 60)
    
    return passed, failed


if __name__ == "__main__":
    test_prompt()
