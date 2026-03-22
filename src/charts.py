import plotly.express as px
import pandas as pd


def create_asset_chart(df: pd.DataFrame):
    fig = px.line(
        df,
        x="year",
        y=["principal", "balance"],
        markers=True,
        title="年別の元本と資産額の推移"
    )

    fig.update_layout(
        xaxis_title="年数",
        yaxis_title="金額（円）",
        legend_title="項目"
    )

    return fig