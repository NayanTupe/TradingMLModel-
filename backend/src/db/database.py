"""
SQLite database for storing trades, signals, and performance metrics.
"""

import sqlite3
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class TradeDatabase:
    def __init__(self, db_path='trade_logs/trading.db'):
        self.db_path = db_path
        self._create_tables()
    
    def _create_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                stock TEXT,
                entry_price REAL,
                exit_price REAL,
                quantity INTEGER,
                gross_profit REAL,
                net_profit REAL,
                exit_reason TEXT,
                confidence REAL,
                entry_time TEXT,
                exit_time TEXT
            )
        ''')
        
        # Signals table (for paper trading)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                stock TEXT,
                close REAL,
                confidence REAL,
                signal INTEGER,
                regime INTEGER
            )
        ''')
        
        # Daily metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_metrics (
                date TEXT PRIMARY KEY,
                starting_equity REAL,
                ending_equity REAL,
                daily_pnl REAL,
                drawdown REAL,
                num_trades INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database tables created/verified")
    
    def insert_trade(self, trade_dict):
        """Insert a single trade record."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO trades (
                date, stock, entry_price, exit_price, quantity,
                gross_profit, net_profit, exit_reason, confidence,
                entry_time, exit_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trade_dict['date'], trade_dict['stock'], trade_dict['entry_price'],
            trade_dict['exit_price'], trade_dict['quantity'], trade_dict['gross_profit'],
            trade_dict['net_profit'], trade_dict['exit_reason'], trade_dict['confidence'],
            trade_dict['entry_time'], trade_dict['exit_time']
        ))
        conn.commit()
        conn.close()
    
    def insert_signals_batch(self, df_signals):
        """Batch insert signals from DataFrame."""
        conn = sqlite3.connect(self.db_path)
        df_signals.to_sql('signals', conn, if_exists='append', index=False)
        conn.close()
    
    def get_trades_df(self):
        """Return all trades as DataFrame."""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM trades ORDER BY date", conn)
        conn.close()
        return df