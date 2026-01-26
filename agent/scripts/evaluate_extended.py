#!/usr/bin/env python
"""
Evaluate Agent with Extended Dataset

Tests the agent prompt against both original and extended golden datasets.
"""

import json
import os
from pathlib import Path

# Load .env
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

import opik
from opik import track
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


def load_datasets():
    """Load both original and extended datasets."""
    fixtures_path = Path(__file__).parent.parent / "tests" / "fixtures"
    
    datasets = {
        "original": [],
        "extended": []
    }
    
    # Load original
    original_path = fixtures_path / "golden_dataset.json"
    if original_path.exists():
        with open(original_path, encoding="utf-8") as f:
            datasets["original"] = json.load(f)
    
    # Load extended
    extended_path = fixtures_path / "golden_dataset_extended.json"
    if extended_path.exists():
        with open(extended_path, encoding="utf-8") as f:
            datasets["extended"] = json.load(f)
    
    return datasets


# Updated prompt with multilingual support
SYSTEM_PROMPT = """You are DeepFlow Sentinel, an elite executive assistant.
Your job is to analyze incoming messages and rate their urgency on a scale of 0-10.

## Urgency Scale:
- 10: Critical Infrastructure Failure, Legal Emergency, Health Crisis, 系統掛掉
- 9: Production outage, Security breach, CEO/高層 demands, 老闆緊急需要
- 8: Client escalation, Blocking bugs, 客戶威脅取消合約
- 7: Important deadlines, Deployment issues, 即將到期的任務
- 6: Meeting reminders (即將開始), Time-sensitive requests, 今天 EOD
- 5: Standard work requests, 一般工作詢問, PR review
- 4: Non-urgent tasks, PR reviews (無急迫), 有空再看
- 3: FYI messages, Documentation updates, 政策更新
- 2: Social messages, Team events, 社交邀約, 聚餐
- 1: Newsletters, Spam, 廣告, 垃圾郵件
- 0: Completely spam or irrelevant

## Language Note:
Messages may be in Chinese (繁體/簡體), English, or mixed. Treat urgency keywords equally:
- "緊急", "URGENT", "P0", "critical", "馬上", "ASAP" → High urgency
- "不急", "no rush", "when you can", "有空", "方便時" → Lower urgency
- "production上", "系統掛了", "客戶抱怨" → High urgency

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


@track(name="evaluate_case")
def evaluate_single_case(llm: ChatOpenAI, case: dict) -> dict:
    """Evaluate a single test case."""
    input_data = case["input"]
    expected = case["expected"]
    
    # Format prompts
    system = SYSTEM_PROMPT.format(user_state=input_data.get("user_state", "IDLE"))
    user = USER_PROMPT.format(
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
        "input_preview": input_data["content"][:50],
        "predicted_urgency": predicted_urgency,
        "expected_urgency": expected_urgency,
        "predicted_category": predicted_category,
        "expected_category": expected_category,
        "urgency_accuracy": urgency_accuracy,
        "category_match": category_match,
        "combined_score": combined_score
    }


def run_evaluation():
    """Run the full evaluation."""
    print("=" * 60)
    print("🚀 DeepFlow Prompt Evaluation (Extended Dataset)")
    print("=" * 60)
    
    # Load datasets
    datasets = load_datasets()
    original_count = len(datasets["original"])
    extended_count = len(datasets["extended"])
    
    print(f"\n📊 Datasets loaded:")
    print(f"   Original: {original_count} cases")
    print(f"   Extended: {extended_count} cases (中文 + Tool-specific)")
    print(f"   Total: {original_count + extended_count} cases")
    
    # Initialize Opik
    opik.configure(use_local=False)
    os.environ["OPIK_PROJECT_NAME"] = "DeepFlow"
    
    # Initialize LLM
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    model = os.getenv("LLM_MODEL", "gpt-4-turbo")
    
    print(f"\n🤖 Model: {model}")
    
    llm = ChatOpenAI(
        model=model,
        temperature=0,
        api_key=api_key,
        base_url=api_base if api_base != "https://api.openai.com/v1" else None,
    )
    
    # Evaluate extended dataset only (for speed)
    print(f"\n📝 Evaluating EXTENDED dataset ({extended_count} cases)...")
    print("-" * 60)
    
    extended_results = []
    for case in datasets["extended"]:
        result = evaluate_single_case(llm, case)
        extended_results.append(result)
        status = "✅" if result["combined_score"] >= 0.7 else "❌"
        print(f"   {status} {result['case_id']}: {result['predicted_urgency']} vs {result['expected_urgency']} | {result['combined_score']:.0%}")
    
    # Calculate metrics
    avg_urgency = sum(r["urgency_accuracy"] for r in extended_results) / len(extended_results)
    avg_category = sum(r["category_match"] for r in extended_results) / len(extended_results)
    avg_combined = sum(r["combined_score"] for r in extended_results) / len(extended_results)
    failures = [r for r in extended_results if r["combined_score"] < 0.7]
    
    # Print results
    print("\n" + "=" * 60)
    print("📈 Evaluation Results (Extended Dataset)")
    print("=" * 60)
    print(f"Total Cases: {len(extended_results)}")
    print(f"Avg Urgency Accuracy: {avg_urgency:.1%}")
    print(f"Avg Category Match: {avg_category:.1%}")
    print(f"Avg Combined Score: {avg_combined:.1%}")
    print(f"Passed (≥70%): {len(extended_results) - len(failures)}/{len(extended_results)}")
    print(f"Failed (<70%): {len(failures)} cases")
    
    if failures:
        print(f"\n❌ Failed cases:")
        for f in failures:
            print(f"   {f['case_id']}: predicted={f['predicted_urgency']}, expected={f['expected_urgency']}")
            print(f"      Input: {f['input_preview']}...")
    
    # Save results
    output_path = Path(__file__).parent / "extended_evaluation_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "metrics": {
                "avg_urgency_accuracy": avg_urgency,
                "avg_category_match": avg_category,
                "avg_combined_score": avg_combined,
                "total_cases": len(extended_results),
                "failures": len(failures)
            },
            "results": extended_results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {output_path}")
    print(f"👉 View traces: https://www.comet.com/opik")
    
    return extended_results


if __name__ == "__main__":
    run_evaluation()
