import pandas as pd
import networkx as nx
import os

# ------------------------------------------------------
# Max-Flow Allocation Algorithm
# ------------------------------------------------------

def run_maxflow(farmers_file="data/farmers.csv", companies_file="data/companies.csv", edges_file="data/edges.csv"):
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
    # Add farmer → company edges
    # ------------------------------------------------------
    for _, farmer in farmers.iterrows():
        G.add_edge("Source", farmer["Farmer_ID"], capacity=int(farmer["Quantity_kg"]))

    for _, company in companies.iterrows():
        G.add_edge(company["Company_ID"], "Sink", capacity=int(company["Required_Quantity_kg"]))

    # Farmer to company connections from edges.csv
    for _, e in edges.iterrows():
        f_id = e["Farmer_ID"]
        c_id = e["Company_ID"]
        distance = e.get("Distance_km", 0)

        # Capacity could depend on distance or be unrestricted
        capacity = max(1, int(farmer["Quantity_kg"] * (100 / (distance + 100))))
        G.add_edge(f_id, c_id, capacity=capacity)

    # ------------------------------------------------------
    # Compute Max Flow
    # ------------------------------------------------------
    flow_value, flow_dict = nx.maximum_flow(G, "Source", "Sink")

    # ------------------------------------------------------
    # Convert Flow Results to Allocation Table
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
    out_path = "results/maxflow_allocation.csv"
    allocation_df.to_csv(out_path, index=False)

    print("✅ Max-Flow Allocation Complete")
    print(f"Total Flow Value (Total Allocated): {flow_value} kg")
    print(f"Allocations Generated: {len(allocation_df)}")
    return allocation_df


# ------------------------------------------------------
# Run directly (for testing)
# ------------------------------------------------------
if __name__ == "__main__":
    run_maxflow()
