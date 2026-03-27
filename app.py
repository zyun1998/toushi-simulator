from dotenv import load_dotenv

load_dotenv()

import base64
import json
import os

import pandas as pd
import streamlit as st

from src.ai_service import answer_followup_question, generate_result_explanation
from src.calculator import SimulationInput, simulate_monthly_investment
from src.charts import create_asset_chart
from src.product_config import PRODUCT_CONFIG, get_product_description, get_product_label
from src.scenario_builder import build_scenarios

LOGO_PATH = "assets/logo.png"
QA_IMAGE_PATH = "assets/QA.png"
BACKGROUND_PATH = "assets/background.jpg"


def get_base64_image(image_path: str) -> str:
    if not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


background_base64 = get_base64_image(BACKGROUND_PATH)
logo_base64 = get_base64_image(LOGO_PATH)
qa_base64 = get_base64_image(QA_IMAGE_PATH)

st.set_page_config(
    page_title="NISA投資シミュレーター",
    page_icon="🐶",
    layout="wide",
)

background_css = ""
if background_base64:
    background_css = f"""
    .stApp {{
        background:
            linear-gradient(rgba(255, 249, 243, 0.86), rgba(255, 246, 238, 0.88)),
            url("data:image/jpeg;base64,{background_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    """
else:
    background_css = """
    .stApp {
        background:
            radial-gradient(circle at top left, #fffaf5 0%, #fff4ea 30%, #f7ebdf 62%, #f2e5d8 100%);
    }
    """

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Hachi+Maru+Pop&family=Zen+Maru+Gothic:wght@400;500;700;900&display=swap');

html, body, [class*="css"] {{
    font-family: 'Zen Maru Gothic', sans-serif;
    color: #4f4035;
}}

{background_css}

header[data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
}}

.main .block-container {{
    max-width: 1180px;
    padding-top: 0.12rem !important;
    padding-bottom: 2.7rem;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    position: relative;
}}

.stApp::before {{
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    background-image:
        radial-gradient(circle at 4.8% 8.5%, rgba(165, 140, 95, 0.14) 0 12px, transparent 13px),
        radial-gradient(circle at 2.8% 4.8%, rgba(165, 140, 95, 0.08) 0 6px, transparent 7px),
        radial-gradient(circle at 6.5% 4.3%, rgba(165, 140, 95, 0.08) 0 6px, transparent 7px),
        radial-gradient(circle at 1.9% 9.2%, rgba(165, 140, 95, 0.08) 0 6px, transparent 7px),
        radial-gradient(circle at 7.1% 11.9%, rgba(165, 140, 95, 0.08) 0 6px, transparent 7px),

        radial-gradient(circle at 94.5% 15%, rgba(165, 140, 95, 0.16) 0 22px, transparent 23px),
        radial-gradient(circle at 91.7% 9.6%, rgba(165, 140, 95, 0.10) 0 10px, transparent 11px),
        radial-gradient(circle at 97.2% 9.1%, rgba(165, 140, 95, 0.10) 0 10px, transparent 11px),
        radial-gradient(circle at 89.8% 17.8%, rgba(165, 140, 95, 0.10) 0 10px, transparent 11px),
        radial-gradient(circle at 99.1% 18.4%, rgba(165, 140, 95, 0.10) 0 10px, transparent 11px),

        radial-gradient(circle at 3% 86%, rgba(190, 170, 110, 0.11) 0 24px, transparent 25px),
        radial-gradient(circle at 1.1% 79.8%, rgba(190, 170, 110, 0.07) 0 10px, transparent 11px),
        radial-gradient(circle at 5.6% 79.6%, rgba(190, 170, 110, 0.07) 0 10px, transparent 11px),
        radial-gradient(circle at 0.3% 87.9%, rgba(190, 170, 110, 0.07) 0 10px, transparent 11px),
        radial-gradient(circle at 6.5% 89.5%, rgba(190, 170, 110, 0.07) 0 10px, transparent 11px),

        radial-gradient(circle at 93.8% 82%, rgba(190, 170, 110, 0.12) 0 22px, transparent 23px),
        radial-gradient(circle at 91.2% 76.8%, rgba(190, 170, 110, 0.08) 0 10px, transparent 11px),
        radial-gradient(circle at 96.7% 76.3%, rgba(190, 170, 110, 0.08) 0 10px, transparent 11px),
        radial-gradient(circle at 89.6% 84.6%, rgba(190, 170, 110, 0.08) 0 10px, transparent 11px),
        radial-gradient(circle at 98.9% 85.1%, rgba(190, 170, 110, 0.08) 0 10px, transparent 11px);
    filter: blur(0.4px);
}}

.main .block-container > div {{
    position: relative;
    z-index: 1;
}}

.topbar-wrap {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 4px;
}}

.topbar-logo {{
    width: 122px;
    display: block;
    transition: transform 0.22s ease, filter 0.22s ease;
    filter: drop-shadow(0 8px 14px rgba(110, 84, 61, 0.14));
}}

.topbar-logo:hover {{
    transform: translateY(-3px) scale(1.06) rotate(-3deg);
    filter: drop-shadow(0 12px 18px rgba(110, 84, 61, 0.20));
}}

.topbar-title {{
    font-family: 'Hachi Maru Pop', cursive;
    font-size: 1.52rem;
    color: #7a5a43;
    line-height: 1.3;
    letter-spacing: 0.01em;
}}

.hero-wrap {{
    position: relative;
    background: linear-gradient(135deg, rgba(255,252,248,0.72), rgba(255,245,235,0.70));
    border: 1px solid rgba(194, 165, 139, 0.10);
    border-radius: 22px;
    padding: 22px 24px;
    box-shadow: 0 6px 18px rgba(128, 98, 72, 0.04);
    margin-bottom: 18px;
    backdrop-filter: blur(3px);
    overflow: hidden;
}}

.hero-badge {{
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    background: #fff4e5;
    color: #9a6f47;
    font-size: 0.82rem;
    font-weight: 700;
    margin-bottom: 10px;
    border: 1px solid rgba(194,165,139,0.16);
    box-shadow: 0 2px 8px rgba(180, 130, 86, 0.04);
}}

.hero-title {{
    font-family: 'Hachi Maru Pop', cursive;
    font-size: 2.35rem;
    color: #604735;
    line-height: 1.28;
    margin: 0;
    text-align: center;
}}

.hero-subtitle {{
    color: #7d6654;
    font-size: 1rem;
    line-height: 1.8;
    margin-top: 12px;
    text-align: center;
}}

.glass-card {{
    background: rgba(255, 251, 246, 0.74);
    border: 1px solid rgba(194, 165, 139, 0.10);
    border-radius: 20px;
    padding: 15px 17px 11px 17px;
    box-shadow: 0 5px 14px rgba(118, 91, 68, 0.03);
    margin-bottom: 16px;
    backdrop-filter: blur(3px);
}}

.soft-card {{
    background: linear-gradient(135deg, rgba(255,248,239,0.92), rgba(255,253,248,0.92));
    border: 1px solid rgba(194, 165, 139, 0.12);
    border-radius: 18px;
    padding: 15px 16px 12px 16px;
    box-shadow: 0 4px 12px rgba(118, 91, 68, 0.025);
    margin-bottom: 16px;
}}

.section-title {{
    font-family: 'Hachi Maru Pop', cursive;
    font-size: 1.15rem;
    color: #654a37;
    margin-bottom: 0.35rem;
    line-height: 1.4;
}}

.small-note {{
    color: #8b7663;
    font-size: 0.96rem;
    line-height: 1.8;
}}

.metric-shell {{
    background: transparent;
    margin-top: 4px;
}}

[data-testid="stMetric"] {{
    background: rgba(255,255,255,0.66);
    border: 1px solid rgba(194,165,139,0.10);
    padding: 16px 13px;
    border-radius: 18px;
    box-shadow: 0 5px 14px rgba(118, 91, 68, 0.03);
}}

[data-testid="stMetricLabel"] {{
    color: #96785f;
    font-weight: 700;
}}

[data-testid="stMetricValue"] {{
    color: #4f3f33;
}}

.stButton > button {{
    background: linear-gradient(135deg, #d99c68, #c68049);
    color: white;
    border: none;
    border-radius: 999px;
    padding: 0.76rem 1.35rem;
    font-weight: 700;
    box-shadow: 0 8px 16px rgba(172, 112, 61, 0.18);
    transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
}}

.stButton > button:hover {{
    background: linear-gradient(135deg, #e0a574, #cc8852);
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 10px 18px rgba(172, 112, 61, 0.22);
}}

div[data-testid="stDataFrame"] {{
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid rgba(194,165,139,0.10);
}}

.chat-title {{
    font-family: 'Hachi Maru Pop', cursive;
    font-size: 1.2rem;
    color: #654a37;
    margin-bottom: 0.15rem;
}}

.ai-intro-box {{
    background: rgba(255, 249, 241, 0.92);
    border: 1px solid rgba(210, 187, 165, 0.26);
    border-radius: 16px;
    padding: 12px 15px;
    margin-bottom: 10px;
    box-shadow: 0 3px 8px rgba(118, 91, 68, 0.018);
}}

.qa-header {{
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 6px;
}}

.qa-pet {{
    width: 86px;
    margin-top: 2px;
    transition: transform 0.22s ease, filter 0.22s ease;
    filter: drop-shadow(0 8px 14px rgba(110, 84, 61, 0.12));
}}

.qa-pet:hover {{
    transform: translateY(-3px) scale(1.05) rotate(2deg);
    filter: drop-shadow(0 12px 18px rgba(110, 84, 61, 0.18));
}}

.footer-note {{
    text-align: center;
    color: #8a7461;
    font-size: 0.9rem;
    margin-top: 24px;
}}

hr.pretty {{
    border: none;
    height: 1px;
    background: linear-gradient(to right, transparent, rgba(194,165,139,0.28), transparent);
    margin: 20px 0;
}}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {{
    border-radius: 12px !important;
    border-width: 1px !important;
}}

[data-testid="stChatMessage"] {{
    align-items: flex-start;
    margin-bottom: 0.6rem;
}}

[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {{
    line-height: 1.82;
    font-size: 1rem;
    margin-bottom: 0;
}}

@media (max-width: 900px) {{
    .topbar-logo {{
        width: 96px;
    }}
    .topbar-title {{
        font-size: 1.2rem;
    }}
    .hero-title {{
        font-size: 1.9rem;
    }}
    .qa-header {{
        flex-direction: column;
    }}
}}
</style>
""",
    unsafe_allow_html=True,
)

if "result" not in st.session_state:
    st.session_state.result = None

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if "last_simulation_key" not in st.session_state:
    st.session_state.last_simulation_key = None


if logo_base64:
    st.markdown(
        f"""
        <div class="topbar-wrap">
            <img src="data:image/png;base64,{logo_base64}" class="topbar-logo" />
            <div class="topbar-title">やさしく続ける、わんこ投資サポート</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div class="topbar-wrap">
            <div class="topbar-title">やさしく続ける、わんこ投資サポート</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="hero-wrap">', unsafe_allow_html=True)
st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
st.markdown('<div class="hero-badge">やさしく見える、未来のお金</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">NISA投資シミュレーター</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="hero-subtitle">
        毎月の積立金額・投資期間・商品・市場シナリオをもとに、将来の資産推移をわかりやすく確認できます。<br>
        固定前提だけでなく、商品の過去データをもとにした自動シナリオも選べます。
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">シミュレーション条件</div>', unsafe_allow_html=True)

col_input_left, col_input_right = st.columns([1.1, 0.9])

with col_input_left:
    monthly_amount = st.number_input(
        "毎月の投資額（円）",
        min_value=1000,
        value=100000,
        step=1000,
    )

    years = st.slider(
        "投資期間（年）",
        min_value=1,
        max_value=40,
        value=15,
    )

    product_code = st.selectbox(
        "商品選択",
        options=list(PRODUCT_CONFIG.keys()),
        format_func=lambda x: PRODUCT_CONFIG[x]["label_ja"],
    )

with col_input_right:
    scenario_mode = st.radio(
        "シナリオ生成方式",
        options=["fixed", "market_auto"],
        format_func=lambda x: "基本値を使用" if x == "fixed" else "商品の過去データから自動計算",
        index=0,
    )

    scenario = st.selectbox(
        "市場シナリオ",
        options=["bull", "base", "bear"],
        format_func=lambda x: {
            "bull": "上昇相場",
            "base": "平均",
            "bear": "下落相場",
        }[x],
    )

    language = st.radio(
        "言語選択",
        ["ja", "ko"],
        horizontal=True,
        index=0,
    )

product_label = get_product_label(product_code, language)
product_desc = get_product_description(product_code, language)

st.caption(f"選択中の商品：{product_label} / {product_desc}")
st.markdown('</div>', unsafe_allow_html=True)

scenario_build = None
scenario_error = None

try:
    scenario_build = build_scenarios(
        product_code=product_code,
        scenario_mode=scenario_mode,
        period_years=10,
    )
except Exception as e:
    scenario_error = str(e)
    try:
        scenario_build = build_scenarios(
            product_code=product_code,
            scenario_mode="fixed",
            period_years=10,
        )
    except Exception:
        scenario_build = None

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">基準情報</div>', unsafe_allow_html=True)

if scenario_build is not None:
    benchmark_info = scenario_build.benchmark_info
    st.write(f"**基準商品**: {benchmark_info['benchmark_ticker']}")
    st.write(f"**データ期間**: 直近 {benchmark_info['period_years']} 年")
    st.write(f"**計算方式**: {benchmark_info['calculation_method']}")
    if scenario_error and scenario_mode == "market_auto":
        st.warning(f"市場データ取得に失敗したため、固定シナリオへ切り替えました。詳細: {scenario_error}")
    st.info(benchmark_info["warning_note"])
else:
    st.error("基準情報を表示できません。")

run_button = st.button("シミュレーション実行")
st.markdown('</div>', unsafe_allow_html=True)

if run_button:
    if scenario_build is None:
        st.error("シナリオ情報の生成に失敗したため、シミュレーションを実行できません。")
    else:
        config = scenario_build.scenarios[scenario]
        benchmark_info = scenario_build.benchmark_info

        sim_input = SimulationInput(
            monthly_amount=int(monthly_amount),
            years=years,
            annual_return=config["annual_return"],
            scenario=scenario,
            crash_year=config["crash_year"],
            crash_rate=config["crash_rate"],
            product_code=product_code,
            product_label=product_label,
            scenario_mode=scenario_mode if scenario_error is None else "fixed",
            benchmark_ticker=benchmark_info["benchmark_ticker"],
            period_years=benchmark_info["period_years"],
            calculation_method=benchmark_info["calculation_method"],
            warning_note=benchmark_info["warning_note"],
        )

        result = simulate_monthly_investment(sim_input)
        st.session_state.result = result

        simulation_key = json.dumps(
            {
                "monthly_amount": int(monthly_amount),
                "years": years,
                "scenario": scenario,
                "language": language,
                "product_code": product_code,
                "scenario_mode": scenario_mode,
            },
            sort_keys=True,
            ensure_ascii=False,
        )

        if st.session_state.last_simulation_key != simulation_key:
            st.session_state.chat_messages = []
            st.session_state.last_simulation_key = simulation_key

        with st.spinner("ワンコサポートが結果をまとめています..."):
            explanation = generate_result_explanation(result, language)

        st.session_state.chat_messages.append(
            {"role": "assistant", "content": explanation}
        )

if st.session_state.result is not None:
    result = st.session_state.result
    summary = result["summary"]
    result_input = result["input"]
    df = pd.DataFrame(result["yearly_rows"])

    display_df = df.copy()
    display_df["principal"] = display_df["principal"].map(lambda x: f"{x:,.0f}円")
    display_df["balance"] = display_df["balance"].map(lambda x: f"{x:,.0f}円")
    display_df["profit"] = display_df["profit"].map(lambda x: f"{x:,.0f}円")

    display_df = display_df.rename(columns={
        "year": "年数",
        "principal": "元本累計",
        "balance": "資産額",
        "profit": "利益",
    })

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">シミュレーション結果</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-shell">', unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("総投資額", f"{summary['total_principal']:,.0f} 円")
    m2.metric("最終資産額", f"{summary['final_balance']:,.0f} 円")
    m3.metric("予想利益", f"{summary['total_profit']:,.0f} 円")

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    left, right = st.columns([1.02, 0.98])

    with left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">年別データ</div>', unsafe_allow_html=True)
        st.dataframe(display_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">NISA枠チェック</div>', unsafe_allow_html=True)

        nisa_check = result["nisa_check"]
        if nisa_check["within_limit"]:
            st.success(f"年間投資額 {nisa_check['annual_amount']:,.0f}円：NISA枠内")
        else:
            st.warning(
                f"年間投資額 {nisa_check['annual_amount']:,.0f}円："
                f"NISA枠超過（{nisa_check['excess_amount']:,.0f}円オーバー）"
            )

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">計算基準</div>', unsafe_allow_html=True)
        st.write(f"**商品**: {result_input['product_label']}")
        st.write(f"**基準商品**: {result_input['benchmark_ticker']}")
        st.write(f"**データ期間**: 直近 {result_input['period_years']} 年")
        st.write(f"**計算方式**: {result_input['calculation_method']}")
        st.info(result_input["warning_note"])
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">資産の推移グラフ</div>', unsafe_allow_html=True)
        st.caption("元本と資産額の推移を確認できます。")
        chart = create_asset_chart(
            df,
            result_input["product_label"],
            {
                "bull": "上昇相場",
                "base": "平均",
                "bear": "下落相場",
            }[result_input["scenario"]],
        )
        st.plotly_chart(chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="pretty">', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    intro_html = '<div class="qa-header">'
    if qa_base64:
        intro_html += f'<img src="data:image/png;base64,{qa_base64}" class="qa-pet" />'
    intro_html += """
        <div style="flex:1;">
            <div class="chat-title">ワンコサポートチャット</div>
            <div class="ai-intro-box">
                <div class="small-note">
                    シミュレーション結果の意味、利益の見方、NISA枠の確認、基準商品の意味などを続けて質問できます。<br>
                    やさしく、わかりやすく答えます。
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(intro_html, unsafe_allow_html=True)

    assistant_avatar = QA_IMAGE_PATH if os.path.exists(QA_IMAGE_PATH) else None

    for message in st.session_state.chat_messages:
        if message["role"] == "assistant":
            with st.chat_message("assistant", avatar=assistant_avatar):
                st.write(message["content"])
        else:
            with st.chat_message("user"):
                st.write(message["content"])

    user_question = st.chat_input("たとえば「SPYとは何ですか？」のように入力してください")

    if user_question:
        st.session_state.chat_messages.append(
            {"role": "user", "content": user_question}
        )

        with st.chat_message("user"):
            st.write(user_question)

        with st.chat_message("assistant", avatar=assistant_avatar):
            with st.spinner("ワンコサポートが回答を作成中です..."):
                answer = answer_followup_question(result, user_question, language)
                st.write(answer)

        st.session_state.chat_messages.append(
            {"role": "assistant", "content": answer}
        )

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="footer-note">
    あなたのペースで、やさしく続ける積立をサポートするシミュレーターです。
    </div>
    """,
    unsafe_allow_html=True,
)