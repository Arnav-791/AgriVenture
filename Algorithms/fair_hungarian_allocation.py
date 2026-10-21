import pandas as pd
import numpy as np
from scipy.optimize import linear_sum_assignment
import os

def run_fair_hungarian(
    farmers_file="data/farmers.csv",
    companies_file="data/companies.csv",
    edges_file="data/edges.csv"
):
    # ------------------------------------------------------
    # Load Data
    # ------------------------------------------------------
    farmers = pd.read_csv(farmers_file)
    companies = pd.read_csv(companies_file)
    edges = pd.read_csv(edges_file)

    farmer_ids = farmers["Farmer_ID"].unique()
    company_ids = companies["Company_ID"].unique()

    # Initialize large cost matrix
    cost_matrix = np.full((len(farmer_ids), len(company_ids)), 1e6)

    # Fairness weighting factors
    fairness_weight = {
        "Small": 0.8,   # Small farmers have 20% reduced cost (higher priority)
        "Medium": 1.0,  # Neutral
        "Large": 1.2    # Large farmers have 20% increased cost (lower priority)
    }

    # Fill cost matrix using distance × fairness weight
    for _, e in edges.iterrows():
        f_id = e["Farmer_ID"]
        c_id = e["Company_ID"]
        distance = e.get("Distance_km", 0)

        # Get farmer index and company index
        f_idx = np.where(farmer_ids == f_id)[0][0]
        c_idx = np.where(company_ids == c_id)[0][0]

        # Determine farmer size and weight
        farmer_size = farmers.loc[farmers["Farmer_ID"] == f_id, "Farmer_Size"].values[0]
        weight = fairness_weight.get(farmer_size, 1.0)

        # Adjusted cost
        adjusted_cost = distance * weight
        cost_matrix[f_idx][c_idx] = adjusted_cost

    # ------------------------------------------------------
    # Run Hungarian Algorithm
    # ------------------------------------------------------
    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    # ------------------------------------------------------
    # Build Allocation Table
    # ------------------------------------------------------
    allocations = []
    for r, c in zip(row_ind, col_ind):
        if cost_matrix[r][c] < 1e6:  # Valid assignment
            f_id = farmer_ids[r]
            c_id = company_ids[c]
            crop = edges.loc[edges["Farmer_ID"] == f_id, "Crop"].iloc[0]
            allocations.append({
                "Farmer_ID": f_id,
                "Company_ID": c_id,
                "Crop": crop,
                "Distance_km": cost_matrix[r][c],
                "Farmer_Size": farmers.loc[farmers["Farmer_ID"] == f_id, "Farmer_Size"].values[0],
                "Quantity_Allocated": min(
                    farmers.loc[farmers["Farmer_ID"] == f_id, "Quantity_kg"].values[0],
                    companies.loc[companies["Company_ID"] == c_id, "Required_Quantity_kg"].values[0]
                )
            })

    allocation_df = pd.DataFrame(allocations)

    # ------------------------------------------------------
    # Save Results
    # ------------------------------------------------------
    os.makedirs("results", exist_ok=True)
    out_path = "results/fair_hungarian_allocation.csv"
    allocation_df.to_csv(out_path, index=False)

    print("✅ Fairness-Aware Hungarian Allocation Complete")
    print(f"Allocations Generated: {len(allocation_df)}")
    return allocation_df


# ------------------------------------------------------
# Run Directly for Testing
# ------------------------------------------------------
if __name__ == "__main__":
    run_fair_hungarian()
