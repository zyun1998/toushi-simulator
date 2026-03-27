from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd

from src.market_data import MarketDataResult, fetch_monthly_market_data
from src.product_config import get_product_ticker


FIXED_SCENARIO_CONFIG = {
    "bull": {
        "label": "上昇相場",
        "annual_return": 0.08,
        "crash_year": None,
        "crash_rate": None,
        "description": "前向きな成長を想定したシナリオです。",
    },
    "base": {
        "label": "平均",
        "annual_return": 0.05,
        "crash_year": None,
        "crash_rate": None,
        "description": "標準的な前提で試算するシナリオです。",
    },
    "bear": {
        "label": "下落相場",
        "annual_return": 0.03,
        "crash_year": 3,
        "crash_rate": -0.30,
        "description": "途中の下落も考慮した慎重なシナリオです。",
    },
}


@dataclass
class ScenarioBuildResult:
    scenarios: dict
    benchmark_info: dict


def _annualize_from_monthly(monthly_return: float) -> float:
    return (1 + monthly_return) ** 12 - 1


def _build_market_scenarios(monthly_df: pd.DataFrame) -> dict:
    monthly_returns = monthly_df["close"].pct_change().dropna()

    if monthly_returns.empty:
        raise ValueError("月次リターンを計算できませんでした。")

    mean_monthly = float(monthly_returns.mean())
    upper_q = float(monthly_returns.quantile(0.75))
    lower_q = float(monthly_returns.quantile(0.25))

    bull_monthly_series = monthly_returns[monthly_returns >= upper_q]
    bear_monthly_series = monthly_returns[monthly_returns <= lower_q]

    bull_monthly = float(bull_monthly_series.mean()) if not bull_monthly_series.empty else mean_monthly
    bear_monthly = float(bear_monthly_series.mean()) if not bear_monthly_series.empty else mean_monthly

    base_annual = _annualize_from_monthly(mean_monthly)
    bull_annual = _annualize_from_monthly(bull_monthly)
    bear_annual = _annualize_from_monthly(bear_monthly)

    # 너무 과격한 값은 완화
    bear_annual_capped = max(bear_annual, -0.20)
    bull_annual_capped = min(max(bull_annual, base_annual), 0.18)

    return {
        "bull": {
            "label": "上昇相場",
            "annual_return": bull_annual_capped,
            "crash_year": None,
            "crash_rate": None,
            "description": "過去データの上位月次リターン帯をもとに算出したシナリオです。",
        },
        "base": {
            "label": "平均",
            "annual_return": base_annual,
            "crash_year": None,
            "crash_rate": None,
            "description": "過去データの平均月次リターンを年率換算したシナリオです。",
        },
        "bear": {
            "label": "下落相場",
            "annual_return": bear_annual_capped,
            "crash_year": 3,
            "crash_rate": -0.20,
            "description": "過去データの下位月次リターン帯と下落イベントを考慮したシナリオです。",
        },
    }


def build_scenarios(
    product_code: str,
    scenario_mode: str = "fixed",
    period_years: int = 10,
) -> ScenarioBuildResult:
    ticker = get_product_ticker(product_code)

    if scenario_mode == "fixed":
        return ScenarioBuildResult(
            scenarios=FIXED_SCENARIO_CONFIG,
            benchmark_info={
                "benchmark_ticker": ticker,
                "period_years": period_years,
                "calculation_method": "固定シナリオ",
                "source": "internal",
                "warning_note": "過去の実績ではなく、アプリ内の固定前提値を使用しています。",
            },
        )

    market_data: MarketDataResult = fetch_monthly_market_data(ticker, period_years=period_years)
    scenarios = _build_market_scenarios(market_data.monthly_prices)

    return ScenarioBuildResult(
        scenarios=scenarios,
        benchmark_info={
            "benchmark_ticker": ticker,
            "period_years": period_years,
            "calculation_method": "月間リターン平均・分位帯を年率換算",
            "source": market_data.source,
            "warning_note": "過去の実績は将来の成果を保証しません。",
        },
    )