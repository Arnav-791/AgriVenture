import pandas as pd
import networkx as nx
import os

# ------------------------------------------------------
# Fairness-Aware Min-Cost Max-Flow Algorithm
# ------------------------------------------------------

def run_fair_mincost_maxflow(
    farmers_file="data/farmers.csv",
    companies_file="data/companies.csv",
    edges_file="data/edges.csv"
):
    # ------------------------------------------------------
    # Load data
    # ------------------------------------------------------
    farmers = pd.read_csv(farmers_file)
    companies = pd.read_csv(companies_file)
    edges = pd.read_csv(edges_file)

    # Create directed graph
    G = nx.DiGraph()

    # Add source and sink
    G.add_node("Source")
    G.add_node("Sink")

    # ------------------------------------------------------
    # Add Farmer and Company nodes
    # ------------------------------------------------------
    for _, farmer in farmers.iterrows():
        G.add_edge("Source", farmer["Farmer_ID"], capacity=int(farmer["Quantity_kg"]), weight=0)

    for _, company in companies.iterrows():
        G.add_edge(company["Company_ID"], "Sink", capacity=int(company["Required_Quantity_kg"]), weight=0)

    # ------------------------------------------------------
    # Add Farmer → Company edges with Fairness-Aware Cost
    # ------------------------------------------------------
    size_factor = {"Small": 0.6, "Medium": 1.0, "Large": 1.4}

    for _, e in edges.iterrows():
        f_id = e["Farmer_ID"]
        c_id = e["Company_ID"]
        distance = e.get("Distance_km", 0)

        # Get farmer info
        farmer_row = farmers.loc[farmers["Farmer_ID"] == f_id].iloc[0]
        farmer_qty = farmer_row["Quantity_kg"]
        farmer_size = farmer_row["Farmer_Size"]

        # Capacity scaled by distance (optional)
        capacity = max(1, int(farmer_qty * (100 / (distance + 100))))

        # Fairness-aware cost: smaller farmers are cheaper
        cost = int(distance * size_factor[farmer_size])

        G.add_edge(f_id, c_id, capacity=capacity, weight=cost)

    # ------------------------------------------------------
    # Compute Fairness-Aware Min-Cost Max-Flow
    # ------------------------------------------------------
    flow_dict = nx.max_flow_min_cost(G, "Source", "Sink", weight="weight")
    total_flow = 0
    total_cost = 0

    for u, v_dict in flow_dict.items():
        for v, flow in v_dict.items():
            if flow > 0 and "weight" in G[u][v]:
                total_flow += flow
                total_cost += flow * G[u][v]["weight"]

    avg_cost = total_cost / total_flow if total_flow > 0 else 0

    # ------------------------------------------------------
    # Convert results into DataFrame
    # ------------------------------------------------------
    allocations = []
    for f_id in farmers["Farmer_ID"]:
        if f_id not in flow_dict:
            continue
        for c_id, flow in flow_dict[f_id].items():
            if flow > 0 and c_id in companies["Company_ID"].values:
                crop = edges.loc[edges["Farmer_ID"] == f_id, "Crop"].iloc[0]
                allocations.append({
                    "Farmer_ID": f_id,
                    "Company_ID": c_id,
                    "Crop": crop,
                    "Quantity_Allocated": flow,
                    "Distance_km": edges.loc[(edges["Farmer_ID"] == f_id) & (edges["Company_ID"] == c_id), "Distance_km"].mean(),
                    "Farmer_Size": farmers.loc[farmers["Farmer_ID"] == f_id, "Farmer_Size"].values[0]
                })

    allocation_df = pd.DataFrame(allocations)

    # ------------------------------------------------------
    # Save Results
    # ------------------------------------------------------
    os.makedirs("results", exist_ok=True)
    out_path = "results/fair_mincost_maxflow_allocation.csv"
    allocation_df.to_csv(out_path, index=False)

    print("✅ Fairness-Aware Min-Cost Max-Flow Allocation Complete")
    print(f"Total Flow Value: {total_flow} kg")
    print(f"Total Transport Cost: {total_cost}")
    print(f"Average Cost per Unit: {avg_cost:.2f}")
    print(f"Allocations Generated: {len(allocation_df)}")

    return allocation_df


# ------------------------------------------------------
# Run directly (for testing)
# ------------------------------------------------------
if __name__ == "__main__":
    run_fair_mincost_maxflow()
