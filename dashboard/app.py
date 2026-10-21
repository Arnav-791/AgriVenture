# app.py — CLEAN FINAL VERSION (NO DUPLICATES, NO PIE PANEL)

import os
import glob
import pandas as pd
import numpy as np
from dash import dash_table
from sklearn.preprocessing import MinMaxScaler

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px


# ---------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------

SCENARIOS_DIR = "scenarios"

ALGORITHM_KEYS = {
    "greedy": "Greedy",
    "maxflow": "Max-Flow",
    "mincostmaxflow": "Min-Cost Max-Flow",
    "fairmincostmaxflow": "Fair Min-Cost Max-Flow",
    "hungarian": "Hungarian",
    "fairhungarian": "Fair Hungarian"
}

METRICS = [
    "Total_Allocated",
    "Demand_Satisfied_%",
    "Supply_Utilized_%",
    "Allocation_Variance",
    "Fairness_Small_Farmers_%",
    "Average_Distance_km"
]


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def list_scenarios():
    if not os.path.exists(SCENARIOS_DIR):
        return []
    return sorted([d for d in os.listdir(SCENARIOS_DIR)
                   if os.path.isdir(os.path.join(SCENARIOS_DIR, d))])


def load_evaluations_for_scenario(scen_path):
    """Loads evaluation CSVs and normalizes algorithm names."""
    files = glob.glob(os.path.join(scen_path, "evaluation_*.csv"))
    if not files:
        return None

    rows = []
    for f in files:
        df = pd.read_csv(f)

        # 1) Extract algorithm key from filename
        key = os.path.basename(f).replace("evaluation_", "").replace(".csv", "").lower()
        algo_label = ALGORITHM_KEYS.get(key, key)

        # 2) Force a single clean algorithm column
        df["Algorithm"] = algo_label

        # 3) Remove leftover raw algorithm columns
        for col in list(df.columns):
            if col.lower() in ["algo", "algorithm_key", "algorithm_raw"]:
                df = df.drop(columns=[col], errors="ignore")

        rows.append(df.iloc[[0]])  # keep first row

    combined = pd.concat(rows, ignore_index=True)

    # Remove duplicates if any
    combined = combined.drop_duplicates(subset=["Algorithm"], keep="first")

    # Convert metrics to numeric
    for c in METRICS:
        if c in combined.columns:
            combined[c] = pd.to_numeric(combined[c], errors="coerce")

    return combined.reset_index(drop=True)


def load_allocation_distances(scen_path):
    """Reads raw *_allocation.csv and extracts Distance_km distributions."""
    files = glob.glob(os.path.join(scen_path, "*_allocation.csv"))
    rows = []

    for f in files:
        df = pd.read_csv(f)

        key = os.path.basename(f).replace("_allocation.csv", "").lower()
        algo_label = ALGORITHM_KEYS.get(key, key)

        if "Distance_km" in df.columns:
            tmp = pd.DataFrame({
                "Distance_km": pd.to_numeric(df["Distance_km"], errors="coerce"),
                "Algorithm": algo_label
            }).dropna()
            if not tmp.empty:
                rows.append(tmp)

    if not rows:
        return None

    return pd.concat(rows, ignore_index=True)


# ---------------------------------------------------------
# CHART BUILDERS
# ---------------------------------------------------------

def create_radar(df_eval, selected):
    if df_eval is None or df_eval.empty:
        return go.Figure()

    df = df_eval.copy().set_index("Algorithm")
    if selected:
        df = df.loc[df.index.intersection(selected)]

    metrics = [m for m in METRICS if m in df.columns]
    if df.empty or not metrics:
        return go.Figure()

    vals = df[metrics].fillna(0).astype(float)

    if len(vals) == 1:
        norm = pd.DataFrame([[0.5] * len(metrics)], index=vals.index, columns=metrics)
    else:
        scaler = MinMaxScaler()
        norm_arr = scaler.fit_transform(vals)
        norm = pd.DataFrame(norm_arr, index=vals.index, columns=metrics)

    fig = go.Figure()
    theta = [m.replace("_", " ") for m in metrics]

    for algo in norm.index:
        fig.add_trace(go.Scatterpolar(
            r=norm.loc[algo].values,
            theta=theta,
            name=algo,
            fill='toself'
        ))

    fig.update_layout(
        title="Radar Chart — Normalized Metrics",
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        legend=dict(orientation="h")
    )
    return fig


def create_bubble(df_eval, selected):
    if df_eval is None:
        return go.Figure()

    df = df_eval.copy()
    if selected:
        df = df[df["Algorithm"].isin(selected)]

    df = df.dropna(subset=["Demand_Satisfied_%", "Fairness_Small_Farmers_%"])
    if df.empty:
        return go.Figure()

    fig = px.scatter(
        df,
        x="Demand_Satisfied_%",
        y="Fairness_Small_Farmers_%",
        size="Total_Allocated",
        color="Algorithm",
        hover_name="Algorithm",
        labels={
            "Demand_Satisfied_%": "Demand Satisfied (%)",
            "Fairness_Small_Farmers_%": "Fairness (%)"
        },
        title="Bubble Chart — Demand vs Fairness"
    )
    fig.update_layout(legend=dict(orientation="h"))
    return fig


def create_distance_box(dist_df, selected):
    if dist_df is None:
        return go.Figure()
    df = dist_df.copy()
    if selected:
        df = df[df["Algorithm"].isin(selected)]

    fig = px.box(
        df,
        x="Algorithm",
        y="Distance_km",
        points="all",
        title="Distance Distribution Across Algorithms"
    )
    fig.update_layout(legend=dict(orientation="h"))
    return fig


# ---------------------------------------------------------
# DASH APP
# ---------------------------------------------------------

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server


def algo_checklist(df):
    if df is None:
        return []
    return [{"label": algo, "value": algo} for algo in df["Algorithm"].unique()]


app.layout = html.Div([
    html.H1("AgriVenture Allocation Dashboard", style={"textAlign": "center"}),

    html.Div([
        html.Label("Select Scenario:"),
        dcc.Dropdown(
            id="scenario",
            options=[{"label": s, "value": s} for s in list_scenarios()],
            value=(list_scenarios()[0] if list_scenarios() else None),
            clearable=False,
            style={"width": "300px", "margin": "auto"}
        )
    ], style={"textAlign": "center"}),

    html.Div(id="algo-container", style={"textAlign": "center", "margin": "15px"}),

    dcc.Tabs(id="tabs", value="radar", children=[
        dcc.Tab(label="Radar", value="radar"),
        dcc.Tab(label="Bubble", value="bubble"),
        dcc.Tab(label="Distance Box", value="box"),
        dcc.Tab(label="Table", value="table"),
    ]),

    html.Div(id="tab-output", style={"padding": "20px"})
])


# ---------------------------------------------------------
# CALLBACKS
# ---------------------------------------------------------

@app.callback(
    Output("algo-container", "children"),
    Input("scenario", "value")
)
def update_algo_list(scen):
    path = os.path.join(SCENARIOS_DIR, scen)
    df = load_evaluations_for_scenario(path)

    if df is None:
        return "No evaluation files found."

    opts = algo_checklist(df)
    vals = [o["value"] for o in opts]

    return html.Div([
        html.Label("Select algorithms:"),
        dcc.Checklist(id="algos", options=opts, value=vals, inline=True)
    ])


@app.callback(
    Output("tab-output", "children"),
    Input("tabs", "value"),
    Input("scenario", "value"),
    Input("algos", "value")
)
def update_tab(tab, scen, selected):
    path = os.path.join(SCENARIOS_DIR, scen)
    df_eval = load_evaluations_for_scenario(path)
    dist_df = load_allocation_distances(path)

    if tab == "radar":
        return dcc.Graph(figure=create_radar(df_eval, selected))

    if tab == "bubble":
        return dcc.Graph(figure=create_bubble(df_eval, selected))

    if tab == "box":
        return dcc.Graph(figure=create_distance_box(dist_df, selected))

    if tab == "table":
        if df_eval is None:
            return "No data available."
        df_f = df_eval.copy()
        if selected:
            df_f = df_f[df_f["Algorithm"].isin(selected)]

        cols = ["Algorithm"] + [c for c in df_f.columns if c != "Algorithm"]
        return dash_table.DataTable(
            columns=[{"name": c, "id": c} for c in cols],
            data=df_f[cols].to_dict("records"),
            sort_action="native",
            page_size=10,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "center"},
            style_header={"fontWeight": "bold"}
        )

    return "Invalid tab."


# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------

if __name__ == "__main__":
    print("Dashboard running at: http://127.0.0.1:8050")
    app.run_server(debug=True)
