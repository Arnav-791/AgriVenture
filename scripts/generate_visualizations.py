"""
generate_visualizations.py  — FINAL VERSION (NO PIE CHARTS)

Per scenario generates:
 1) Radar Chart
 2) Bubble Chart
 3) Distance Distribution Box Plot (from *_allocation.csv)

Also generates grouped cross-scenario bar charts.

✔ CLEAN
✔ FINAL
✔ READY TO RUN
"""

import os
import glob
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.preprocessing import MinMaxScaler

# ---------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------

SCENARIOS_DIR = "scenarios"
PLOTS_SUBDIR = "plots"

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

BAR_METRICS = [
    "Total_Allocated",
    "Demand_Satisfied_%",
    "Supply_Utilized_%",
    "Fairness_Small_Farmers_%",
    "Average_Distance_km"
]

# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------

def safe_float(x):
    try:
        return float(x)
    except:
        return None


def ensure(path):
    os.makedirs(path, exist_ok=True)
    return path


def load_evaluations_for_scenario(scen_path):
    rows = []

    for f in glob.glob(os.path.join(scen_path, "evaluation_*.csv")):
        try:
            df = pd.read_csv(f)
        except:
            continue

        key = os.path.basename(f).replace("evaluation_", "").replace(".csv", "").lower()
        algo = ALGORITHM_KEYS.get(key, key)
        df["Algorithm"] = algo

        for m in METRICS:
            if m in df.columns:
                df[m] = df[m].apply(safe_float)

        rows.append(df)

    if not rows:
        return None

    combined = pd.concat(rows, ignore_index=True)
    combined = combined.drop_duplicates(subset=["Algorithm"], keep="first")
    return combined.reset_index(drop=True)

# ---------------------------------------------------------------------
# 1) RADAR CHART
# ---------------------------------------------------------------------

def create_radar(df, scen, out_dir):

    metrics = [m for m in METRICS if m in df.columns]
    scaler = MinMaxScaler()

    vals = df[metrics].astype(float).fillna(0.0)
    if len(vals) == 1:
        scaled = [[0.5] * len(metrics)]
    else:
        scaled = scaler.fit_transform(vals)

    norm = pd.DataFrame(scaled, columns=metrics, index=df["Algorithm"])

    fig = go.Figure()
    for algo in norm.index:
        fig.add_trace(go.Scatterpolar(
            r=norm.loc[algo].values,
            theta=[m.replace("Small_Farmers_%", "Fairness")
                .replace("Demand_Satisfied_%", "Demand %")
                .replace("Supply_Utilized_%", "Supply %")
                .replace("Average_Distance_km", "Avg Dist")
                .replace("Total_Allocated", "Allocated")
                .replace("Allocation_Variance", "Variance")
            for m in metrics],

            name=algo,
            fill="toself",
        ))

    fig.update_layout(
        title=f"Radar Chart — {scen}",
        polar=dict(radialaxis=dict(range=[0,1], visible=True)),
        legend=dict(orientation="h", y=1.1),
        margin=dict(t=120, b=40)
    )

    out = os.path.join(out_dir, f"radar_{scen}.html")
    fig.write_html(out, include_plotlyjs='cdn')
    return out

# ---------------------------------------------------------------------
# 2) BUBBLE CHART
# ---------------------------------------------------------------------

def create_bubble(df, scen, out_dir):

    fig = px.scatter(
        df,
        x="Demand_Satisfied_%",
        y="Fairness_Small_Farmers_%",
        size="Total_Allocated",
        color="Algorithm",
        title=f"Bubble Chart — Fairness vs Demand — {scen}",
        text=df["Algorithm"]
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
        margin=dict(t=80, b=120),
    )

    out = os.path.join(out_dir, f"bubble_{scen}.html")
    fig.write_html(out, include_plotlyjs='cdn')
    return out

# ---------------------------------------------------------------------
# 3) DISTANCE DISTRIBUTION BOX PLOT
# ---------------------------------------------------------------------

def create_distance_distribution_plot(scen_path, scen, out_dir):

    rows = []
    alloc_files = glob.glob(os.path.join(scen_path, "*_allocation.csv"))

    for f in alloc_files:
        df = pd.read_csv(f)
        if "Distance_km" not in df.columns:
            continue

        key = os.path.basename(f).replace("_allocation.csv", "")
        algo = ALGORITHM_KEYS.get(key.lower(), key)

        tmp = df[["Distance_km"]].copy()
        tmp["Algorithm"] = algo
        rows.append(tmp)

    if not rows:
        return None

    dist_df = pd.concat(rows, ignore_index=True)

    fig = px.box(
        dist_df,
        x="Algorithm",
        y="Distance_km",
        points="all",
        title=f"Distance Distribution Across Algorithms — {scen}",
        labels={"Distance_km": "Transport Distance (km)"}
    )

    out = os.path.join(out_dir, f"distance_distribution_{scen}.html")
    fig.write_html(out, include_plotlyjs='cdn')
    return out

# ---------------------------------------------------------------------
# CROSS-SCENARIO BAR CHARTS
# ---------------------------------------------------------------------

def create_bars(all_evals, out_dir):

    rows = []
    for scen, df in all_evals.items():
        for _, r in df.iterrows():
            d = r.to_dict()
            d["Scenario"] = scen
            rows.append(d)

    if not rows:
        return []

    combined = pd.DataFrame(rows)
    saved = []

    for m in BAR_METRICS:
        if m not in combined.columns:
            continue

        fig = px.bar(
            combined,
            x="Algorithm",
            y=m,
            color="Scenario",
            barmode="group",
            title=f"{m} — Across Scenarios"
        )

        out = os.path.join(out_dir, f"bars_{m}.html")
        fig.write_html(out, include_plotlyjs='cdn')
        saved.append(out)

    return saved

# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

def main():

    if not os.path.exists(SCENARIOS_DIR):
        print("❌ No scenarios folder found.")
        return

    scenarios = sorted(os.listdir(SCENARIOS_DIR))
    all_evals = {}

    for scen in scenarios:
        scen_path = os.path.join(SCENARIOS_DIR, scen)
        if not os.path.isdir(scen_path):
            continue

        print(f"\n📁 Scenario: {scen}")
        out_dir = ensure(os.path.join(scen_path, PLOTS_SUBDIR))

        df = load_evaluations_for_scenario(scen_path)
        if df is None:
            print("⚠️ No evaluation CSVs found.")
            continue

        all_evals[scen] = df

        create_radar(df, scen, out_dir)
        print("  ✔ Radar")

        create_bubble(df, scen, out_dir)
        print("  ✔ Bubble")

        create_distance_distribution_plot(scen_path, scen, out_dir)
        print("  ✔ Distance Distribution Box")

    print("\n📊 Generating cross-scenario comparison charts...")
    master = ensure(os.path.join(SCENARIOS_DIR, "plots"))
    create_bars(all_evals, master)

    print("\n✅ All visualizations generated!")

if __name__ == "__main__":
    main()
