import pandas as pd

df = pd.read_csv("models/lime_background_data.csv")
print("Total NaN values:", df.isna().sum().sum())
print(df.isna().sum())