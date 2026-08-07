"""AI agent endpoints."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents import AgentContext, InvestmentCommittee, ResearchAgent
from app.db import get_db
from app.models.company import Company

router = APIRouter(prefix="/agents", tags=["AI Agents"])


class AgentRunRequest(BaseModel):
    company_id: UUID
    question: str | None = Field(None, description="Optional user question")


class AgentRunResponse(BaseModel):
    agent_name: str
    recommendation: str
    confidence: float
    evidence: list[str]
    analysis: str
    counter_arguments: list[str] = []
    risks: list[str] = []
    catalysts: list[str] = []
    members: list[dict[str, Any]] | None = None


async def _company_context(
    session: AsyncSession, company_id: UUID, question: str | None
) -> AgentContext:
    result = await session.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    data = {
        "symbol": company.symbol,
        "exchange": company.exchange,
        "name": company.name,
        "sector": company.sector,
        "roce": float(company.roce) if company.roce is not None else None,
        "roe": float(company.roe) if company.roe is not None else None,
        "pe_ratio": float(company.pe_ratio) if company.pe_ratio is not None else None,
        "debt_to_equity": float(company.debt_to_equity)
        if company.debt_to_equity is not None
        else None,
        "market_cap": float(company.market_cap) if company.market_cap is not None else None,
        "description": company.description,
    }
    return AgentContext(
        company_id=company.id,
        symbol=company.symbol,
        exchange=company.exchange,
        company_data=data,
        user_question=question,
    )


@router.post("/research", response_model=AgentRunResponse)
async def run_research_agent(
    body: AgentRunRequest,
    session: AsyncSession = Depends(get_db),
) -> AgentRunResponse:
    """Run the fundamental research agent on a company."""
    ctx = await _company_context(session, body.company_id, body.question)
    result = await ResearchAgent().run(ctx)
    return AgentRunResponse(**result.to_dict())


@router.post("/committee", response_model=AgentRunResponse)
async def run_committee(
    body: AgentRunRequest,
    session: AsyncSession = Depends(get_db),
) -> AgentRunResponse:
    """Run Investment Committee (research + risk + quant).

    Works offline with rule-based members. If OPENAI_API_KEY is set,
    LLM enrichment is used for research and chairman synthesis.
    """
    ctx = await _company_context(session, body.company_id, body.question)
    result = await InvestmentCommittee().run(ctx)
    payload = result.to_dict()
    members = result.raw.get("members") if result.raw else None
    return AgentRunResponse(**payload, members=members)
