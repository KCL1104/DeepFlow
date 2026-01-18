#!/usr/bin/env python
"""
Opik Agent Optimizer for Semantic Gateway

Uses HierarchicalReflectiveOptimizer to automatically improve
the Semantic Gateway prompt based on the golden dataset.
"""

import json
import os
from pathlib import Path

# Set environment variables before imports
os.environ.setdefault("OPENAI_API_KEY", "your-api-key")

import opik
from opik.evaluation.metrics import score_result
import opik_optimizer
from opik_optimizer import ChatPrompt, HierarchicalReflectiveOptimizer


# Load golden dataset
def load_golden_dataset():
    """Load the golden dataset from fixtures."""
    dataset_path = Path(__file__).parent.parent / "tests" / "fixtures" / "golden_dataset.json"
    with open(dataset_path) as f:
        return json.load(f)


# Get model from env
TARGET_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# Define the prompt to optimize
def get_initial_prompt():
    return ChatPrompt(
        messages=[
            {
                "role": "system",
                "content": """You are DeepFlow Sentinel, an elite executive assistant.
Your job is to analyze incoming messages and rate their urgency on a scale of 0-10.

## Urgency Scale:
- 10: Critical Infrastructure Failure, Legal Emergency, Health Crisis
- 9: Production outage, Security breach, CEO/高層 demands  
- 8: Client escalation, Blocking bugs, 客戶威脅
- 7: Important deadlines, Deployment issues, CI/CD failure
- 6: Meeting reminders (即將開始), Time-sensitive requests
- 5: Standard work requests, 一般工作詢問
- 4: Non-urgent tasks, PR reviews (無急迫)
- 3: FYI messages, Documentation updates
- 2: Social messages, Team events, 社交邀約
- 1: Newsletters, Spam, 廣告
- 0: Complete noise

## Language Note:
Messages may be in Chinese, English, or mixed. Keywords like:
- "緊急", "URGENT", "P0", "critical", "掛了" → High urgency
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
            },
            {
                "role": "user",
                "content": """Analyze this message:

From: {sender}
User State: {user_state}

Message:
{content}

Respond with JSON only."""
            }
        ],
        model=TARGET_MODEL
    )


def urgency_accuracy_metric(dataset_item: dict, llm_output: str) -> score_result.ScoreResult:
    """
    Measure how accurately the model predicted urgency score.
    
    Score = 1 - (|predicted - expected| / 10)
    """
    try:
        output_data = json.loads(llm_output)
        predicted = output_data.get("urgency_score", 5)
    except (json.JSONDecodeError, AttributeError):
        predicted = 5
    
    expected = dataset_item["expected"]["urgency_score"]
    diff = abs(predicted - expected)
    score = max(0, 1 - (diff / 10))
    
    return score_result.ScoreResult(
        name="urgency_accuracy",
        value=score,
        reason=f"Predicted {predicted}, expected {expected}, diff={diff}"
    )


def category_accuracy_metric(dataset_item: dict, llm_output: str) -> score_result.ScoreResult:
    """
    Measure if the model correctly categorized the message.
    """
    try:
        output_data = json.loads(llm_output)
        predicted = output_data.get("category", "standard")
    except (json.JSONDecodeError, AttributeError):
        predicted = "standard"
    
    expected = dataset_item["expected"]["category"]
    score = 1.0 if predicted == expected else 0.0
    
    return score_result.ScoreResult(
        name="category_accuracy",
        value=score,
        reason=f"Predicted '{predicted}', expected '{expected}'"
    )


def combined_metric(dataset_item: dict, llm_output: str) -> score_result.ScoreResult:
    """
    Combined metric: 70% urgency accuracy + 30% category accuracy
    """
    urgency_result = urgency_accuracy_metric(dataset_item, llm_output)
    category_result = category_accuracy_metric(dataset_item, llm_output)
    
    combined_score = 0.7 * urgency_result.value + 0.3 * category_result.value
    
    return score_result.ScoreResult(
        name="combined_accuracy",
        value=combined_score,
        reason=f"Urgency: {urgency_result.value:.2f}, Category: {category_result.value}"
    )


def prepare_opik_dataset():
    """Prepare the dataset in Opik format."""
    golden_data = load_golden_dataset()
    
    # Transform to Opik format
    opik_items = []
    for item in golden_data:
        opik_items.append({
            "content": item["input"]["content"],
            "sender": item["input"]["sender"],
            "user_state": item["input"].get("user_state", "IDLE"),
            "expected": item["expected"]
        })
    
    return opik_items


def run_optimization(max_trials: int = 10, project_name: str = "deepflow-semantic-gateway"):
    """Run the Opik prompt optimization."""
    print("=" * 60)
    print("🚀 DeepFlow Semantic Gateway - Opik Optimization")
    print("=" * 60)
    
    # Initialize Opik client
    client = opik.Opik()
    
    # Get or create dataset
    dataset_name = "semantic-gateway-golden"
    try:
        dataset = client.get_dataset(name=dataset_name)
        print(f"📊 Found existing dataset: {dataset_name}")
    except:
        dataset = client.create_dataset(name=dataset_name)
        print(f"📊 Created new dataset: {dataset_name}")
        
        # Insert items
        items = prepare_opik_dataset()
        dataset.insert(items)
        print(f"   Inserted {len(items)} items")
    
    # Create optimizer with verbose=0 to avoid tqdm issues
    print("\n🔧 Initializing HierarchicalReflectiveOptimizer...")
    optimizer = HierarchicalReflectiveOptimizer(
        model="gpt-4o",
        verbose=0,  # Disable progress bar to avoid tqdm bug
        n_threads=4,
    )
    
    # Run optimization
    print(f"\n⚡ Running optimization with max_trials={max_trials}...")
    initial_prompt = get_initial_prompt()
    result = optimizer.optimize_prompt(
        prompt=initial_prompt,
        dataset=dataset,
        metric=combined_metric,
        max_trials=max_trials,
        project_name=project_name,
    )
    
    # Display results
    print("\n" + "=" * 60)
    print("📈 Optimization Results")
    print("=" * 60)
    result.display()
    
    # Save optimized prompt
    output_path = Path(__file__).parent / "optimized_prompt.json"
    with open(output_path, "w") as f:
        json.dump({
            "messages": result.best_prompt.messages,
            "model": result.best_prompt.model,
            "score": result.best_score,
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved optimized prompt to: {output_path}")
    
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Optimize Semantic Gateway prompt")
    parser.add_argument("--max-trials", type=int, default=10, help="Max optimization trials")
    parser.add_argument("--project", type=str, default="deepflow-semantic-gateway", help="Opik project name")
    
    args = parser.parse_args()
    
    run_optimization(max_trials=args.max_trials, project_name=args.project)
