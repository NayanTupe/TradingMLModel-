# combine stocks
import pandas as pd
import os

# Folder path
folder_path = 'data/raw/price/'

# List of selected files
files = [
    'RELIANCE_minute.csv',
    'HDFCBANK_minute.csv',
    'ICICIBANK_minute.csv',
    'INFY_minute.csv',
    'TCS_minute.csv',
    'NIFTY50_minute.csv',
    'NIFTYBANK_minute.csv'
]

df_list = []

for file in files:
    df = pd.read_csv(folder_path + file)
    
    # Add stock name column
    df['stock'] = file.split('_')[0]
    
    df_list.append(df)

# Combine all
combined_df = pd.concat(df_list, ignore_index=True)

# Save
combined_df.to_csv('data/processed/combined_data.csv', index=False)

print("✅ Combined data created")
print(combined_df.head())