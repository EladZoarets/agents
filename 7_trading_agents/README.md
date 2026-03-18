# Trading Agents System

Automated multi-agent financial analysis and options trading system using **OpenAI Agent SDK**, **OpenClaw** news feeds, **Reddit sentiment**, and **Interactive Brokers** for autonomous weekly trading decisions.

## System Overview

```
┌─────────────────┐
│   OpenClaw      │
│  News Feed      │ ──┐
└─────────────────┘   │
                      ├──→ Agent 1: News Aggregation
┌─────────────────┐   │    └─→ Classify events
│    Reuters      │ ──┘     (War/Crisis/Rates/etc)
│    Bloomberg    │
└─────────────────┘

┌─────────────────┐
│     Reddit      │
│  r/stocks       │ ──→ Agent 2: Sentiment Analysis
│  r/investing    │     └─→ Sentiment scores (-1 to +1)
└─────────────────┘

┌─────────────────┐
│    yfinance     │
│    ETF Prices   │ ──→ Agent 3: ETF Impact Analyzer
└─────────────────┘     └─→ Sector impact matrix

                        Agent 4: Trading Decision Engine
                        └─→ Options recommendations
                        
                        Agent 5: Report Generator
                        └─→ Excel analysis file
                        
                        Agent 6: IB Executor
                        └─→ Execute actual trades
```

## Quick Start

### 1. Installation

```bash
cd /Users/eladzoarets/Projects/agents/7_trading_agents

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy template and configure
cp .env.template .env

# Edit .env with your credentials:
# - OPENCLAW_WS_URL & token (you have this)
# - OPENAI_API_KEY
# - REDDIT_CLIENT_ID & SECRET (from Reddit API)
# - Interactive Brokers credentials (IB_ACCOUNT, etc)
```

### 3. Run the Workflow

```bash
jupyter notebook orchestrator.ipynb
```

The notebook will:
1. ✅ Fetch news from OpenClaw
2. ✅ Analyze sentiment from Reddit
3. ✅ Calculate ETF impacts
4. ✅ Make trading decisions
5. ✅ Execute trades via Interactive Brokers (if confidence > 70%)
6. ✅ Generate report & track positions

## Agents

### Agent 1: News Aggregation (`agents/news_agent.py`)
Fetches global news from OpenClaw and classifies events:
- **War/Geopolitical**: Impact on oil, defense, safe-haven assets
- **Crisis/Recession**: Market-wide risk-off behavior
- **Rate Changes**: Fed policy → bond yields → sector rotation
- **Earnings**: Company-specific to sector trend identification
- **Policy**: Tariffs, regulations, subsidies

**Output**: Event classifications with severity scores (0-1)

### Agent 2: Sentiment Analysis (`agents/sentiment_agent.py`)
Analyzes Reddit discussions for market sentiment:
- Scrapes Reddit (r/stocks, r/investing, sector-specific)
- NLP sentiment analysis (bullish/bearish)
- Calculates engagement volume
- Validates signals against actual trading activity

**Output**: Sentiment scores (-1 to +1) by sector/ETF

### Agent 3: ETF Impact Analyzer (`agents/etf_analyzer.py`)
Maps events → sector impacts:
- Correlates events with historical sector performance
- Identifies affected ETF symbols
- Calculates expected move magnitude
- Finds hedging opportunities

**Output**: Sector impact matrix with expected % moves

### Agent 4: Decision Engine (`agents/decision_and_executor.py`)
Makes final trading decisions:

```
Confidence Score = (News Impact × 0.6) + (Sentiment × 0.4)

IF Confidence > 0.70 AND Positive Impact:
  → BUY CALL (3-week expiry)
ELSE IF Confidence > 0.70 AND Negative Impact:
  → BUY PUT (3-week expiry)
ELSE:
  → SKIP (insufficient signal)
```

**Output**: Trade recommendations with strikes, quantities, stops

### Agent 5: Report Generator
Creates Excel analysis file with:
- News summary
- Sentiment dashboard
- Impact matrix (short/mid/long-term)
- Trade recommendations
- Historical comparisons

### Agent 6: Interactive Brokers Executor
Executes trades via TWS API:
- Validates orders
- Places calls/puts
- Sets stops & profits
- Logs all trades
- Tracks P&L

## Event Impact Matrix

Example: When **War escalates in Middle East**

| Sector | Impact | Direction | Trade |
|--------|--------|-----------|-------|
| Energy (XLE) | +0.85 | Bullish | **BUY CALL** |
| Financials (XLF) | -0.65 | Bearish | **BUY PUT** |
| Industrials (XLI) | +0.70 | Bullish | **BUY CALL** |
| Tech (XLK) | +0.50 | Bullish | **BUY CALL** |
| Consumer (XLY) | -0.60 | Bearish | **BUY PUT** |

Example: When **Fed cuts rates**

| Sector | Impact | Direction | Trade |
|--------|--------|-----------|-------|
| Technology (XLK) | +0.75 | Bullish | **BUY CALL** |
| Growth (QQQ) | +0.80 | Bullish | **BUY CALL** |
| Utilities (XLU) | -0.50 | Bearish | **BUY PUT** |
| Financials (XLF) | -0.60 | Bearish | **BUY PUT** |
| Bonds (TLT) | -0.40 | Bearish | **BUY PUT** |

## Configuration

### ETFs Monitored (default)

```python
TARGET_ETFS = {
    "energy": ["XLE", "VDE"],
    "technology": ["XLK", "VGT", "QQQ"],
    "consumer_discretionary": ["XLY"],
    "consumer_staples": ["XLP"],
    "financials": ["XLF"],
    "healthcare": ["XLV"],
    "industrials": ["XLI"],
    "utilities": ["XLU"],
    "materials": ["XLB"],
    "real_estate": ["XLRE", "VNQ"],
}
```

### Trading Parameters

- **Confidence Threshold**: 70% (requires this to trade)
- **Option Expiry**: 3 weeks (21 days)
- **Strike Offset**: 2% above current (calls), 2% below (puts)
- **Risk per Trade**: 2% of account
- **Stop Loss**: 5% per position
- **Take Profit**: 15% per position
- **Max Positions**: 10 concurrent

## Data Storage

### SQLite Database (`./data/trading.db`)
- News events with timestamps
- Event classifications
- Sentiment scores
- Analysis results

### Position Tracking (`./data/positions.json`)
- Active trades
- Entry price/date
- Current P&L
- Expiry dates

### Reports (`./reports/`)
- Excel analysis files (weekly)
- Trade execution logs
- Historical performance

## Scheduling for Automatic Runs

To run automatically every **Monday at 9:00 AM**:

```python
# Create scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from orchestrator_main import run_full_workflow
import asyncio

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=lambda: asyncio.run(run_full_workflow()),
    trigger="cron",
    day_of_week="mon",
    hour=9,
    minute=0,
    timezone="US/Eastern"
)

scheduler.start()

# Keep scheduler running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    scheduler.shutdown()
```

## Risk Management

### Position Sizing
```
Position Size = (Account × 2%) × Confidence × Volatility Adjustment
```

### Stop Loss & Take Profit
- **Stop Loss**: Automatic at 5% loss
- **Take Profit**: Automatic at 15% gain
- **Trailing Stop**: Can be enabled for winners

### Circuit Breakers
- Skip trades if volatility > 50% annualized
- Maximum 10 concurrent positions
- Pause if account drawdown > 10%

## Weekly Workflow

Every Monday 9:00 AM:

1. **Check Active Positions** (from last week)
   - Review P&L
   - Decide: HOLD / CLOSE / ADD

2. **Run Analysis** (fresh news & sentiment)
   - Fetch latest news
   - Analyze sentiment
   - Calculate impacts

3. **Make Decisions** (new positions)
   - Identify high-confidence opportunities
   - Calculate position sizes
   - Get ready to execute

4. **Execute** (if confidence > 70%)
   - Place orders
   - Set stops/profits
   - Log trades

5. **Report** (document everything)
   - Excel with all analysis
   - Position summary
   - Next week outlook

## Files Structure

```
7_trading_agents/
├── orchestrator.ipynb          # Main entry point (jupyter notebook)
├── requirements.txt            # Python dependencies
├── .env.template              # Configuration template
├── config/
│   └── config.py              # All configuration settings
├── utils/
│   ├── openclaw_client.py      # OpenClaw WebSocket client
│   └── etf_mappings.py         # ETF database & impact matrices
├── agents/
│   ├── news_agent.py           # News aggregation
│   ├── sentiment_agent.py       # Reddit sentiment
│   ├── etf_analyzer.py          # Impact analysis
│   └── decision_and_executor.py # Decisions & IB execution
├── data/
│   ├── trading.db              # SQLite database
│   └── positions.json          # Active positions
└── reports/
    ├── analysis_2026-03-09.xlsx # Weekly Excel reports
    └── executed_trades.csv      # Trade log
```

## Next Steps

1. **Setup OpenClaw**: Ensure WebSocket is running at `ws://127.0.0.1:18792`
2. **Get API Keys**:
   - OpenAI: `sk-...`
   - Reddit: OAuth credentials
   - Interactive Brokers: Account setup, TWS/Gateway running on port 7497
3. **Configure .env**: Fill in all credentials
4. **Run Orchestrator**: `jupyter notebook orchestrator.ipynb`
5. **Monitor First Run**: Watch for errors, validate trades
6. **Schedule Automation**: Setup APScheduler for Monday 9 AM runs

## Troubleshooting

### OpenClaw Connection Error
```
Error: Failed to connect to OpenClaw at ws://127.0.0.1:18792
Solution: Check OpenClaw is running and WebSocket port is correct
```

### OpenAI API Error
```
Error: openai.error.AuthenticationError
Solution: Set OPENAI_API_KEY in .env correctly
```

### Interactive Brokers Connection
```
Error: Cannot connect to IB
Solution: 
- Start TWS or IB Gateway
- Ensure listening on port 7497 (live) or 7496 (paper)
- Check IB_HOST and IB_PORT in .env
```

### Low Confidence Trades
```
No trades executed - all were below 70% confidence
Solution: This is actually good - means system is being conservative
Try with lower MIN_CONFIDENCE_THRESHOLD if you want more trades
```

## Performance Metrics to Track

- **Win Rate**: % of profitable trades
- **Avg Win/Loss Ratio**: Average gain vs loss
- **Sharpe Ratio**: Risk-adjusted returns
- **Max Drawdown**: Largest peak-to-trough decline
- **Confidence Accuracy**: How often high-confidence trades win

## Disclaimer

⚠️ **This system makes real trades with real money via Interactive Brokers.**

- Start with **paper trading** (port 7496) to validate strategy
- Use **small position sizes** initially
- Monitor **every run** until you trust the system
- **This is not financial advice** - you are responsible for your trades
- Past performance ≠ future results

## Support & Development

For issues or enhancements:
1. Check logs in `./logs/trading_agents.log`
2. Review executed trades in `./reports/executed_trades.csv`
3. Validate OpenClaw, Reddit, and IB connections
4. Test with paper trading before live

Good luck! 🚀📈💰
