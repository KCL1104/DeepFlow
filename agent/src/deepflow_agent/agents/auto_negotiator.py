"""
Auto Negotiator Agent

Generates automatic replies when user is in focus mode.
"""

import json
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from ..config import get_settings
from ..models import AutoNegotiatorOutput
from ..prompts import AUTO_NEGOTIATOR_SYSTEM, AUTO_NEGOTIATOR_USER


class AutoNegotiatorAgent:
    """
    Agent that generates polite auto-replies for non-urgent messages.
    """

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        settings = get_settings()

        if llm:
            self.llm = llm
        else:
            self.llm = ChatOpenAI(
                model=settings.llm_model,
                temperature=0.7,  # Slightly creative for natural replies
                api_key=settings.openai_api_key,
                base_url=settings.openai_api_base if settings.openai_api_base != "https://api.openai.com/v1" else None,
            )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", AUTO_NEGOTIATOR_SYSTEM),
            ("user", AUTO_NEGOTIATOR_USER),
        ])

        self.chain = self.prompt | self.llm | StrOutputParser()

    async def generate_reply(
        self,
        content: str,
        sender: str,
        urgency_score: int,
        summary: str,
        user_state: str = "FLOW",
    ) -> AutoNegotiatorOutput:
        """
        Decide if an auto-reply should be sent and generate it.
        """
        # High urgency messages bypass auto-reply
        if urgency_score >= 8:
            return AutoNegotiatorOutput(
                should_reply=False,
                reply_message="",
                escalation_hint="",
            )

        response = await self.chain.ainvoke({
            "user_state": user_state,
            "sender": sender,
            "urgency_score": urgency_score,
            "summary": summary,
            "content": content,
        })

        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            data = {
                "should_reply": True,
                "reply_message": f"Hi {sender}, I'm currently in a focused work session. I'll get back to you soon. If urgent, please reply with 'URGENT'.",
                "escalation_hint": "Reply 'URGENT' to bypass this filter",
            }

        return AutoNegotiatorOutput(
            should_reply=data.get("should_reply", True),
            reply_message=data.get("reply_message", ""),
            escalation_hint=data.get("escalation_hint", "Reply 'URGENT' to bypass"),
        )

    def generate_reply_sync(
        self,
        content: str,
        sender: str,
        urgency_score: int,
        summary: str,
        user_state: str = "FLOW",
    ) -> AutoNegotiatorOutput:
        """Synchronous version of generate_reply."""
        import asyncio
        return asyncio.run(
            self.generate_reply(content, sender, urgency_score, summary, user_state)
        )


def create_auto_negotiator(llm: Optional[ChatOpenAI] = None) -> AutoNegotiatorAgent:
    """Factory function to create AutoNegotiatorAgent."""
    return AutoNegotiatorAgent(llm)
