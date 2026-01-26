#!/usr/bin/env python
"""
Opik HRPO Optimizer with Extended Dataset

Runs HRPO optimization using the extended golden dataset
that includes Chinese, Tool-specific, and mixed-language cases.
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

apply_tqdm_fix()

import opik
from opik.evaluation.metrics import score_result
import opik_optimizer
from opik_optimizer import ChatPrompt, HierarchicalReflectiveOptimizer


def load_extended_dataset():
    """Load both original and extended datasets."""
    fixtures_path = Path(__file__).parent.parent / "tests" / "fixtures"
    
    all_cases = []
    
    # Load original (sample 20)
    original_path = fixtures_path / "golden_dataset.json"
    if original_path.exists():
        with open(original_path, encoding="utf-8") as f:
            original = json.load(f)
            # Sample every 3rd case to get ~20
            all_cases.extend(original[::3])
    
    # Load extended (all 20)
    extended_path = fixtures_path / "golden_dataset_extended.json"
    if extended_path.exists():
        with open(extended_path, encoding="utf-8") as f:
            all_cases.extend(json.load(f))
    
    return all_cases


# Get model from env
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
- 8: Client escalation, Blocking bugs, 客戶威脅取消, production bug, blocking
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
- "緊急", "URGENT", "P0", "critical", "ASAP", "馬上"
- "掛了", "down", "outage", "系統掛"
- "blocking", "blocked", "阻塞"
- "老闆", "CEO", "investor", "投資人"
- "今天", "EOD", "30分鐘", "within hours"
- "production", "prod bug", "線上問題"

### LOW URGENCY (0-3):
- "不急", "no rush", "when you can", "有空"
- "FYI", "供參考"
- "聚餐", "lunch", "social"
- "newsletter", "廣告", "免費"

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
  "summary": "<brief summary in same language as input>",
  "should_interrupt": <true/false>
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
        ]
    )


def urgency_accuracy_metric(output, reference):
    """Calculate urgency accuracy score."""
    try:
        result = json.loads(output)
        predicted = result.get("urgency_score", 5)
        expected = reference.get("urgency_score", 5)
        diff = abs(predicted - expected)
        accuracy = max(0, 1 - (diff / 10))
        return score_result(value=accuracy, name="urgency_accuracy")
    except:
        return score_result(value=0.5, name="urgency_accuracy")


def category_accuracy_metric(output, reference):
    """Calculate category accuracy score."""
    try:
        result = json.loads(output)
        predicted = result.get("category", "standard")
        expected = reference.get("category", "standard")
        match = 1.0 if predicted == expected else 0.0
        return score_result(value=match, name="category_accuracy")
    except:
        return score_result(value=0.0, name="category_accuracy")


def combined_score_metric(output, reference):
    """Combined score: 70% urgency + 30% category."""
    try:
        result = json.loads(output)
        
        # Urgency
        predicted_urgency = result.get("urgency_score", 5)
        expected_urgency = reference.get("urgency_score", 5)
        urgency_acc = max(0, 1 - abs(predicted_urgency - expected_urgency) / 10)
        
        # Category
        predicted_cat = result.get("category", "standard")
        expected_cat = reference.get("category", "standard")
        cat_acc = 1.0 if predicted_cat == expected_cat else 0.0
        
        combined = 0.7 * urgency_acc + 0.3 * cat_acc
        return score_result(value=combined, name="combined_score")
    except:
        return score_result(value=0.5, name="combined_score")


def create_opik_dataset(cases):
    """Create Opik dataset from test cases."""
    items = []
    for case in cases:
        items.append({
            "input": {
                "content": case["input"]["content"],
                "sender": case["input"]["sender"],
                "user_state": case["input"].get("user_state", "IDLE")
            },
            "expected": case["expected"]
        })
    return items


def run_optimization():
    """Run HRPO optimization with extended dataset."""
    print("=" * 60)
    print("🚀 DeepFlow HRPO Optimization (Extended Dataset)")
    print("=" * 60)
    
    # Load dataset
    cases = load_extended_dataset()
    print(f"\n📊 Loaded {len(cases)} total test cases")
    
    # Configure Opik
    opik.configure(use_local=False)
    os.environ["OPIK_PROJECT_NAME"] = "DeepFlow"
    
    # LiteLLM settings
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
    os.environ["OPENAI_API_BASE"] = os.getenv("OPENAI_API_BASE", "")
    
    print(f"\n🤖 Model: {TARGET_MODEL}")
    
    # Create HRPO optimizer
    optimizer = HierarchicalReflectiveOptimizer(
        model=TARGET_MODEL,
        project_name="DeepFlow",
        max_iterations=3,
        n_samples=min(15, len(cases))
    )
    
    # Create dataset
    dataset = create_opik_dataset(cases)
    
    # Task function
    def evaluate_task(prompt: ChatPrompt, input_data: dict) -> str:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage
        
        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE")
        
        llm = ChatOpenAI(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            temperature=0,
            api_key=api_key,
            base_url=api_base if api_base else None
        )
        
        # Format messages
        messages = []
        for msg in prompt.messages:
            content = msg["content"].format(**input_data)
            if msg["role"] == "system":
                messages.append(SystemMessage(content=content))
            else:
                messages.append(HumanMessage(content=content))
        
        response = llm.invoke(messages)
        return response.content
    
    # Scoring function
    def scoring_function(output, reference):
        return [combined_score_metric(output, reference)]
    
    print("\n🔧 Starting HRPO optimization...")
    print("-" * 60)
    
    # Run optimization
    try:
        result = optimizer.optimize(
            prompt=get_initial_prompt(),
            task=evaluate_task,
            scoring_function=scoring_function,
            dataset=dataset
        )
        
        print("\n" + "=" * 60)
        print("📈 Optimization Complete!")
        print("=" * 60)
        
        # Save optimized prompt
        output_path = Path(__file__).parent / "optimized_prompt_extended.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "version": "2.0-extended",
                "optimized_by": "HRPO with Extended Dataset",
                "messages": result.prompt.messages if hasattr(result, 'prompt') else [],
                "model": TARGET_MODEL
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved to: {output_path}")
        print(f"👉 View traces: https://www.comet.com/opik")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Optimization error: {e}")
        print("Saving current improved prompt manually...")
        
        # Save improved prompt manually
        improved = get_initial_prompt()
        output_path = Path(__file__).parent / "optimized_prompt_extended.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "version": "2.0-extended-manual",
                "optimized_by": "Manual improvement with extended keywords",
                "messages": improved.messages,
                "model": TARGET_MODEL,
                "note": "HRPO failed, saved improved initial prompt"
            }, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved improved prompt to: {output_path}")
        return None


if __name__ == "__main__":
    run_optimization()
