import pandas as pd
from math import radians, cos, sin, asin, sqrt

def haversine(lat1, lon1, lat2, lon2):
    # compute distance between two lat/lon points
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Earth radius in km
    return c * r

def build_graph(farmers_path, companies_path, output_edges_path):
    farmers = pd.read_csv(farmers_path)
    companies = pd.read_csv(companies_path)

    edges = []
    for _, comp in companies.iterrows():
        for _, fam in farmers.iterrows():
            if comp['RequiredCrop'] == fam['Crop'] and fam['AvailabilityDate'] <= comp['DeliveryDeadline']:
                dist = haversine(
                    float(fam['Location'].split(',')[0]), float(fam['Location'].split(',')[1]),
                    float(comp['Location'].split(',')[0]), float(comp['Location'].split(',')[1])
                )
                max_alloc = min(fam['Quantitykg'], comp['RequiredQuantitykg'])
                edges.append({
                    'FarmerID': fam['FarmerID'],
                    'CompanyID': comp['CompanyID'],
                    'Crop': fam['Crop'],
                    'DistanceKm': dist,
                    'MaxAlloc': max_alloc,
                    'FarmerQty': fam['Quantitykg'],
                    'CompanyQty': comp['RequiredQuantitykg']
                })
    df_edges = pd.DataFrame(edges)
    df_edges.to_csv(output_edges_path, index=False)

if __name__ == "__main__":
    build_graph('farmers.csv', 'companies.csv', 'edges.csv')
