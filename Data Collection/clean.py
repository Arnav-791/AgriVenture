import pandas as pd

# Load and skip possible header row/blank lines
df = pd.read_excel("enaam.xlsx", header=0)

# Drop rows where essential columns are missing
df = df.dropna(subset=["APMC's", "Commodity", "Commodity Traded", "Date"])

# Generate Farmer_ID
df["Farmer_ID"] = ["F" + str(i).zfill(5) for i in range(1, len(df) + 1)]

# Prepare base DataFrame
df_farmers = df[["Farmer_ID", "Commodity", "Commodity Traded", "APMC's", "Date"]].copy()
df_farmers = df_farmers.rename(columns={
    "Commodity": "Crop",
    "Commodity Traded": "Quantity_kg",
    "APMC's": "Location",  # will be updated to lat,lon
    "Date": "Availability_Date"
})

# You'll next merge with a mandi-coordinates lookup to turn Location (APMC name) to "lat,lon"

print(df_farmers.head())
df_farmers.to_csv("farmers_needs_coordinates.csv", index=False)
