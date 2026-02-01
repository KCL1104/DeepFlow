#!/usr/bin/env python
"""
Opik HRPO Optimizer with Email Dataset

Runs HRPO optimization using the comprehensive email dataset
that includes critical, customer, executive, meeting, and code review scenarios.

Based on the working optimize_hrpo.py script.
"""

import os
import json
from pathlib import Path

# Load .env first
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

# Monkey-patch the tqdm issue BEFORE importing opik
def apply_tqdm_fix():
    """Fix the tqdm/rich compatibility issue in opik."""
    try:
        import opik.evaluation.engine.evaluation_tasks_executor as executor_module
        from tqdm import tqdm
        
        def fixed_tqdm(iterable=None, **kwargs):
            if iterable is None:
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

import opik
from opik.evaluation.metrics import score_result
from opik_optimizer import ChatPrompt, HierarchicalReflectiveOptimizer


def load_email_dataset():
    """Load the comprehensive email dataset."""
    dataset_path = Path(__file__).parent.parent / "tests" / "fixtures" / "email_dataset.json"
    with open(dataset_path, encoding="utf-8") as f:
        return json.load(f)


# Get model from env - LiteLLM requires openai/ prefix for custom endpoints
_base_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
TARGET_MODEL = f"openai/{_base_model}"


def get_initial_prompt():
    """Get the initial prompt to optimize from."""
    return ChatPrompt(
        messages=[
            {
                "role": "system",
                "content": """You are DeepFlow Sentinel, an elite executive assistant.
Your job is to analyze incoming messages and rate their urgency on a scale of 0-10.

## Urgency Scale:
- 10: Critical Infrastructure Failure, Legal Emergency, Health Crisis, 系統掛掉, 線上掛了
- 9: Production outage, Security breach, CEO/高層 demands, 老闆緊急要, 五分鐘內
- 8: Client escalation, Blocking bugs, 客戶威脅取消, production bug, blocking, VIP 客戶
- 7: Important deadlines (within 2 hours), Deployment issues, CI/CD failure, 即將到期
- 6: Meeting reminders (今天), Time-sensitive requests, today EOD, 今天結束前
- 5: Standard work requests, 一般工作詢問, review PR
- 4: Non-urgent tasks, PR reviews (無急迫), 有空看
- 3: FYI messages, Documentation updates, 政策更新
- 2: Social messages, Team events, 社交邀約, 聚餐
- 1: Newsletters, 廣告
- 0: Complete noise, spam

## CRITICAL Urgency Keywords (多語言):
### HIGH URGENCY (7-10):
- "緊急", "URGENT", "P0", "critical", "ASAP", "馬上", "立即"
- "掛了", "down", "outage", "系統掛", "crashes", "CrashLoopBackOff"
- "blocking", "blocked", "阻塞", "失敗"
- "老闆", "CEO", "CFO", "CTO", "investor", "投資人", "board meeting"
- "今天", "EOD", "30分鐘", "within hours", "5 minutes"
- "production", "prod bug", "線上問題"
- "客戶威脅", "threatening to cancel", "取消合約"
- "VIP", "Fortune 500", "enterprise"

### MEDIUM URGENCY (4-6):
- "SLA", "response time", "performance"
- "demo", "meeting", "會議"
- "review", "approve"

### LOW URGENCY (0-3):
- "不急", "no rush", "when you can", "有空"
- "FYI", "供參考"
- "聚餐", "lunch", "social"
- "newsletter", "廣告", "免費"
- "reschedule", "next week", "下週"

## Category Mapping (CRITICAL):
- Urgency 10-9: critical
- Urgency 8-6: urgent  
- Urgency 5-4: standard
- Urgency 3-2: low
- Urgency 1-0: discard

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


def prepare_opik_items(sample_size: int = 30):
    """Prepare items for Opik dataset."""
    all_cases = load_email_dataset()
    
    # Sample to get diversity
    step = max(1, len(all_cases) // sample_size)
    sampled = all_cases[::step][:sample_size]
    
    items = []
    for item in sampled:
        items.append({
            "content": item["input"]["content"],
            "sender": item["input"].get("sender", item["input"].get("sender_name", "unknown")),
            "user_state": item["input"].get("user_state", "IDLE"),
            "expected": item["expected"]
        })
    return items


def run_optimization(max_trials: int = 3, sample_size: int = 30):
    """Run optimization."""
    print("=" * 60)
    print("🚀 DeepFlow - Opik HRPO Optimization (Email Dataset)")
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
    dataset_name = f"email-dataset-v3-{sample_size}"
    try:
        dataset = client.get_dataset(name=dataset_name)
        print(f"📊 Using existing dataset: {dataset_name}")
    except:
        dataset = client.create_dataset(name=dataset_name)
        items = prepare_opik_items(sample_size)
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
        project_name="DeepFlow-Email",
    )
    
    print("\n📈 Results:")
    result.display()
    
    # Get the optimized prompt using the correct API
    optimized_prompt = result.apply_to_prompt(initial_prompt)
    
    # Save
    output_path = Path(__file__).parent / "optimized_prompt_email.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "version": "3.0-email",
            "optimized_by": "HRPO with Email Dataset",
            "dataset_size": sample_size,
            "messages": optimized_prompt.messages,
            "model": optimized_prompt.model,
            "run_link": result.get_run_link() if hasattr(result, 'get_run_link') else None,
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved to: {output_path}")
    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-trials", type=int, default=3)
    parser.add_argument("--sample-size", type=int, default=30)
    args = parser.parse_args()
    
    run_optimization(max_trials=args.max_trials, sample_size=args.sample_size)
