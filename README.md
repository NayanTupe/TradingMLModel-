# Data Setup

This project requires data files separately from OneDrive.

## Required folder structure

Trading-System/
├── data/
│   ├── raw/
│   │   ├── options/
│   │   │   └── option_data.csv
│   │   └── price/
│   │       ├── HDFCBANK_minute.csv
│   │       ├── ICICIBANK_minute.csv
│   │       ├── INFY_minute.csv
│   │       ├── NIFTY50_minute.csv
│   │       ├── NIFTYBANK_minute.csv
│   │       ├── RELIANCE_minute.csv
│   │       └── TCS_minute.csv
│   └── processed/
│       ├── combined_data.csv
│       └── features.csv

## Data location

Data is stored in OneDrive Nunnurider account.
Download the data folder and paste it in the project root.



Backtest achieved +488.86 net profit on test sample using confidence filtering, stop loss, target profit, and brokerage simulation.