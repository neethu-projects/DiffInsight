import pandas as pd

df = pd.read_csv(r"..\..\data\raw\dataset_raw.csv")

df["diff"] = df["diff"].fillna("")

print(df.shape)
print(df.isnull().sum())
print(df.head())