# Simple script to replace values 
import pandas as pd

# Load the merged dataset for checking
df = pd.read_csv("outputs/merged_train_station_data.csv")
 
name_corrections = {
    "Letchworth": "Letchworth Garden City",
    "London Kings Cross": "King's Cross",
}

# Apply the corrections to your columns
df['origin'] = df['origin'].replace(name_corrections)
df['destination'] = df['destination'].replace(name_corrections)

# Check the results
print(df[['origin', 'destination']].head())
