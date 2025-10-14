
# app_final.py
# Final Dash app for Pink Morsels sales visualization

import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

PRICE_CHANGE_DATE = datetime(2021, 1, 15)
DEFAULT_CSV = Path("output/pink_morsels_sales.csv")

def robust_parse_dates(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip()
    try:
        parsed = pd.to_datetime(s, format="mixed", dayfirst=True, errors="coerce")
    except Exception:
        parsed = pd.to_datetime(s, errors="coerce", dayfirst=True)
    if parsed.isna().any():
        for fmt in ("%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y"):
            mask = parsed.isna()
            if not mask.any():
                break
            try:
                parsed.loc[mask] = pd.to_datetime(s.loc[mask], format=fmt, errors="coerce")
            except Exception:
                pass
    if parsed.isna().any():
        parsed = parsed.fillna(pd.to_datetime(s, errors="coerce"))
    return parsed

def load_data() -> pd.DataFrame:
    csv_path = Path(os.getenv("SALES_CSV", DEFAULT_CSV))
    if not csv_path.exists():
        alt = Path("pink_morsels_sales.csv")
        if alt.exists():
            csv_path = alt
        else:
            raise SystemExit(
                f"Could not find CSV at {csv_path.resolve()} or {alt.resolve()}\n"
                "Please export the file from Task 1 first."
            )
    df = pd.read_csv(csv_path)
    df.columns = [c.strip().title() for c in df.columns]
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
    df["Date"] = robust_parse_dates(df["Date"])
    df = df.dropna(subset=["Sales", "Date"]).sort_values("Date", kind="stable")
    df["Region"] = df["Region"].astype(str).str.strip().str.title()
    df["_region_key"] = df["Region"].str.casefold()
    return df

df = load_data()
region_keys = sorted(df["_region_key"].unique().tolist())
region_options = [{"label": rk.title(), "value": rk} for rk in region_keys]
region_options.append({"label": "All", "value": "all"})

app = Dash(__name__)
server = app.server

def make_figure(data: pd.DataFrame, title_suffix: str = "All Regions"):
    fig = px.line(
        data,
        x="Date",
        y="Sales",
        color="Region",
        title=f"Sales Trend ({title_suffix})",
    )
    fig.update_layout(
        template="plotly_white",
        xaxis_title="Date",
        yaxis_title="Sales",
        legend_title="Region",
        margin=dict(l=40, r=30, t=60, b=40),
    )
    # Safe marker using shape + annotation
    fig.add_shape(
        type="line",
        x0=PRICE_CHANGE_DATE, x1=PRICE_CHANGE_DATE,
        y0=0, y1=1, yref="paper",
        line=dict(width=2, dash="dash")
    )
    fig.add_annotation(
        x=PRICE_CHANGE_DATE, y=1, yref="paper",
        text="Price increase (2021-01-15)",
        showarrow=False, xanchor="left", yanchor="bottom"
    )
    return fig

app.layout = html.Div(
    style={
        "maxWidth": "1100px",
        "margin": "0 auto",
        "padding": "24px",
        "fontFamily": "Inter, system-ui, Segoe UI, Roboto, Helvetica, Arial",
    },
    children=[
        html.Div(
            style={
                "background": "linear-gradient(90deg, #f7cad0, #fbe0e6)",
                "borderRadius": "14px",
                "padding": "18px 22px",
                "marginBottom": "18px",
                "boxShadow": "0 6px 18px rgba(0,0,0,0.08)",
            },
            children=[
                html.H1(
                    "Pink Morsels Sales Over Time",
                    style={"margin": 0, "fontWeight": 800, "color": "#751a3d"},
                ),
                html.P(
                    "Filter by region and inspect sales before/after the 2021-01-15 price increase.",
                    style={"margin": "6px 0 0 0", "color": "#5b5b5b"},
                ),
            ],
        ),
        html.Div(
            style={
                "background": "#fff",
                "borderRadius": "14px",
                "padding": "14px 16px",
                "marginBottom": "14px",
                "boxShadow": "0 6px 18px rgba(0,0,0,0.06)",
            },
            children=[
                html.Div("Select region:", style={"fontWeight": 600, "marginBottom": "8px"}),
                dcc.RadioItems(
                    id="region-selector",
                    options=region_options,
                    value="all",
                    inline=True,
                    inputStyle={"marginRight": "6px"},
                    labelStyle={"marginRight": "16px"},
                    style={"fontSize": "16px"},
                ),
            ],
        ),
        html.Div(
            style={
                "background": "#fff",
                "borderRadius": "14px",
                "padding": "8px 10px",
                "boxShadow": "0 8px 20px rgba(0,0,0,0.08)",
            },
            children=[dcc.Graph(id="sales-graph", style={"height": "70vh"})],
        ),
    ],
)

@app.callback(
    Output("sales-graph", "figure"),
    Input("region-selector", "value"),
)
def update_graph(selected_region):
    if selected_region == "all":
        filtered = df
        suffix = "All Regions"
    else:
        filtered = df[df["_region_key"] == selected_region]
        suffix = selected_region.title()
    return make_figure(filtered, title_suffix=suffix)

if __name__ == "__main__":
    app.run(debug=True, port=int(os.getenv("PORT", "8050")))
