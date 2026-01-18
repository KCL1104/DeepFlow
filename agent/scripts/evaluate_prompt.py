#!/usr/bin/env python
"""
Manual Prompt Optimization with Opik Tracking

This script manually implements prompt optimization with 
Opik tracking, bypassing opik-optimizer's internal issues.
"""

import json
import os
from pathlib import Path
from typing import Callable

# Load .env
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

import opik
from opik import track
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


# Load golden dataset
def load_golden_dataset():
    dataset_path = Path(__file__).parent.parent / "tests" / "fixtures" / "golden_dataset.json"
    with open(dataset_path) as f:
        return json.load(f)


# Current prompt template
SYSTEM_PROMPT = """You are DeepFlow Sentinel, an elite executive assistant.
Your job is to analyze incoming messages and rate their urgency on a scale of 0-10.

## Urgency Scale:
- 10: Critical Infrastructure Failure, Legal Emergency, Health Crisis
- 9: Production outage, Security breach, CEO/高層 demands
- 8: Client escalation, Blocking bugs, 客戶威脅
- 7: Important deadlines, Deployment issues
- 6: Meeting reminders (即將開始), Time-sensitive requests
- 5: Standard work requests, 一般工作詢問
- 4: Non-urgent tasks, PR reviews (無急迫)
- 3: FYI messages, Documentation updates
- 2: Social messages, Team events, 社交邀約
- 1: Newsletters, Spam, 廣告

## Language Note:
Messages may be in Chinese, English, or mixed. Treat urgency keywords equally:
- "緊急", "URGENT", "P0", "critical" → High urgency
- "不急", "no rush", "when you can" → Lower urgency

## User State Context:
The user is in "{user_state}" state:
- FLOW: Deep focus. Only urgency >= 9 should interrupt.
- SHALLOW: Light work. Urgency >= 6 should interrupt.
- IDLE: Available. All notifications allowed.

## Response Format:
Respond with ONLY a JSON object:
{{
  "urgency_score": <int 0-10>,
  "category": "<critical|urgent|standard|low|discard>",
  "summary": "<brief summary in same language as input>",
  "should_interrupt": <true/false based on urgency and user_state>
}}"""


USER_PROMPT = """Analyze this message:

From: {sender}
User State: {user_state}

Message:
{content}

Respond with JSON only."""


@track(name="evaluate_prompt")
def evaluate_single_case(
    llm: ChatOpenAI,
    case: dict,
    system_prompt: str,
    user_prompt: str
) -> dict:
    """Evaluate a single test case."""
    input_data = case["input"]
    expected = case["expected"]
    
    # Format prompts
    system = system_prompt.format(user_state=input_data.get("user_state", "IDLE"))
    user = user_prompt.format(
        content=input_data["content"],
        sender=input_data["sender"],
        user_state=input_data.get("user_state", "IDLE")
    )
    
    # Call LLM
    messages = [
        SystemMessage(content=system),
        HumanMessage(content=user)
    ]
    
    response = llm.invoke(messages)
    
    # Parse response
    try:
        output = json.loads(response.content)
        predicted_urgency = output.get("urgency_score", 5)
        predicted_category = output.get("category", "standard")
    except (json.JSONDecodeError, AttributeError):
        predicted_urgency = 5
        predicted_category = "standard"
    
    # Calculate scores
    expected_urgency = expected["urgency_score"]
    expected_category = expected["category"]
    
    urgency_diff = abs(predicted_urgency - expected_urgency)
    urgency_accuracy = max(0, 1 - (urgency_diff / 10))
    category_match = 1.0 if predicted_category == expected_category else 0.0
    
    combined_score = 0.7 * urgency_accuracy + 0.3 * category_match
    
    return {
        "case_id": case["id"],
        "predicted_urgency": predicted_urgency,
        "expected_urgency": expected_urgency,
        "predicted_category": predicted_category,
        "expected_category": expected_category,
        "urgency_accuracy": urgency_accuracy,
        "category_match": category_match,
        "combined_score": combined_score
    }


@track(name="evaluate_all_cases")
def evaluate_all_cases(
    llm: ChatOpenAI,
    dataset: list,
    system_prompt: str,
    user_prompt: str
) -> dict:
    """Evaluate all test cases and return aggregated results."""
    results = []
    
    for case in dataset:
        result = evaluate_single_case(llm, case, system_prompt, user_prompt)
        results.append(result)
        print(f"   {result['case_id']}: urgency {result['predicted_urgency']} vs {result['expected_urgency']} | score={result['combined_score']:.2f}")
    
    # Aggregate
    avg_urgency_accuracy = sum(r["urgency_accuracy"] for r in results) / len(results)
    avg_category_match = sum(r["category_match"] for r in results) / len(results)
    avg_combined = sum(r["combined_score"] for r in results) / len(results)
    
    # Find failures (score < 0.7)
    failures = [r for r in results if r["combined_score"] < 0.7]
    
    return {
        "total_cases": len(results),
        "avg_urgency_accuracy": avg_urgency_accuracy,
        "avg_category_match": avg_category_match,
        "avg_combined_score": avg_combined,
        "failures": failures,
        "results": results
    }


def run_evaluation():
    """Run the prompt evaluation."""
    print("=" * 60)
    print("🚀 DeepFlow Prompt Evaluation (with Opik Tracking)")
    print("=" * 60)
    
    # Load dataset
    dataset = load_golden_dataset()
    print(f"\n📊 Loaded {len(dataset)} test cases")
    
    # Initialize Opik
    opik.configure(use_local=False)
    os.environ["OPIK_PROJECT_NAME"] = "DeepFlow"
    
    # Initialize LLM
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    model = os.getenv("LLM_MODEL", "gpt-4-turbo")
    
    print(f"\n🤖 Using model: {model}")
    
    llm = ChatOpenAI(
        model=model,
        temperature=0,
        api_key=api_key,
        base_url=api_base if api_base != "https://api.openai.com/v1" else None,
    )
    
    # Run evaluation
    print(f"\n📝 Evaluating current prompt...")
    results = evaluate_all_cases(llm, dataset, SYSTEM_PROMPT, USER_PROMPT)
    
    # Print results
    print("\n" + "=" * 60)
    print("📈 Evaluation Results")
    print("=" * 60)
    print(f"Total Cases: {results['total_cases']}")
    print(f"Avg Urgency Accuracy: {results['avg_urgency_accuracy']:.2%}")
    print(f"Avg Category Match: {results['avg_category_match']:.2%}")
    print(f"Avg Combined Score: {results['avg_combined_score']:.2%}")
    print(f"Failures (<70%): {len(results['failures'])} cases")
    
    if results['failures']:
        print(f"\n❌ Failed cases:")
        for f in results['failures'][:10]:  # Show first 10
            print(f"   {f['case_id']}: predicted={f['predicted_urgency']}, expected={f['expected_urgency']}")
    
    # Save results
    output_path = Path(__file__).parent / "evaluation_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {output_path}")
    print(f"\n👉 View traces: https://www.comet.com/opik")
    
    return results


if __name__ == "__main__":
    run_evaluation()
