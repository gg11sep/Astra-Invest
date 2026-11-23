# Astra Research & Validation Standards
**Version 1.1 – November 2026**

## Purpose
These standards protect Astra from overfitting, narrative bias, look-ahead bias, and false confidence.

## Core Principles
1. Process over Prediction
2. Most ideas fail — report this honestly
3. No look-ahead bias
4. Realistic costs required in all tests
5. Robustness > Optimization
6. Multi-model / multi-agent thinking
7. Capital preservation ranks higher in elevated stress regimes

## Minimum Validation Requirements
- Clear economic rationale
- Out-of-sample or walk-forward testing
- Parameter sensitivity / robustness checks
- Honest reporting of the full parameter space (including failures)
- Documented failure modes

## Backtesting Rules
- Signal at close → fill next open (or realistic delay)
- Include transaction costs
- Report trades, win rate, drawdown, turnover, exposure
- Prefer economic significance over pure statistical significance

## Feedback Requirement
Every major regime call and Top Idea is logged and scored at 30 / 90 / 180 days.
