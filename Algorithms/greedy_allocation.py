import pandas as pd
import os
from datetime import datetime

# ------------------------------------------------------
# Greedy Allocation Algorithm
# ------------------------------------------------------

def greedy_allocate(farmers_file="data/farmers.csv", companies_file="data/companies.csv", edges_file="data/edges.csv"):
    # ------------------------------------------------------
    # Load and Preprocess Data
    # ------------------------------------------------------
    farmers = pd.read_csv(farmers_file)
    companies = pd.read_csv(companies_file)
    edges = pd.read_csv(edges_file)

    # Merge extra info into edges
    edges = edges.merge(companies[['Company_ID', 'Delivery_Deadline']], on='Company_ID', how='left')
    edges = edges.merge(farmers[['Farmer_ID', 'Farmer_Size', 'Quantity_kg']], on='Farmer_ID', how='left')

    # Convert date columns
    edges['Delivery_Deadline'] = pd.to_datetime(edges['Delivery_Deadline'], errors='coerce')
    farmers['Availability_Date'] = pd.to_datetime(farmers['Availability_Date'], errors='coerce')

    # Prioritize: distance → deadline → small farmers
    size_priority = {'Small': 1, 'Medium': 2, 'Large': 3}
    edges['Size_Priority'] = edges['Farmer_Size'].map(size_priority)
    edges = edges.sort_values(
        by=['Distance_km', 'Delivery_Deadline', 'Size_Priority'],
        ascending=[True, True, True]
    ).reset_index(drop=True)

    # ------------------------------------------------------
    # Initialize allocation trackers
    # ------------------------------------------------------
    farmer_remaining = farmers.set_index('Farmer_ID')['Quantity_kg'].to_dict()
    company_remaining = companies.set_index('Company_ID')['Required_Quantity_kg'].to_dict()

    allocations = []

    # ------------------------------------------------------
    # Core Greedy Allocation Loop
    # ------------------------------------------------------
    for _, edge in edges.iterrows():
        f_id = edge['Farmer_ID']
        c_id = edge['Company_ID']
        crop = edge['Crop']

        # Skip exhausted entities
        if farmer_remaining.get(f_id, 0) <= 0 or company_remaining.get(c_id, 0) <= 0:
            continue

        # Allocate minimal of remaining supply/demand
        alloc_qty = min(farmer_remaining[f_id], company_remaining[c_id])

        allocations.append({
            'Farmer_ID': f_id,
            'Company_ID': c_id,
            'Crop': crop,
            'Quantity_Allocated': alloc_qty,
            'Distance_km': edge.get('Distance_km', 0),
            'Farmer_Size': edge.get('Farmer_Size', None),
            'Delivery_Deadline': edge['Delivery_Deadline'].strftime("%Y-%m-%d") if pd.notnull(edge['Delivery_Deadline']) else None
        })

        # Update remaining supply/demand
        farmer_remaining[f_id] -= alloc_qty
        company_remaining[c_id] -= alloc_qty

    # ------------------------------------------------------
    # Create Allocation DataFrame
    # ------------------------------------------------------
    allocation_df = pd.DataFrame(allocations)

    # ✅ Ensure 'Farmer_Size' column exists (fallback fix)
    if 'Farmer_Size' not in allocation_df.columns or allocation_df['Farmer_Size'].isnull().any():
        allocation_df['Farmer_Size'] = allocation_df['Farmer_ID'].map(
            farmers.set_index('Farmer_ID')['Farmer_Size']
        )

    # Save results
    os.makedirs("results", exist_ok=True)
    allocation_df.to_csv("results/greedy_allocation.csv", index=False)

    # ------------------------------------------------------
    # Basic Evaluation Metrics
    # ------------------------------------------------------
    total_demand = companies['Required_Quantity_kg'].sum()
    total_supply = farmers['Quantity_kg'].sum()
    total_allocated = allocation_df['Quantity_Allocated'].sum()

    demand_satisfied = (total_allocated / total_demand) * 100 if total_demand > 0 else 0
    supply_utilized = (total_allocated / total_supply) * 100 if total_supply > 0 else 0

    # Fairness: % of total allocation to small farmers
    small_alloc = allocation_df[allocation_df['Farmer_Size'] == 'Small']['Quantity_Allocated'].sum()
    fairness_ratio = (small_alloc / total_allocated * 100) if total_allocated > 0 else 0

    # ------------------------------------------------------
    # Print Summary
    # ------------------------------------------------------
    print("✅ Greedy Allocation Complete")
    print(f"Total Allocations: {len(allocation_df)}")
    print(f"Total Quantity Allocated: {total_allocated} kg")
    print(f"Demand Satisfied: {demand_satisfied:.2f}%")
    print(f"Supply Utilized: {supply_utilized:.2f}%")
    print(f"Fairness Ratio (Small Farmers): {fairness_ratio:.2f}%")

    return allocation_df


# ------------------------------------------------------
# Run Script
# ------------------------------------------------------
if __name__ == "__main__":
    greedy_allocate()
