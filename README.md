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


## Latest Backtest Result

Initial Balance: 100000  
Final Balance: 100488.86  
Net Profit: +488.86  
Total Trades: 11  
Win Rate: 36.36%  
Average Net Profit Per Trade: 44.44  

Settings:
- Confidence Threshold: 0.60
- Stop Loss: 0.20%
- Target: 0.50%
- Capital Per Trade: 100000
- Brokerage: 0.005%
- Hold Candles: 30




## Optimized Backtest Result ACCURCY INCREASE WIN INCREASE

Initial Balance: 100000  
Final Balance: 103368.98  
Total Net Profit: +3368.98  
Total Trades: 14  
Win Rate: 57.14%  
Average Net Profit Per Trade: +240.64  

Settings:
- Confidence Threshold: 0.58
- Stop Loss: 0.25%
- Target Profit: 0.70%
- Hold Candles: 30
- Brokerage: 0.005%



## Features

- Historical market data processing
- Technical indicator based feature engineering
- VWAP, ATR, RSI, Moving Averages, Volume Spike
- Random Forest ML model
- Confidence based trade filtering
- Stop loss and target profit logic
- Brokerage/transaction cost simulation
- Backtest optimization
- GitHub-ready project structure