from __future__ import annotations

import os
from dataclasses import dataclass

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


@dataclass
class MarketDataResult:
    ticker: str
    period_years: int
    monthly_prices: pd.DataFrame
    source: str


def _get_alpha_vantage_api_key() -> str | None:
    env_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if env_key:
        return env_key

    try:
        return st.secrets.get("ALPHA_VANTAGE_API_KEY")
    except Exception:
        return None


@st.cache_data(show_spinner=False, ttl=60 * 60 * 12)
def fetch_monthly_market_data(ticker: str, period_years: int = 10) -> MarketDataResult:
    ticker = ticker.strip().upper()

    api_key = _get_alpha_vantage_api_key()
    
    if not api_key:
        raise RuntimeError("ALPHA_VANTAGE_API_KEY が設定されていません。")
        

    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_MONTHLY_ADJUSTED",
        "symbol": ticker,
        "apikey": api_key,
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Alpha Vantage API 호출에 실패했습니다: {e}") from e

    try:
        data = response.json()
    except ValueError as e:
        raise ValueError("Alpha Vantage 응답이 JSON 형식이 아닙니다。") from e

    if "Error Message" in data:
        raise ValueError(f"Alpha Vantage error: {data['Error Message']}")

    if "Note" in data:
        raise ValueError("Alpha Vantage API 호출 한도를 초과했습니다. 잠시 후 다시 시도해주세요.")

    time_series = data.get("Monthly Adjusted Time Series")
    if not time_series:
        raise ValueError(f"{ticker} の月次データを取得できませんでした。")

    rows = []
    for date_str, values in time_series.items():
        rows.append(
            {
                "date": pd.to_datetime(date_str),
                "close": float(values["5. adjusted close"]),
            }
        )

    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)

    if len(df) < 24:
        raise ValueError(f"{ticker} のデータ件数が不足しています。")

    cutoff_date = df["date"].max() - pd.DateOffset(years=period_years)
    df = df[df["date"] >= cutoff_date].reset_index(drop=True)

    if len(df) < 24:
        raise ValueError(f"{ticker} の{period_years}年分データが不足しています。")

    return MarketDataResult(
        ticker=ticker,
        period_years=period_years,
        monthly_prices=df,
        source="Alpha Vantage",
    )