#!/usr/bin/env python
"""
Run Agent Evaluation

Runs the Semantic Gateway Agent against the golden dataset
and reports evaluation metrics using Opik.
"""

import asyncio
import json
from pathlib import Path

from deepflow_agent.agents import create_semantic_gateway
from deepflow_agent.models import SemanticGatewayInput, TaskSource
from deepflow_agent.tracer import init_opik


def load_golden_dataset():
    """Load golden dataset from fixtures."""
    fixtures_path = Path(__file__).parent.parent / "tests" / "fixtures" / "golden_dataset.json"
    with open(fixtures_path) as f:
        return json.load(f)


def calculate_accuracy(predictions: list, expected: list) -> dict:
    """Calculate evaluation metrics."""
    total = len(predictions)
    if total == 0:
        return {"total": 0}

    urgency_diffs = []
    category_matches = 0

    for pred, exp in zip(predictions, expected):
        # Urgency difference
        urgency_diffs.append(abs(pred["urgency_score"] - exp["urgency_score"]))

        # Category match
        if pred["category"] == exp["category"]:
            category_matches += 1

    return {
        "total": total,
        "avg_urgency_diff": sum(urgency_diffs) / total,
        "urgency_accuracy": 1 - (sum(urgency_diffs) / (total * 10)),
        "category_accuracy": category_matches / total,
    }


async def run_evaluation():
    """Run evaluation against golden dataset."""
    print("🧪 DeepFlow Agent Evaluation")
    print("=" * 50)

    # Initialize Opik
    opik_ready = init_opik()

    # Load dataset
    dataset = load_golden_dataset()
    print(f"📁 Loaded {len(dataset)} test cases")

    # Create agent
    agent = create_semantic_gateway()

    predictions = []
    expected_list = []

    for case in dataset:
        test_id = case["id"]
        input_data = case["input"]
        expected = case["expected"]

        print(f"\n📝 Running {test_id}...")

        # Create input
        agent_input = SemanticGatewayInput(
            content=input_data["content"],
            sender=input_data["sender"],
            source=TaskSource(input_data.get("source", "manual")),
            user_state=input_data.get("user_state", "IDLE"),
        )

        try:
            result = await agent.analyze(agent_input)
            pred = {
                "urgency_score": result.urgency_score,
                "category": result.category,
                "summary": result.summary,
            }
            print(f"   Predicted: urgency={pred['urgency_score']}, category={pred['category']}")
            print(f"   Expected:  urgency={expected['urgency_score']}, category={expected['category']}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            pred = {"urgency_score": 5, "category": "standard"}

        predictions.append(pred)
        expected_list.append(expected)

    # Calculate metrics
    metrics = calculate_accuracy(predictions, expected_list)

    print("\n" + "=" * 50)
    print("📊 Evaluation Results")
    print("=" * 50)
    print(f"Total test cases: {metrics['total']}")
    print(f"Urgency Accuracy: {metrics['urgency_accuracy']:.2%}")
    print(f"Category Accuracy: {metrics['category_accuracy']:.2%}")
    print(f"Avg Urgency Diff: {metrics['avg_urgency_diff']:.2f}")

    return metrics


if __name__ == "__main__":
    asyncio.run(run_evaluation())
