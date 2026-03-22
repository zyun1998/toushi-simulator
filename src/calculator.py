from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class SimulationInput:
    monthly_amount: int #매달 투자하는 금액
    years: int #투자 기간(년)
    annual_return: float   # 연 수익률 예: 0.05
    scenario: str          # 시나리오 이름 bull / base / bear
    crash_year: Optional[int] = None # 몇 년 차 말에 폭락장을 반영할지
    crash_rate: Optional[float] = None  # 폭락 비율 예: -0.3


def apply_crash_scenario(balance: float, year_index: int, crash_year: Optional[int], crash_rate: Optional[float]) -> float:
    """
    특정 연도 말에 하락장을 반영 (폭락 연도가 지정되어있고 폭락률도 지정되어 있음,현재 연도가 그 폭락 연도와 같으면 적용)
    """
    if crash_year is not None and crash_rate is not None and year_index == crash_year:
        balance = balance * (1 + crash_rate)
    return balance


def check_nisa_limit(monthly_amount: int) -> dict:
    """
    NISA 연간 투자 한도 체크
    여기서는 단순히 연간 360만엔 기준으로 체크
    """
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
    """
    월 적립 + 월 복리 기준 계산 (월초에 투자한뒤 한달동안 운용된것 처럼 계산(그 달 수익률을 바로 적용))
    """
    monthly_rate = sim_input.annual_return / 12 #연 수익률을 월 수익률로 단순 나눗셈해서 계산
    total_months = sim_input.years * 12

    balance = 0.0
    principal = 0
    yearly_rows = []

    for month in range(1, total_months + 1):
        # 매달 투자금 추가
        balance += sim_input.monthly_amount 
        principal += sim_input.monthly_amount
        
        #월 수익률 적용
        balance *= (1 + monthly_rate)

        # 12개월마다 연도 요약 저장
        if month % 12 == 0:
            year = month // 12

            # 해당 연도에 폭락장이 설정되어있을 경우 폭락 적용
            balance = apply_crash_scenario(
                balance=balance,
                year_index=year,
                crash_year=sim_input.crash_year,
                crash_rate=sim_input.crash_rate,
            )
            
            #연도별 결과를 저장
            yearly_rows.append({
                "year": year,
                "principal": principal,
                "balance": round(balance, 2),
                "profit": round(balance - principal, 2),
            })

    final_balance = round(balance, 2)  #마지막 평가금액
    total_profit = round(final_balance - principal, 2) #최종 수익금
   
    # input은 입력값 기록용,summary은 최종요약,yearly_rows는 연도별 상세 데이터,nisa 한도 체크 결과
    return {
        "input": {
            "monthly_amount": sim_input.monthly_amount,
            "years": sim_input.years,
            "annual_return": sim_input.annual_return,
            "scenario": sim_input.scenario,
            "crash_year": sim_input.crash_year,
            "crash_rate": sim_input.crash_rate,
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