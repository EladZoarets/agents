"""Configuration for Trading Agents System"""
import os
from dotenv import load_dotenv

load_dotenv()

# OpenClaw Configuration
OPENCLAW_WS_URL = os.getenv("OPENCLAW_WS_URL", "ws://127.0.0.1:18792")
OPENCLAW_AUTH_TOKEN = os.getenv("OPENCLAW_AUTH_TOKEN", "e0aced2dc51e67e045546a0a991429fe46697f9ed3e999a1")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4-turbo"

# Reddit Configuration
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = "TradingAgent/1.0"

# Interactive Brokers Configuration
IB_HOST = os.getenv("IB_HOST", "127.0.0.1")
IB_PORT = int(os.getenv("IB_PORT", "7497"))  # TWS live trading
IB_CLIENT_ID = int(os.getenv("IB_CLIENT_ID", "1"))
IB_ACCOUNT = os.getenv("IB_ACCOUNT")

# Database Configuration
DB_PATH = os.getenv("DB_PATH", "./data/trading.db")
REPORTS_DIR = os.getenv("REPORTS_DIR", "./reports")
DATA_DIR = os.getenv("DATA_DIR", "./data")

# Scheduling Configuration
SCHEDULE_DAY = "monday"  # Run every Monday
SCHEDULE_TIME = "09:00"  # 9:00 AM
TIMEZONE = os.getenv("TIMEZONE", "US/Eastern")

# ETF Configurations
TARGET_ETFS = {
    "energy": ["XLE", "VDE", "OIL"],
    "consumer_discretionary": ["XLY", "VDC", "COMP"],
    "consumer_staples": ["XLP", "VDC"],
    "technology": ["XLK", "VGT", "QQQ"],
    "financials": ["XLF", "VFV"],
    "healthcare": ["XLV", "VHT"],
    "industrials": ["XLI", "VIS"],
    "utilities": ["XLU", "VPU"],
    "materials": ["XLB", "VAW"],
    "real_estate": ["XLRE", "VNQ"],
}

# Trading Parameters
MIN_CONFIDENCE_THRESHOLD = 0.70  # Minimum confidence to trade
OPTION_EXPIRY_DAYS_SHORT = 21  # 3 weeks
OPTION_EXPIRY_DAYS_MID = 56  # 2 months
CALL_STRIKE_OFFSET = 0.02  # 2% above current price
PUT_STRIKE_OFFSET = -0.02  # 2% below current price
MIN_CONTRACT_QUANTITY = 1
MAX_CONTRACT_QUANTITY = 10

# Event Classification Keywords
EVENT_KEYWORDS = {
    "war": ["war", "conflict", "escalat", "military", "attack", "strike", "invasion"],
    "crisis": ["crisis", "crash", "collapse", "panic", "emergency", "recession", "pandemic"],
    "rates": ["rate", "fed", "interest", "monetary", "policy", "inflation", "deflation"],
    "earnings": ["earnings", "beat", "miss", "guidance", "forecast", "surprise", "q1", "q2", "q3", "q4"],
    "policy": ["tariff", "tax", "regulation", "subsidy", "ban", "mandate", "legislation"],
}

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "./logs/trading_agents.log")
