# run everything from here
import pandas as pd

df = pd.read_csv('data/processed/combined_data.csv')

print(df.head(10))     # first 10 rows
print(df.tail(10))     # last 10 rows
print(df.columns)      # column names