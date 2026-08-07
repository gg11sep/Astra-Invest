"""AI agent base types and interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import UUID


class Recommendation(str, Enum):
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    WATCH = "WATCH"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


@dataclass
class AgentContext:
    """Shared context passed to every agent."""

    company_id: UUID | None = None
    symbol: str | None = None
    exchange: str | None = None
    company_data: dict[str, Any] = field(default_factory=dict)
    portfolio_data: dict[str, Any] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)
    user_question: str | None = None


@dataclass
class AgentResult:
    """Structured, explainable agent output."""

    agent_name: str
    recommendation: Recommendation
    confidence: float  # 0–1
    evidence: list[str] = field(default_factory=list)
    analysis: str = ""
    counter_arguments: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    catalysts: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "recommendation": self.recommendation.value,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "analysis": self.analysis,
            "counter_arguments": self.counter_arguments,
            "risks": self.risks,
            "catalysts": self.catalysts,
        }


class BaseAgent(ABC):
    """Every AI agent implements this interface."""

    name: str = "base"

    @abstractmethod
    async def run(self, context: AgentContext) -> AgentResult:
        """Execute the agent and return a structured result."""
        ...
