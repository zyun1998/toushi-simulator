from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class SimulationInput:
    monthly_amount: int
    years: int
    annual_return: float
    scenario: str
    crash_year: Optional[int] = None
    crash_rate: Optional[float] = None

    # Phase2 확장 메타정보
    product_code: str = "sp500"
    product_label: str = "S&P500"
    scenario_mode: str = "fixed"
    benchmark_ticker: str = "SPY"
    period_years: int = 10
    calculation_method: str = "固定シナリオ"
    warning_note: str = "過去の実績は将来の成果を保証しません。"


def apply_crash_scenario(
    balance: float,
    year_index: int,
    crash_year: Optional[int],
    crash_rate: Optional[float],
) -> float:
    if crash_year is not None and crash_rate is not None and year_index == crash_year:
        balance = balance * (1 + crash_rate)
    return balance


def check_nisa_limit(monthly_amount: int) -> dict:
    annual_amount = monthly_amount * 12
    annual_limit = 3_600_000
    within_limit = annual_amount <= annual_limit

    return {
        "annual_amount": annual_amount,
        "annual_limit": annual_limit,
        "within_limit": within_limit,
        "excess_amount": max(0, annual_amount - annual_limit),
    }


def simulate_monthly_investment(sim_input: SimulationInput) -> dict:
    monthly_rate = sim_input.annual_return / 12
    total_months = sim_input.years * 12

    balance = 0.0
    principal = 0
    yearly_rows = []

    for month in range(1, total_months + 1):
        balance += sim_input.monthly_amount
        principal += sim_input.monthly_amount
        balance *= (1 + monthly_rate)

        if month % 12 == 0:
            year = month // 12

            balance = apply_crash_scenario(
                balance=balance,
                year_index=year,
                crash_year=sim_input.crash_year,
                crash_rate=sim_input.crash_rate,
            )

            yearly_rows.append(
                {
                    "year": year,
                    "principal": principal,
                    "balance": round(balance, 2),
                    "profit": round(balance - principal, 2),
                }
            )

    final_balance = round(balance, 2)
    total_profit = round(final_balance - principal, 2)

    return {
        "input": {
            "monthly_amount": sim_input.monthly_amount,
            "years": sim_input.years,
            "annual_return": sim_input.annual_return,
            "scenario": sim_input.scenario,
            "crash_year": sim_input.crash_year,
            "crash_rate": sim_input.crash_rate,
            "product_code": sim_input.product_code,
            "product_label": sim_input.product_label,
            "scenario_mode": sim_input.scenario_mode,
            "benchmark_ticker": sim_input.benchmark_ticker,
            "period_years": sim_input.period_years,
            "calculation_method": sim_input.calculation_method,
            "warning_note": sim_input.warning_note,
        },
        "summary": {
            "total_principal": principal,
            "final_balance": final_balance,
            "total_profit": total_profit,
        },
        "yearly_rows": yearly_rows,
        "nisa_check": check_nisa_limit(sim_input.monthly_amount),
    }


def build_yearly_summary(result: dict) -> list[dict]:
    return result["yearly_rows"]