#!/usr/bin/env python
"""
Evaluate Prompt with Email Dataset

Quick evaluation script to test the semantic gateway prompt
against the email dataset.
"""

import os
import json
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


def load_email_dataset():
    dataset_path = Path(__file__).parent.parent / "tests" / "fixtures" / "email_dataset.json"
    with open(dataset_path, encoding="utf-8") as f:
        return json.load(f)


def load_prompt():
    import sys
    src_path = str(Path(__file__).parent.parent / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    from deepflow_agent.prompts.semantic_gateway import (
        SEMANTIC_GATEWAY_SYSTEM,
        SEMANTIC_GATEWAY_USER
    )
    return SEMANTIC_GATEWAY_SYSTEM, SEMANTIC_GATEWAY_USER


def evaluate_single(llm, case, system_template, user_template):
    """Evaluate a single case."""
    input_data = case["input"]
    expected = case["expected"]
    
    user_state = input_data.get("user_state", "IDLE")
    sender = input_data.get("sender", input_data.get("sender_name", "unknown"))
    content = input_data["content"]
    
    system = system_template.format(user_state=user_state)
    user = user_template.format(
        sender=sender,
        user_state=user_state,
        content=content
    )
    
    messages = [
        SystemMessage(content=system),
        HumanMessage(content=user)
    ]
    
    try:
        response = llm.invoke(messages)
        result = json.loads(response.content)
        predicted_urgency = result.get("urgency_score", 5)
        predicted_category = result.get("category", "standard")
    except Exception as e:
        predicted_urgency = 5
        predicted_category = "standard"
    
    expected_urgency = expected["urgency_score"]
    expected_category = expected["category"]
    
    urgency_diff = abs(predicted_urgency - expected_urgency)
    urgency_acc = max(0, 1 - urgency_diff / 10)
    category_match = 1.0 if predicted_category == expected_category else 0.0
    combined = 0.7 * urgency_acc + 0.3 * category_match
    
    return {
        "id": case.get("id", "unknown"),
        "predicted_urgency": predicted_urgency,
        "expected_urgency": expected_urgency,
        "predicted_category": predicted_category,
        "expected_category": expected_category,
        "urgency_acc": urgency_acc,
        "category_match": category_match,
        "combined": combined,
        "scenario": case.get("metadata", {}).get("scenario", "unknown"),
        "language": case.get("metadata", {}).get("language", "unknown")
    }


def run_evaluation(sample_size: int = 25):
    """Run evaluation on email dataset."""
    print("=" * 60)
    print("📊 Evaluating Semantic Gateway Prompt with Email Dataset")
    print("=" * 60)
    
    # Load
    all_cases = load_email_dataset()
    system_template, user_template = load_prompt()
    
    # Sample
    step = max(1, len(all_cases) // sample_size)
    cases = all_cases[::step][:sample_size]
    print(f"\n📋 Evaluating {len(cases)} cases (sampled from {len(all_cases)})")
    
    # Init LLM
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    
    print(f"🤖 Model: {model}")
    
    llm = ChatOpenAI(
        model=model,
        temperature=0,
        api_key=api_key,
        base_url=api_base if api_base else None
    )
    
    # Evaluate
    results = []
    print("\n" + "-" * 60)
    
    for i, case in enumerate(cases):
        result = evaluate_single(llm, case, system_template, user_template)
        results.append(result)
        
        status = "✅" if result["combined"] >= 0.7 else "❌"
        print(f"{status} [{result['id']}] U:{result['predicted_urgency']} vs {result['expected_urgency']} | C:{result['predicted_category']} vs {result['expected_category']} | Score:{result['combined']:.2f}")
    
    # Aggregate
    print("\n" + "=" * 60)
    print("📈 Results Summary")
    print("=" * 60)
    
    avg_urgency = sum(r["urgency_acc"] for r in results) / len(results)
    avg_category = sum(r["category_match"] for r in results) / len(results)
    avg_combined = sum(r["combined"] for r in results) / len(results)
    
    failures = [r for r in results if r["combined"] < 0.7]
    
    print(f"Avg Urgency Accuracy: {avg_urgency:.1%}")
    print(f"Avg Category Match:   {avg_category:.1%}")
    print(f"Avg Combined Score:   {avg_combined:.1%}")
    print(f"Pass Rate (>=70%):    {(len(results) - len(failures)) / len(results):.1%}")
    print(f"Failures:             {len(failures)}/{len(results)}")
    
    # By scenario
    print("\n📊 By Scenario:")
    scenarios = {}
    for r in results:
        s = r["scenario"]
        if s not in scenarios:
            scenarios[s] = []
        scenarios[s].append(r["combined"])
    
    for s, scores in sorted(scenarios.items()):
        avg = sum(scores) / len(scores)
        print(f"  {s}: {avg:.1%} ({len(scores)} cases)")
    
    # Save
    output_path = Path(__file__).parent / "email_evaluation_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_cases": len(results),
            "avg_urgency_accuracy": avg_urgency,
            "avg_category_match": avg_category,
            "avg_combined_score": avg_combined,
            "failures": len(failures),
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved to: {output_path}")
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-size", type=int, default=25)
    args = parser.parse_args()
    
    run_evaluation(sample_size=args.sample_size)
