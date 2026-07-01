# Trading System Workspace

This repository is organized as a clean workspace for the ML trading backend and supporting project documentation.

## Structure

```text
Trading-System/
├── backend/                  # Python ML trading system, FastAPI, backtests
│   ├── src/                  # Backend source code
│   ├── configs/              # Strategy/model configuration
│   ├── data/                 # Local market data, ignored by git
│   ├── results/              # Backtest charts and reports
│   ├── saved_models/         # Model metadata; .pkl files ignored by git
│   ├── trade_logs/           # Trade logs used by reports/dashboard
│   ├── notebooks/            # Research notebooks
│   ├── scripts/              # Report generation scripts
│   ├── main.py
│   ├── requirements.txt
│   └── README.md
├── Trading-system-dashboard/ # Separate React dashboard repository
├── docs/                     # Reports, presentations, and portfolio docs
├── .gitattributes
├── .gitignore
└── README.md
```

## Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

FastAPI:

```bash
cd backend
uvicorn src.api.trading_api:app --reload
```

Backend GitHub repository:

```text
https://github.com/NayanTupe/TradingMLModel-
```

## Dashboard

The dashboard is intentionally kept as a separate git repository inside:

```text
Trading-system-dashboard/
```

Run it with:

```bash
cd Trading-system-dashboard
npm install
npm run dev
```

Dashboard GitHub repository:

```text
https://github.com/NayanTupe/trading-system-dashboard
```

## Notes

- Do not commit virtual environments, local datasets, `node_modules`, or generated build folders.
- Large model files such as `*.pkl` should use Git LFS or an external download link.
- Keep dashboard changes inside `Trading-system-dashboard/`.
- Keep backend changes inside `backend/`.
