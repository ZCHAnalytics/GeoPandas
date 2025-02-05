import pandas as pd

# Load the merged dataset for checking
df = pd.read_csv("outputs/merged_train_station_data.csv")

# Check missing values in key columns
missing_summary = df.isna().sum()
print("Missing values in Merged Dataset:\n", missing_summary)

df_missing = df[df["origin_crs"].isna() | df["destination_crs"].isna()]
print(df_missing.head())

# Save for documentation
df_missing.to_csv("outputs/missing_station_values.csv", index=False)

"""
import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
sns.heatmap(df.isna(), cmap="viridis", cbar=False, yticklabels=False)
plt.title("Missing Data Heatmap")
plt.show()
"""
import numpy as np
import matplotlib.pyplot as plt
# Calculate missing percentage
missing_percentage = (df.isna().sum() / len(df)) * 100

# Plot missing data percentage
missing_percentage[missing_percentage > 0].plot(kind='bar', figsize=(10,5), color="red")
plt.title("Percentage of Missing Values per Column")
plt.ylabel("Percentage")
plt.show()
