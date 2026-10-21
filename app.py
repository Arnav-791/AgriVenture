# app.py

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

# ---------- Config ----------
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

# ---------- utility functions ----------
def list_scenarios():
    if not os.path.exists(SCENARIOS_DIR):
        return []
    return sorted([d for d in os.listdir(SCENARIOS_DIR)
                   if os.path.isdir(os.path.join(SCENARIOS_DIR, d))])


def load_evaluations_for_scenario(scen_path):
    files = glob.glob(os.path.join(scen_path, "evaluation_*.csv"))
    if not files:
        return None

    rows = []
    for f in files:
        try:
            df = pd.read_csv(f)
        except Exception:
            continue
        key = os.path.basename(f).replace("evaluation_", "").replace(".csv", "").lower()
        algo_label = ALGORITHM_KEYS.get(key, key)
        df["Algorithm"] = algo_label
        rows.append(df.iloc[[0]])

    if not rows:
        return None

    combined = pd.concat(rows, ignore_index=True)

    for c in METRICS:
        if c in combined.columns:
            combined[c] = pd.to_numeric(combined[c], errors="coerce")

    return combined.reset_index(drop=True)


def load_allocation_distances(scen_path):
    files = glob.glob(os.path.join(scen_path, "*_allocation.csv"))
    rows = []

    for f in files:
        try:
            df = pd.read_csv(f)
        except Exception:
            continue

        base = os.path.basename(f).replace("_allocation.csv", "")
        algo_key = base.lower()
        algo_label = ALGORITHM_KEYS.get(algo_key, algo_key)

        if "Distance_km" in df.columns:
            temp = pd.DataFrame({
                "Distance_km": pd.to_numeric(df["Distance_km"], errors="coerce"),
                "Algorithm": algo_label
            }).dropna(subset=["Distance_km"])

            if not temp.empty:
                rows.append(temp)

    if not rows:
        return None

    return pd.concat(rows, ignore_index=True)


# ---------- Radar ----------
def create_radar_figure(df_eval, selected_algos):
    if df_eval is None or df_eval.empty:
        return go.Figure()

    df = df_eval.set_index("Algorithm").copy()

    if selected_algos:
        df = df.loc[df.index.intersection(selected_algos)]

    metrics = [m for m in METRICS if m in df.columns]

    if not metrics or df.empty:
        return go.Figure()

    vals = df[metrics].fillna(0).astype(float)

    if len(vals) == 1:
        norm = pd.DataFrame([[0.5]*len(metrics)], columns=metrics, index=vals.index)
    else:
        norm_arr = MinMaxScaler().fit_transform(vals)
        norm = pd.DataFrame(norm_arr, columns=metrics, index=vals.index)

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
        title="Radar Chart — normalized metrics",
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        legend=dict(orientation="h"),
        margin=dict(l=30, r=30, t=60, b=30)
    )
    return fig


# ---------- Bubble ----------
def create_bubble_figure(df_eval, selected_algos):
    if df_eval is None or df_eval.empty:
        return go.Figure()

    df = df_eval.copy()

    if selected_algos:
        df = df[df["Algorithm"].isin(selected_algos)]

    if df.empty:
        return go.Figure()

    x = "Demand_Satisfied_%"
    y = "Fairness_Small_Farmers_%"
    size = "Total_Allocated"

    df = df.dropna(subset=[x, y])

    fig = px.scatter(
        df,
        x=x,
        y=y,
        size=size,
        color="Algorithm",
        hover_name="Algorithm",
        labels={x: "Demand Satisfied (%)", y: "Fairness (%)"},
        title="Bubble: Demand vs Fairness"
    )

    fig.update_layout(legend=dict(orientation="h"))
    return fig


# ---------- Distance Box ----------
def create_distance_box_figure_from_alloc(dist_df, selected_algos):
    if dist_df is None or dist_df.empty:
        return go.Figure()

    df = dist_df.copy()

    if selected_algos:
        df = df[df["Algorithm"].isin(selected_algos)]

    fig = px.box(
        df,
        x="Algorithm",
        y="Distance_km",
        points="all",
        title="Distance distribution across algorithms (raw allocations)",
        labels={"Distance_km": "Transport distance (km)"}
    )

    fig.update_layout(margin=dict(l=40, r=30, t=60, b=40))
    return fig


# ---------------- DASH APP LAYOUT ---------------- #

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server


def make_algo_checklist_options(df_eval):
    if df_eval is None:
        return []
    return [{"label": a, "value": a} for a in df_eval["Algorithm"].tolist()]


app.layout = html.Div([
    html.Div([
        html.H1("AgriVenture Allocation Dashboard", style={"textAlign": "center"}),

        html.Div([
            html.Label("Select Scenario:"),
            dcc.Dropdown(
                id="scenario-dropdown",
                options=[{"label": s, "value": s} for s in list_scenarios()],
                value=(list_scenarios()[0] if list_scenarios() else None),
                clearable=False,
                style={"width": "350px"}
            )
        ], style={"textAlign": "center", "padding": "8px"}),

        html.Div(id="algos-container", style={"textAlign": "center", "padding": "8px"}),

    ], style={"borderBottom": "1px solid #ddd", "paddingBottom": 10}),

    dcc.Tabs(id="tabs", value="tab-radar", children=[
        dcc.Tab(label="Radar", value="tab-radar"),
        dcc.Tab(label="Bubble", value="tab-bubble"),
        dcc.Tab(label="Distance Box", value="tab-box"),
        dcc.Tab(label="Table", value="tab-table")
    ]),

    html.Div(id="tab-content", style={"padding": "10px 20px"})
])


# ---------------- CALLBACKS ---------------- #

@app.callback(
    Output("algos-container", "children"),
    Input("scenario-dropdown", "value")
)
def update_algos_container(scenario):
    if not scenario:
        return "No scenarios found."

    scen_path = os.path.join(SCENARIOS_DIR, scenario)
    df_eval = load_evaluations_for_scenario(scen_path)

    options = make_algo_checklist_options(df_eval)
    if not options:
        return html.Div("No evaluation CSVs found for this scenario.", style={"color": "#a00"})

    values = [o["value"] for o in options]

    return html.Div([
        html.Label("Select algorithms to include:"),
        dcc.Checklist(
            id="algorithm-checklist",
            options=options,
            value=values,
            inline=True,
            inputStyle={"margin": "6px"}
        )
    ])


@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "value"),
    Input("scenario-dropdown", "value"),
    Input("algorithm-checklist", "value")
)
def render_tab(tab, scenario, selected_algos):
    scen_path = os.path.join(SCENARIOS_DIR, scenario)
    df_eval = load_evaluations_for_scenario(scen_path)
    dist_df = load_allocation_distances(scen_path)

    if tab == "tab-radar":
        return dcc.Graph(figure=create_radar_figure(df_eval, selected_algos))

    elif tab == "tab-bubble":
        return dcc.Graph(figure=create_bubble_figure(df_eval, selected_algos))

    elif tab == "tab-box":
        return dcc.Graph(figure=create_distance_box_figure_from_alloc(dist_df, selected_algos))

    elif tab == "tab-table":
        if df_eval is None or df_eval.empty:
            return html.Div("No data available.")

        df_table = df_eval.copy()
        if selected_algos:
            df_table = df_table[df_table["Algorithm"].isin(selected_algos)]

        cols = ["Algorithm"] + [c for c in df_table.columns if c != "Algorithm"]

        return dash_table.DataTable(
            id="results-table",
            columns=[{"name": c, "id": c} for c in cols],
            data=df_table[cols].to_dict("records"),
            sort_action="native",
            page_size=10,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "center", "padding": "8px"},
            style_header={"fontWeight": "bold", "backgroundColor": "#f0f0f0"},
            style_data_conditional=[
                {"if": {"column_id": "Algorithm"}, "backgroundColor": "#fafafa", "fontWeight": "bold"}
            ]
        )

    return html.Div("Unknown tab.")


# ----------- RUN APP ----------- #

if __name__ == "__main__":
    print("Starting Dash app — open http://127.0.0.1:8050")
    app.run(debug=True)

