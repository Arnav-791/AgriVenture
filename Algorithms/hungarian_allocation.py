import pandas as pd
import numpy as np
from scipy.optimize import linear_sum_assignment
import os

def run_hungarian(farmers_file="data/farmers.csv", companies_file="data/companies.csv", edges_file="data/edges.csv"):
    farmers = pd.read_csv(farmers_file)
    companies = pd.read_csv(companies_file)
    edges = pd.read_csv(edges_file)

    # Unique IDs
    farmer_ids = farmers["Farmer_ID"].unique()
    company_ids = companies["Company_ID"].unique()

    # Initialize a large cost matrix (distance only)
    cost_matrix = np.full((len(farmer_ids), len(company_ids)), 1e6)

    # Fill cost matrix with distance values
    for _, e in edges.iterrows():
        f_idx = np.where(farmer_ids == e["Farmer_ID"])[0][0]
        c_idx = np.where(company_ids == e["Company_ID"])[0][0]
        distance = e.get("Distance_km", 0)
        cost_matrix[f_idx][c_idx] = distance

    # Solve using Hungarian Algorithm
    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    # Collect allocations
    allocations = []
    for r, c in zip(row_ind, col_ind):
        if cost_matrix[r][c] < 1e6:  # valid edge
            allocations.append({
                "Farmer_ID": farmer_ids[r],
                "Company_ID": company_ids[c],
                "Crop": edges.loc[edges["Farmer_ID"] == farmer_ids[r], "Crop"].iloc[0],
                "Distance_km": cost_matrix[r][c],
                "Farmer_Size": farmers.loc[farmers["Farmer_ID"] == farmer_ids[r], "Farmer_Size"].values[0],
                "Quantity_Allocated": min(
                    farmers.loc[farmers["Farmer_ID"] == farmer_ids[r], "Quantity_kg"].values[0],
                    companies.loc[companies["Company_ID"] == company_ids[c], "Required_Quantity_kg"].values[0]
                )
            })

    allocation_df = pd.DataFrame(allocations)
    os.makedirs("results", exist_ok=True)
    allocation_df.to_csv("results/hungarian_allocation.csv", index=False)

    print("✅ Hungarian Allocation Complete")
    print(f"Allocations Generated: {len(allocation_df)}")
    return allocation_df
