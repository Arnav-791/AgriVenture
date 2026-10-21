import pandas as pd
import random
import math
from datetime import datetime, timedelta


# ------------------------------
# Utility Functions
# ------------------------------

def estimate_distance(lat1, lon1, lat2, lon2):
    """Rough Euclidean distance between two coordinate points."""
    return round(math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) * 111, 2)  # approx km


def random_date(start, end):
    """Generate a random date between start and end."""
    return start + timedelta(days=random.randint(0, (end - start).days))


# ------------------------------
# Farmer Data Generation
# ------------------------------

def generate_farmers_dataframe(num_farmers=200):
    crops = ['Rice', 'Wheat', 'Maize', 'Sugarcane', 'Cotton', 'Millets']
    regions = {
        'North': (28.6, 77.2),
        'South': (12.9, 77.6),
        'East': (22.5, 88.3),
        'West': (19.0, 72.8),
        'Central': (23.2, 79.9)
    }
    farmer_sizes = ['Small', 'Medium', 'Large']

    farmers = []

    for i in range(num_farmers):
        region = random.choice(list(regions.keys()))
        lat, lon = regions[region]

        farmers.append({
            'Farmer_ID': f'F{i + 1:04d}',
            'Region': region,
            'Crop': random.choice(crops),
            'Quantity_kg': random.randint(500, 5000),
            'Availability_Date': random_date(datetime(2025, 6, 1), datetime(2025, 8, 31)).strftime('%Y-%m-%d'),
            'Farmer_Size': random.choices(farmer_sizes, weights=[0.6, 0.3, 0.1])[0],  # bias towards small farmers
            'Latitude': round(lat + random.uniform(-0.5, 0.5), 3),
            'Longitude': round(lon + random.uniform(-0.5, 0.5), 3)
        })

    return pd.DataFrame(farmers)


# ------------------------------
# Company Data Generation
# ------------------------------

def generate_companies_dataframe(num_companies=50):
    crops = ['Rice', 'Wheat', 'Maize', 'Sugarcane', 'Cotton', 'Millets']
    regions = {
        'North': (28.6, 77.2),
        'South': (12.9, 77.6),
        'East': (22.5, 88.3),
        'West': (19.0, 72.8),
        'Central': (23.2, 79.9)
    }

    companies = []

    for i in range(num_companies):
        region = random.choice(list(regions.keys()))
        lat, lon = regions[region]
        preferred_region = region if random.random() < 0.7 else random.choice(list(regions.keys()))

        companies.append({
            'Company_ID': f'C{i + 1:04d}',
            'Preferred_Region': preferred_region,
            'Required_Crop': random.choice(crops),
            'Required_Quantity_kg': random.randint(2000, 10000),
            'Delivery_Deadline': random_date(datetime(2025, 7, 15), datetime(2025, 9, 15)).strftime('%Y-%m-%d'),
            'Latitude': round(lat + random.uniform(-0.5, 0.5), 3),
            'Longitude': round(lon + random.uniform(-0.5, 0.5), 3)
        })

    return pd.DataFrame(companies)



# ------------------------------
# Main Generator Function
# ------------------------------

def generate_and_save_data():
   # random.seed(42)  # reproducibility

    farmers_df = generate_farmers_dataframe()
    companies_df = generate_companies_dataframe()

    farmers_df.to_csv('data/farmers.csv', index=False)
    companies_df.to_csv('data/companies.csv', index=False)
    print(f"Generated {len(farmers_df)} farmers and {len(companies_df)} companies")


# ------------------------------
# Run Generator
# ------------------------------

if __name__ == "__main__":
    generate_and_save_data()
