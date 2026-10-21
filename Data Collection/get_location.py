import pandas as pd
from geopy.geocoders import Nominatim
import time 

# Load your cleaned farmers file
farmers = pd.read_csv('farmers_needs_coordinates.csv')

# Get sorted unique mandi/APMC names
mandi_list = sorted(farmers['Location'].unique())
geolocator = Nominatim(user_agent="agri_locator")
results = []

for name in mandi_list:
    try:
        # Use 'APMC' keyword for better geo search
        query = f"{name} APMC, India"
        location = geolocator.geocode(query)
        if location:
            results.append({
                'Location': name,
                'Latitude': location.latitude,
                'Longitude': location.longitude
            })
        else:
            # Try plain name as fallback
            location = geolocator.geocode(f"{name}, India")
            if location:
                results.append({
                    'Location': name,
                    'Latitude': location.latitude,
                    'Longitude': location.longitude
                })
            else:
                results.append({'Location': name, 'Latitude': None, 'Longitude': None})
    except Exception as e:
        results.append({'Location': name, 'Latitude': None, 'Longitude': None})
    time.sleep(1)  # Be polite to API

df_coords = pd.DataFrame(results)
df_coords.to_csv('mandi_coordinates.csv', index=False)

print(df_coords.head())