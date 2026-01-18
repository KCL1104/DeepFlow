#!/usr/bin/env python
"""
Opik Optimizer with tqdm fix

Monkey-patches the tqdm issue in opik before running optimization.
"""

import os
from pathlib import Path

# Load .env first
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

# Monkey-patch the tqdm issue BEFORE importing opik
def apply_tqdm_fix():
    """Fix the tqdm/rich compatibility issue in opik."""
    try:
        import opik.evaluation.engine.evaluation_tasks_executor as executor_module
        
        # Replace the problematic _tqdm function with standard tqdm
        from tqdm import tqdm
        
        def fixed_tqdm(iterable=None, **kwargs):
            if iterable is None:
                # Return a no-op progress bar when no iterable
                class NoOpProgress:
                    def update(self, n=1): pass
                    def close(self): pass
                    def __enter__(self): return self
                    def __exit__(self, *args): pass
                return NoOpProgress()
            return tqdm(iterable, **kwargs)
        
        executor_module._tqdm = fixed_tqdm
        print("✅ Applied tqdm fix")
        return True
    except Exception as e:
        print(f"⚠️ Could not apply tqdm fix: {e}")
        return False


# Apply fix before importing opik modules
apply_tqdm_fix()

import json
import opik
from opik.evaluation.metrics import score_result
import opik_optimizer
from opik_optimizer import ChatPrompt, HierarchicalReflectiveOptimizer


# Load golden dataset
def load_golden_dataset():
    dataset_path = Path(__file__).parent.parent / "tests" / "fixtures" / "golden_dataset.json"
    with open(dataset_path) as f:
        return json.load(f)


# Get model from env - LiteLLM requires openai/ prefix for custom endpoints
_base_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
TARGET_MODEL = f"openai/{_base_model}"

# Define the prompt
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

## Language Note:
Messages may be in Chinese, English, or mixed. Keywords like:
- "緊急", "URGENT", "P0", "critical", "掛了" → High urgency
- "不急", "no rush", "when you can" → Lower urgency

## User State Context:
The user is in "{user_state}" state:
- FLOW: Deep focus. Only urgency >= 9 should interrupt.
- SHALLOW: Light work. Urgency >= 6 should interrupt.
- IDLE: Available. All notifications allowed.

## Response Format (JSON only):
{{
  "urgency_score": <int 0-10>,
  "category": "<critical|urgent|standard|low|discard>",
  "summary": "<brief summary>",
  "should_interrupt": <true/false>
}}"""
            },
            {
                "role": "user",
                "content": """Analyze this message:
From: {sender}
User State: {user_state}
Message: {content}

Respond with JSON only."""
            }
        ],
        model=TARGET_MODEL
    )


def combined_metric(dataset_item: dict, llm_output: str) -> score_result.ScoreResult:
    """Combined metric: 70% urgency + 30% category accuracy."""
    try:
        output_data = json.loads(llm_output)
        predicted_urgency = output_data.get("urgency_score", 5)
        predicted_category = output_data.get("category", "standard")
    except (json.JSONDecodeError, AttributeError):
        predicted_urgency = 5
        predicted_category = "standard"
    
    expected = dataset_item.get("expected", {})
    expected_urgency = expected.get("urgency_score", 5)
    expected_category = expected.get("category", "standard")
    
    # Calculate scores
    diff = abs(predicted_urgency - expected_urgency)
    urgency_score = max(0, 1 - (diff / 10))
    category_score = 1.0 if predicted_category == expected_category else 0.0
    
    combined = 0.7 * urgency_score + 0.3 * category_score
    
    reason = f"Urgency: {predicted_urgency} vs {expected_urgency}, Category: {predicted_category} vs {expected_category}"
    
    return score_result.ScoreResult(
        name="combined_accuracy",
        value=combined,
        reason=reason
    )


def prepare_opik_items():
    """Prepare items for Opik dataset."""
    golden_data = load_golden_dataset()
    items = []
    for item in golden_data:
        items.append({
            "content": item["input"]["content"],
            "sender": item["input"]["sender"],
            "user_state": item["input"].get("user_state", "IDLE"),
            "expected": item["expected"]
        })
    return items


def run_optimization(max_trials: int = 3):
    """Run optimization."""
    print("=" * 60)
    print("🚀 DeepFlow - Opik HRPO Optimization")
    print("=" * 60)
    
    # Get API config from env
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    target_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    
    print(f"📋 Config:")
    print(f"   API Base: {api_base}")
    print(f"   Target Model: {target_model}")
    
    # For LiteLLM, use openai/ prefix for custom endpoints
    # Set the base URL as env var for LiteLLM
    os.environ["OPENAI_API_BASE"] = api_base
    os.environ["OPENAI_API_KEY"] = api_key
    
    # Optimizer uses the same model as target
    optimizer_model = f"openai/{target_model}"
    
    # Initialize client
    client = opik.Opik()
    
    # Create/get dataset
    dataset_name = "semantic-gateway-golden-v2"
    try:
        dataset = client.get_dataset(name=dataset_name)
        print(f"📊 Using existing dataset: {dataset_name}")
    except:
        dataset = client.create_dataset(name=dataset_name)
        items = prepare_opik_items()
        dataset.insert(items)
        print(f"📊 Created dataset with {len(items)} items")
    
    # Create optimizer - use same model from env with explicit api_base
    print(f"\n🔧 Creating HRPO optimizer with model: {optimizer_model}...")
    optimizer = HierarchicalReflectiveOptimizer(
        model=optimizer_model,
        model_parameters={
            "api_base": api_base,
            "api_key": api_key,
        },
        verbose=0,
        n_threads=2,
    )
    
    # Run
    print(f"\n⚡ Optimizing (max_trials={max_trials})...")
    initial_prompt = get_initial_prompt()
    
    result = optimizer.optimize_prompt(
        prompt=initial_prompt,
        dataset=dataset,
        metric=combined_metric,
        max_trials=max_trials,
        project_name="DeepFlow",
    )
    
    print("\n📈 Results:")
    result.display()
    
    # Save
    output_path = Path(__file__).parent / "optimized_prompt.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "messages": result.best_prompt.messages,
            "model": result.best_prompt.model,
            "score": result.best_score,
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved to: {output_path}")
    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-trials", type=int, default=3)
    args = parser.parse_args()
    
    run_optimization(max_trials=args.max_trials)
