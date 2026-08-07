"""Investment Committee — aggregates multiple agent opinions."""

from __future__ import annotations

from collections import Counter

from app.agents.base import AgentContext, AgentResult, BaseAgent, Recommendation
from app.agents.research import ResearchAgent
from app.agents.llm import LLMClient


class RiskAgent(BaseAgent):
    """Conservative risk-focused view."""

    name = "risk"

    async def run(self, context: AgentContext) -> AgentResult:
        data = context.company_data
        risks: list[str] = []
        evidence: list[str] = []
        de = data.get("debt_to_equity")
        pe = data.get("pe_ratio")

        score = 0.6
        if de is not None and float(de) > 1:
            risks.append(f"High leverage (D/E={de})")
            score -= 0.2
        if pe is not None and float(pe) > 50:
            risks.append(f"Rich valuation (PE={pe})")
            score -= 0.15
        if not risks:
            evidence.append("No major red flags in available leverage/valuation metrics")

        rec = Recommendation.HOLD if score >= 0.4 else Recommendation.WATCH
        return AgentResult(
            agent_name=self.name,
            recommendation=rec,
            confidence=max(0.2, min(score, 0.9)),
            evidence=evidence,
            analysis="Risk agent focuses on leverage and valuation extremes.",
            risks=risks,
        )


class QuantAgent(BaseAgent):
    """Simple quant-style momentum/quality blend on available fields."""

    name = "quant"

    async def run(self, context: AgentContext) -> AgentResult:
        data = context.company_data
        roce = float(data["roce"]) if data.get("roce") is not None else None
        pe = float(data["pe_ratio"]) if data.get("pe_ratio") is not None else None
        evidence: list[str] = []
        score = 0.5

        if roce is not None and roce > 20:
            score += 0.2
            evidence.append(f"Quality: ROCE {roce}")
        if pe is not None and 0 < pe < 20:
            score += 0.15
            evidence.append(f"Value: PE {pe}")
        elif pe is not None and pe > 40:
            score -= 0.1

        if score >= 0.65:
            rec = Recommendation.BUY
        elif score >= 0.4:
            rec = Recommendation.HOLD
        else:
            rec = Recommendation.WATCH

        return AgentResult(
            agent_name=self.name,
            recommendation=rec,
            confidence=min(score, 0.95),
            evidence=evidence,
            analysis="Quant agent blends quality (ROCE) and value (PE) signals.",
            risks=[],
        )


class InvestmentCommittee(BaseAgent):
    """Chairman that runs member agents and synthesizes a final view."""

    name = "committee"

    def __init__(self, llm: LLMClient | None = None) -> None:
        self._llm = llm or LLMClient()
        self._members: list[BaseAgent] = [
            ResearchAgent(self._llm),
            RiskAgent(),
            QuantAgent(),
        ]

    async def run(self, context: AgentContext) -> AgentResult:
        results: list[AgentResult] = []
        for agent in self._members:
            results.append(await agent.run(context))

        votes = Counter(r.recommendation for r in results)
        # Weighted by confidence
        weight: dict[Recommendation, float] = {}
        for r in results:
            weight[r.recommendation] = weight.get(r.recommendation, 0) + r.confidence

        final_rec = max(weight, key=weight.get) if weight else Recommendation.HOLD  # type: ignore[arg-type]
        avg_conf = sum(r.confidence for r in results) / len(results) if results else 0

        evidence = []
        risks = []
        for r in results:
            evidence.append(f"[{r.agent_name}] {r.recommendation.value} ({r.confidence:.0%})")
            risks.extend(r.risks)

        analysis = (
            f"Committee of {len(results)} agents. "
            f"Vote tally: {dict(votes)}. "
            f"Chairman synthesis: {final_rec.value}."
        )

        # Optional LLM chairman summary
        if self._llm.available:
            member_blob = [r.to_dict() for r in results]
            llm_out = await self._llm.chat_json(
                system=(
                    "You are the Investment Committee chairman. "
                    "Synthesize member opinions into JSON: "
                    "analysis, recommendation (BUY|HOLD|SELL|WATCH), "
                    "confidence (0-1), risks (string[]), catalysts (string[])."
                ),
                user=str(member_blob),
            )
            if llm_out.get("analysis"):
                analysis = str(llm_out["analysis"])
            if llm_out.get("recommendation"):
                try:
                    final_rec = Recommendation(str(llm_out["recommendation"]).upper())
                except ValueError:
                    pass
            if isinstance(llm_out.get("confidence"), (int, float)):
                avg_conf = float(llm_out["confidence"])

        return AgentResult(
            agent_name=self.name,
            recommendation=final_rec,
            confidence=round(avg_conf, 3),
            evidence=evidence,
            analysis=analysis,
            risks=list(dict.fromkeys(risks)),
            catalysts=[],
            raw={"members": [r.to_dict() for r in results]},
        )
