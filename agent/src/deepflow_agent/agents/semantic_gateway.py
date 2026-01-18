"""
Semantic Gateway Agent

Analyzes incoming messages and converts them to structured tasks.
"""

import json
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from ..config import get_settings
from ..models import SemanticGatewayInput, SemanticGatewayOutput, TaskCategory
from ..prompts import SEMANTIC_GATEWAY_SYSTEM, SEMANTIC_GATEWAY_USER


class SemanticGatewayAgent:
    """
    Agent that analyzes messages and extracts structured task information.
    """

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        settings = get_settings()

        if llm:
            self.llm = llm
        else:
            self.llm = ChatOpenAI(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                api_key=settings.openai_api_key,
                base_url=settings.openai_api_base if settings.openai_api_base != "https://api.openai.com/v1" else None,
            )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SEMANTIC_GATEWAY_SYSTEM),
            ("user", SEMANTIC_GATEWAY_USER),
        ])

        self.chain = self.prompt | self.llm | StrOutputParser()

    async def analyze(self, input: SemanticGatewayInput) -> SemanticGatewayOutput:
        """
        Analyze a message and return structured task information.
        """
        response = await self.chain.ainvoke({
            "user_state": input.user_state,
            "sender": input.sender,
            "content": input.content,
        })

        # Parse JSON response
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            # Fallback for malformed JSON
            data = {
                "urgency_score": 5,
                "category": "standard",
                "summary": input.content[:200],
                "suggested_action": "Review this message",
                "estimated_time_minutes": 15,
                "context_tags": [],
            }

        return SemanticGatewayOutput(
            urgency_score=data.get("urgency_score", 5),
            category=data.get("category", "standard"),
            summary=data.get("summary", "")[:200],
            suggested_action=data.get("suggested_action", "")[:300],
            estimated_time_minutes=data.get("estimated_time_minutes", 15),
            context_tags=data.get("context_tags", []),
        )

    def analyze_sync(self, input: SemanticGatewayInput) -> SemanticGatewayOutput:
        """Synchronous version of analyze."""
        import asyncio
        return asyncio.run(self.analyze(input))


def create_semantic_gateway(llm: Optional[ChatOpenAI] = None) -> SemanticGatewayAgent:
    """Factory function to create SemanticGatewayAgent."""
    return SemanticGatewayAgent(llm)
