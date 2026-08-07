"""Fundamental research agent with rule-based + optional LLM reasoning."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.agents.base import AgentContext, AgentResult, BaseAgent, Recommendation
from app.agents.llm import LLMClient


class ResearchAgent(BaseAgent):
    """Scores a company using fundamentals; optionally enriches with LLM."""

    name = "research"

    def __init__(self, llm: LLMClient | None = None) -> None:
        self._llm = llm or LLMClient()

    async def run(self, context: AgentContext) -> AgentResult:
        data = context.company_data
        evidence: list[str] = []
        risks: list[str] = []
        catalysts: list[str] = []
        score = 0.0
        max_score = 0.0

        roce = _num(data.get("roce"))
        de = _num(data.get("debt_to_equity"))
        pe = _num(data.get("pe_ratio"))
        roe = _num(data.get("roe"))

        # ROCE
        max_score += 25
        if roce is not None:
            if roce >= 20:
                score += 25
                evidence.append(f"ROCE {roce}% ≥ 20% (quality capital efficiency)")
            elif roce >= 12:
                score += 12
                evidence.append(f"ROCE {roce}% is moderate")
            else:
                risks.append(f"ROCE {roce}% is low")
        else:
            risks.append("ROCE data missing")

        # Debt
        max_score += 20
        if de is not None:
            if de <= 0.5:
                score += 20
                evidence.append(f"Debt/Equity {de} ≤ 0.5 (conservative balance sheet)")
            elif de <= 1.0:
                score += 10
                evidence.append(f"Debt/Equity {de} is moderate")
            else:
                risks.append(f"Debt/Equity {de} is elevated")
        else:
            risks.append("Debt/Equity data missing")

        # PE (context-dependent; treat very high as risk)
        max_score += 15
        if pe is not None:
            if 0 < pe <= 25:
                score += 15
                evidence.append(f"PE {pe} within reasonable range")
            elif pe <= 40:
                score += 7
                evidence.append(f"PE {pe} is elevated")
            else:
                risks.append(f"PE {pe} appears expensive")
        else:
            risks.append("PE data missing")

        # ROE
        max_score += 15
        if roe is not None:
            if roe >= 15:
                score += 15
                evidence.append(f"ROE {roe}% ≥ 15%")
            elif roe >= 10:
                score += 8
            else:
                risks.append(f"ROE {roe}% is weak")

        max_score += 25  # qualitative / LLM slot
        confidence = min(score / max_score, 1.0) if max_score else 0.0

        if confidence >= 0.7:
            rec = Recommendation.BUY
        elif confidence >= 0.45:
            rec = Recommendation.HOLD
        elif evidence:
            rec = Recommendation.WATCH
        else:
            rec = Recommendation.INSUFFICIENT_DATA

        analysis = (
            f"Rule-based fundamental score {score:.0f}/{max_score:.0f}. "
            f"Recommendation: {rec.value}."
        )

        # Optional LLM enrichment
        if self._llm.available and data:
            llm_out = await self._llm.chat_json(
                system=(
                    "You are a fundamental equity research analyst. "
                    "Given company metrics, return JSON with keys: "
                    "analysis (string), counter_arguments (string[]), "
                    "risks (string[]), catalysts (string[]), "
                    "recommendation (BUY|HOLD|SELL|WATCH), confidence (0-1)."
                ),
                user=f"Company data: {data}\nRule-based view: {analysis}\nEvidence: {evidence}",
            )
            if llm_out:
                analysis = str(llm_out.get("analysis") or analysis)
                counter = llm_out.get("counter_arguments") or []
                extra_risks = llm_out.get("risks") or []
                extra_cat = llm_out.get("catalysts") or []
                if isinstance(counter, list):
                    pass
                else:
                    counter = []
                risks = list(dict.fromkeys(risks + [str(r) for r in extra_risks]))
                catalysts = [str(c) for c in extra_cat]
                conf = llm_out.get("confidence")
                if isinstance(conf, (int, float)):
                    confidence = float(conf)
                rec_str = str(llm_out.get("recommendation") or rec.value).upper()
                try:
                    rec = Recommendation(rec_str)
                except ValueError:
                    pass
                return AgentResult(
                    agent_name=self.name,
                    recommendation=rec,
                    confidence=confidence,
                    evidence=evidence,
                    analysis=analysis,
                    counter_arguments=[str(c) for c in counter],
                    risks=risks,
                    catalysts=catalysts,
                    raw=llm_out,
                )

        return AgentResult(
            agent_name=self.name,
            recommendation=rec,
            confidence=round(confidence, 3),
            evidence=evidence,
            analysis=analysis,
            counter_arguments=[],
            risks=risks,
            catalysts=catalysts,
        )


def _num(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(Decimal(str(value)))
    except Exception:
        return None
