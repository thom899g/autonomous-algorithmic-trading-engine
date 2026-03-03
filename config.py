"""
Configuration management for the trading engine.
Centralizes all environment variables and settings.
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ExchangeConfig:
    """Exchange API configuration"""
    name: str = "binance"
    api_key: Optional[str] = os.getenv("EXCHANGE_API_KEY")
    api_secret: Optional[str] = os.getenv("EXCHANGE_API_SECRET")
    testnet: bool = True  # Always use testnet in development

@dataclass
class FirebaseConfig:
    """Firebase configuration for state management"""
    credentials_path: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase-credentials.json")
    project_id: str = os.getenv("FIREBASE_PROJECT_ID")
    database_url: str = os.getenv("FIREBASE_DATABASE_URL")

@dataclass
class TradingConfig:
    """Trading engine configuration"""
    default_symbol: str = "BTC/USDT"
    default_timeframe: str = "1h"
    initial_capital: float = 10000.0
    max_position_size: float = 0.1  # 10% of portfolio per trade
    stop_loss_pct: float = 0.02  # 2% stop loss
    take_profit_pct: float = 0.04  # 4% take profit

@dataclass
class Config:
    """Main configuration container"""
    exchange: ExchangeConfig = ExchangeConfig()
    firebase: FirebaseConfig = FirebaseConfig()
    trading: TradingConfig = TradingConfig()
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    def validate(self) -> bool:
        """Validate critical configuration"""
        if not self.firebase.credentials_path or not os.path.exists(self.firebase.credentials_path):
            raise FileNotFoundError(f"Firebase credentials not found at {self.firebase.credentials_path}")
        if not self.firebase.project_id:
            raise ValueError("FIREBASE_PROJECT_ID environment variable is required")
        return True

config = Config()