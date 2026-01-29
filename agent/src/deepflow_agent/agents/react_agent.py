"""
DeepFlow ReAct Agent

A ReAct (Reasoning + Acting) agent that can analyze messages and take actions
using the available tools.
"""

import os
from typing import Optional

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from ..config import get_settings
from ..tracer import init_opik
from .semantic_gateway import create_semantic_gateway
from ..tools import (
    add_to_queue,
    send_auto_reply,
    update_task_status,
    notify_user_tool,
    send_browser_notification,
)


# System prompt for the agent
AGENT_SYSTEM_PROMPT = """You are DeepFlow Sentinel, an intelligent executive assistant that protects users' focus time.

## User Context
- User ID: {user_id}
- Current State: {user_state}
- State Meanings:
  - FLOW: Deep focus mode. Only urgent (score >= 9) matters.
  - SHALLOW: Light work. Moderate urgency (score >= 6) is acceptable.
  - IDLE: Available. All notifications allowed.

## Recent Conversation History
{conversation_history}

## Your Decision Process
1. **Analyze** the incoming message for urgency (0-10) and category
2. **Consider** the conversation history for context
3. **Decide** what action to take based on user state and urgency
4. **Execute** the appropriate tool(s)

## Category Mapping (CRITICAL):
- Urgency 10-9: critical → Interrupt immediately if FLOW, always add to queue
- Urgency 8-6: urgent → Add to queue, check deadline for notification
- Urgency 5-4: standard → Add to queue, auto-reply if user is in FLOW
- Urgency 3-2: low → Add to queue with low priority
- Urgency 1-0: discard → Do not add to queue, optionally auto-reply

## Telegram Notification Rules:
- **Critical (urgency 10-9)**: ALWAYS send Telegram notification immediately
- **Urgent (urgency 8-6)**: Send Telegram notification ONLY if deadline is within 2 hours
- **Standard/Low (urgency 5-0)**: DO NOT send notification

## Tool Usage Guidelines
- Use `add_to_queue` to add tasks to the user's priority queue
- Use `send_auto_reply` when user is in FLOW and message is not urgent
- Use `send_telegram_notification` for critical items OR urgent items with tight deadlines
- Use `update_task_status` to update existing tasks
- Use `notify_user_tool` for system notifications (internal)

Be accurate. Misjudging urgency can either waste the user's focus time or cause them to miss critical issues.
"""


def create_deepflow_agent(
    user_id: str,
    user_state: str = "IDLE",
    verbose: bool = False,
    include_memory: bool = True
):
    """
    Create a DeepFlow agent with all tools.
    
    Args:
        user_id: The user's unique identifier
        user_state: Current user state (FLOW/SHALLOW/IDLE)
        verbose: Whether to print agent reasoning
        include_memory: Whether to include conversation history
    
    Returns:
        Agent ready to process messages
    """
    # Initialize Opik tracing
    init_opik()
    
    # Get settings
    settings = get_settings()
    
    # Get conversation history if enabled
    conversation_history = "No recent conversation history."
    if include_memory:
        try:
            from ..memory import get_conversation_memory
            memory = get_conversation_memory()
            conversation_history = memory.get_formatted_history(user_id, limit=5)
        except Exception as e:
            logger.debug(f"Could not load conversation history: {e}")
    
    # Initialize LLM
    llm = ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_api_base,
        temperature=0,  # Deterministic for consistent actions
    )
    
    # Available tools
    from ..tools import send_telegram_notification
    
    tools = [
        add_to_queue,
        send_auto_reply,
        update_task_status,
        notify_user_tool,
        send_telegram_notification,  # Primary notification method
        send_browser_notification,   # Fallback (SSE)
    ]
    
    # Format system prompt with user context and history
    system_prompt = AGENT_SYSTEM_PROMPT.format(
        user_id=user_id,
        user_state=user_state,
        conversation_history=conversation_history
    )
    
    # Create the agent using LangChain v1 API
    agent = create_agent(
        llm,
        tools,
        system_prompt=system_prompt,
    )
    
    return agent


async def process_message(
    user_id: str,
    user_state: str,
    message_content: str,
    sender: str,
    source: str = "manual",
    source_id: str = "",
    verbose: bool = False
) -> dict:
    """
    Process an incoming message through the DeepFlow agent.
    
    This is the main entry point for processing messages.
    
    Args:
        user_id: User's unique identifier
        user_state: Current state (FLOW/SHALLOW/IDLE)
        message_content: The message text to analyze
        sender: Who sent the message
        source: Where the message came from (slack/email/telegram/manual)
        source_id: Original message ID from the source
        verbose: Print reasoning
    
    Returns:
        Dict with agent's actions and final answer
    """
    # Create agents
    agent = create_deepflow_agent(
        user_id=user_id,
        user_state=user_state,
        verbose=verbose
    )
    
    gateway = create_semantic_gateway()
    
    # 1. Semantic Analysis
    from ..models import SemanticGatewayInput
    
    if verbose:
        print(f"Running Semantic Analysis on message from {sender}...")
        
    analysis = await gateway.analyze(SemanticGatewayInput(
        user_state=user_state,
        sender=sender,
        content=message_content
    ))
    
    if verbose:
        print(f"Analysis Result: Urgency={analysis.urgency_score}, Category={analysis.category}")
    
    # 2. Format input message with analysis
    input_message = {
        "role": "user",
        "content": f"""New message received:
From: {sender}
Source: {source}
Content: {message_content}

User ID: {user_id}
User State: {user_state}

**Semantic Analysis**:
- Urgency Score: {analysis.urgency_score}/10
- Category: {analysis.category}
- Summary: {analysis.summary}
- Suggested Action: {analysis.suggested_action}
- Context Tags: {", ".join(analysis.context_tags)}

Based on this analysis and the User State, execute the appropriate tool actions (add_to_queue, notifications, etc.)."""
    }
    
    # Run agent using LangGraph stream
    final_output = None
    tool_calls = []
    
    # Use metadata from analysis to enrich return value
    enriched_metadata = {
        "urgency_score": analysis.urgency_score,
        "category": analysis.category,
        "summary": analysis.summary
    }
    
    async for step in agent.astream({"messages": [input_message]}):
        if verbose:
            print(f"Step: {step}")
        
        # Collect tool calls and final output
        if "messages" in step:
            for msg in step["messages"]:
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    tool_calls.extend(msg.tool_calls)
                if hasattr(msg, "content") and msg.content:
                    final_output = msg.content
    
    return {
        "input": message_content,
        "output": final_output or "Agent completed",
        "tool_calls": tool_calls,
        "user_id": user_id,
        "user_state": user_state,
        "analysis": enriched_metadata
    }


def process_message_sync(
    user_id: str,
    user_state: str,
    message_content: str,
    sender: str,
    source: str = "manual",
    source_id: str = "",
    verbose: bool = False
) -> dict:
    """
    Synchronous version of process_message.
    """
    import asyncio
    return asyncio.run(process_message(
        user_id=user_id,
        user_state=user_state,
        message_content=message_content,
        sender=sender,
        source=source,
        source_id=source_id,
        verbose=verbose
    ))
