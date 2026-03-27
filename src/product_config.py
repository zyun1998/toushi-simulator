from __future__ import annotations

PRODUCT_CONFIG = {
    "sp500": {
        "label_ja": "S&P500",
        "label_ko": "S&P500",
        "ticker": "SPY",
        "description_ja": "米国大型株を代表する指数に連動するETFを基準にします。",
        "description_ko": "미국 대형주 대표 지수를 추종하는 ETF를 기준으로 사용합니다.",
    },
    "nasdaq100": {
        "label_ja": "NASDAQ100",
        "label_ko": "NASDAQ100",
        "ticker": "QQQ",
        "description_ja": "米国ハイテク株中心の指数に連動するETFを基準にします。",
        "description_ko": "미국 기술주 중심 지수를 추종하는 ETF를 기준으로 사용합니다.",
    },
    "all_world": {
        "label_ja": "全世界株",
        "label_ko": "전세계주",
        "ticker": "VT",
        "description_ja": "全世界株式に分散投資するETFを基準にします。",
        "description_ko": "전세계 주식 분산 ETF를 기준으로 사용합니다.",
    },
    "emerging": {
        "label_ja": "新興国株",
        "label_ko": "신흥국주",
        "ticker": "VWO",
        "description_ja": "新興国株式ETFを基準にします。",
        "description_ko": "신흥국 주식 ETF를 기준으로 사용합니다.",
    },
    "japan": {
        "label_ja": "日本株",
        "label_ko": "일본주",
        "ticker": "EWJ",
        "description_ja": "日本株ETFを基準にします。",
        "description_ko": "일본 주식 ETF를 기준으로 사용합니다.",
    },
}


def get_product_label(product_code: str, language: str = "ja") -> str:
    product = PRODUCT_CONFIG[product_code]
    return product["label_ko"] if language == "ko" else product["label_ja"]


def get_product_ticker(product_code: str) -> str:
    return PRODUCT_CONFIG[product_code]["ticker"]


def get_product_description(product_code: str, language: str = "ja") -> str:
    product = PRODUCT_CONFIG[product_code]
    return product["description_ko"] if language == "ko" else product["description_ja"]