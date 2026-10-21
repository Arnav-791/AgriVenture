import pandas as pd

# Load Excel file
df = pd.read_excel('enaam.xlsx')

# Show all column names
print(df.columns)

# Show the first few rows to inspect data structure
print(df.head())
