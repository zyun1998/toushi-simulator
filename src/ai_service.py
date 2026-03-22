import json
import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from src.prompts import (
    build_followup_question_prompt,
    build_result_explanation_prompt,
)

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY が設定されていません。.env を確認してください。")

client = OpenAI(api_key=api_key)


def _extract_simple_result(result: dict) -> dict:
    summary = result["summary"]
    nisa_check = result["nisa_check"]

    return {
        "total_principal": summary["total_principal"],
        "final_balance": summary["final_balance"],
        "total_profit": summary["total_profit"],
        "annual_amount": nisa_check["annual_amount"],
        "annual_limit": nisa_check["annual_limit"],
        "within_limit": nisa_check["within_limit"],
        "excess_amount": nisa_check["excess_amount"],
    }


@st.cache_data(show_spinner=False)
def _call_explanation_cached(simple_result_json: str, language: str) -> str:
    simple_result = json.loads(simple_result_json)
    prompt = build_result_explanation_prompt(simple_result, language)

    response = client.responses.create(
        model="gpt-5.4-mini",
        input=prompt,
    )
    return response.output_text


@st.cache_data(show_spinner=False)
def _call_followup_cached(simple_result_json: str, question: str, language: str) -> str:
    simple_result = json.loads(simple_result_json)
    prompt = build_followup_question_prompt(simple_result, question, language)

    response = client.responses.create(
        model="gpt-5.4-mini",
        input=prompt,
    )
    return response.output_text


def generate_result_explanation(result: dict, language: str = "ja") -> str:
    try:
        simple_result = _extract_simple_result(result)
        simple_result_json = json.dumps(simple_result, sort_keys=True, ensure_ascii=False)
        return _call_explanation_cached(simple_result_json, language)

    except Exception as e:
        return f"AI解説の生成に失敗しました: {type(e).__name__}: {e}"


def answer_followup_question(result: dict, question: str, language: str = "ja") -> str:
    try:
        simple_result = _extract_simple_result(result)
        simple_result_json = json.dumps(simple_result, sort_keys=True, ensure_ascii=False)
        return _call_followup_cached(simple_result_json, question, language)

    except Exception as e:
        return f"AI回答の生成に失敗しました: {type(e).__name__}: {e}"