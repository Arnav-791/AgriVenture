import pandas as pd
import math
import random


# ----------------------------------------
# Helper Function: Haversine Distance
# ----------------------------------------

def haversine(lat1, lon1, lat2, lon2):
    """Calculate real-world distance between two points (km)."""
    R = 6371  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2

    return round(2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 2)


# ----------------------------------------
# Graph Builder Function (CLEAN VERSION)
# ----------------------------------------

def build_bipartite_graph(
        farmers_file="data/farmers.csv",
        companies_file="data/companies.csv",
        output_file="data/edges.csv"):

    farmers = pd.read_csv(farmers_file)
    companies = pd.read_csv(companies_file)

    edges = []

    for _, comp in companies.iterrows():
        for _, fam in farmers.iterrows():

            # 1️⃣ Crop Matching
            if comp['Required_Crop'] != fam['Crop']:
                continue

            # 2️⃣ Availability <= Deadline
            if fam['Availability_Date'] > comp['Delivery_Deadline']:
                continue

            # 3️⃣ Distance Constraint
            distance = haversine(fam['Latitude'], fam['Longitude'],
                                 comp['Latitude'], comp['Longitude'])

            if distance > 250:     # max 250 km
                continue

            # 4️⃣ Regional Preference (soft rule)
            if fam['Region'] != comp['Preferred_Region'] and random.random() < 0.7:
                continue

            # 5️⃣ Weight Calculation (no perishability)
            # Higher weight = more preferred assignment
            weight = max(1, round(1000 / (distance + 1), 2))

            # Small Farmer Boost to maintain fairness idea
            if fam['Farmer_Size'] == 'Small':
                weight *= 1.1

            edges.append({
                'Farmer_ID': fam['Farmer_ID'],
                'Company_ID': comp['Company_ID'],
                'Crop': fam['Crop'],
                'Distance_km': distance,
                'Weight': round(weight, 2)
            })

    edges_df = pd.DataFrame(edges)
    edges_df.to_csv(output_file, index=False)

    print(f"✅ Graph built successfully with {len(edges_df)} edges.")
    print(f"Average distance: {round(edges_df['Distance_km'].mean(), 2)} km")
    print(f"Average weight: {round(edges_df['Weight'].mean(), 2)}")

    return edges_df


# ----------------------------------------
# Run Script
# ----------------------------------------

if __name__ == "__main__":
    random.seed(42)
    build_bipartite_graph()
