from __future__ import annotations

import pandas as pd
import plotly.express as px


def create_asset_chart(df: pd.DataFrame, product_label: str, scenario_label: str):
    fig = px.line(
        df,
        x="year",
        y=["principal", "balance"],
        markers=True,
        title=f"{product_label} / {scenario_label} の年別推移",
    )

    fig.update_layout(
        xaxis_title="年数",
        yaxis_title="金額（円）",
        legend_title="項目",
    )

    return fig