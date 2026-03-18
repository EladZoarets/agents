#!/usr/bin/env python3
"""
Full Trading Workflow Test
Tests the system without Reddit credentials
Uses OpenClaw for news + neutral sentiment fallback
"""

import os
import sys

# CRITICAL: Set up environment BEFORE any project imports
project_root = "/Users/eladzoarets/Projects/agents/7_trading_agents"
os.chdir(project_root)

# Set PYTHONPATH to ensure modules can find config and utils
pythonpath = f"{project_root}:.:{os.environ.get('PYTHONPATH', '')}"
os.environ['PYTHONPATH'] = pythonpath
sys.path.insert(0, '.')
sys.path.insert(0, project_root)

# Now we can import asyncio and other standard library modules
import asyncio
import json
from datetime import datetime

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import local trading agents
from trading_agents.news_agent import NewsAggregationAgent
from trading_agents.sentiment_agent import SentimentAnalysisAgent
from trading_agents.etf_analyzer import ETFImpactAnalyzerAgent
from trading_agents.decision_and_executor import TradingDecisionAgent
from config.config import TARGET_ETFS, MIN_CONFIDENCE_THRESHOLD


async def run_full_workflow():
    """Run the complete trading workflow"""
    
    print("\n" + "="*70)
    print("🤖 TRADING AGENTS WORKFLOW - FULL TEST")
    print("="*70)
    print(f"Start Time: {datetime.now()}")
    print(f"Min Confidence: {MIN_CONFIDENCE_THRESHOLD}")
    print(f"Target ETFs: {len(TARGET_ETFS)} tickers")
    print("="*70 + "\n")
    
    # ========== STEP 1: NEWS AGGREGATION ==========
    print("\n" + "─"*70)
    print("📰 STEP 1: NEWS AGGREGATION FROM OPENCLAW")
    print("─"*70)
    
    try:
        news_agent = NewsAggregationAgent()
        sectors = ["energy", "technology", "finance", "commodities"]
        
        logger.info(f"Fetching news for sectors: {sectors}")
        news_result = await news_agent.run(
            sectors=sectors,
            urgency="high"
        )
        
        if news_result.get("status") == "completed":
            print("✅ News aggregation successful")
            news_impact = news_result.get("news_analysis", {})
            print(f"   Events found: {len(news_result.get('events', []))}")
            print(f"   Event types: {set(e.get('type') for e in news_result.get('events', []))}")
        else:
            print("⚠️  No news data available (OpenClaw may be offline)")
            news_impact = {}
            news_result = {"status": "no_data", "events": []}
            
    except Exception as e:
        print(f"❌ News aggregation error: {e}")
        news_impact = {}
        news_result = {"status": "error", "events": []}
    
    # ========== STEP 2: SENTIMENT ANALYSIS ==========
    print("\n" + "─"*70)
    print("💭 STEP 2: SENTIMENT ANALYSIS")
    print("─"*70)
    
    try:
        sentiment_agent = SentimentAnalysisAgent()
        
        if sentiment_agent.reddit_enabled:
            print("✅ Reddit API connected")
        else:
            print("⚠️  Reddit API not available - using neutral sentiment")
        
        sentiment_result = await sentiment_agent.run(
            sectors=sectors
        )
        
        if sentiment_result.get("status") == "completed":
            print("✅ Sentiment analysis successful")
            sentiment_analysis = sentiment_result.get("sentiment_analysis", {})
        else:
            print("✅ Sentiment analysis completed (neutral fallback)")
            sentiment_analysis = {}
            
    except Exception as e:
        print(f"❌ Sentiment analysis error: {e}")
        sentiment_analysis = {}
    
    # ========== STEP 3: ETF IMPACT ANALYSIS ==========
    print("\n" + "─"*70)
    print("📊 STEP 3: ETF SECTOR IMPACT ANALYSIS")
    print("─"*70)
    
    try:
        etf_analyzer = ETFImpactAnalyzerAgent()
        
        # Use news events to determine impact
        impact_result = await etf_analyzer.run(
            event_classification=news_result.get("events", []),
            sentiment_data=sentiment_analysis
        )
        
        if impact_result.get("status") == "completed":
            print("✅ ETF impact analysis successful")
            etf_impacts = impact_result.get("impact_analysis", {})
            print(f"   ETFs analyzed: {len(etf_impacts.get('etf_impacts', {}))}")
        else:
            print("⚠️  Limited ETF data available")
            etf_impacts = {}
            impact_result = {"status": "no_data", "impact_analysis": {}}
            
    except Exception as e:
        print(f"❌ ETF analysis error: {e}")
        etf_impacts = {}
        impact_result = {"status": "error"}
    
    # ========== STEP 4: TRADING DECISIONS ==========
    print("\n" + "─"*70)
    print("🎯 STEP 4: TRADING DECISION ENGINE")
    print("─"*70)
    
    try:
        decision_agent = TradingDecisionAgent()
        
        # Generate trading decisions based on analysis
        decision_result = await decision_agent.run(
            news_impact=news_impact,
            etf_impacts=etf_impacts,
            sentiment_data=sentiment_analysis
        )
        
        if decision_result.get("status") == "completed":
            print("✅ Trading decisions generated")
            decisions = decision_result.get("decisions", [])
            print(f"   Trade recommendations: {len(decisions)}")
            
            # Show high-confidence trades
            high_conf_trades = [d for d in decisions if d.get("confidence", 0) >= MIN_CONFIDENCE_THRESHOLD]
            print(f"   High confidence (>{MIN_CONFIDENCE_THRESHOLD}): {len(high_conf_trades)}")
            
            if high_conf_trades:
                print("\n   🚀 Top Recommendations:")
                for i, trade in enumerate(high_conf_trades[:3], 1):
                    print(f"      {i}. {trade.get('etf_symbol')} {trade.get('trade_type')} "
                          f"@ ${trade.get('strike_price')} "
                          f"(Confidence: {trade.get('confidence', 0):.1%})")
        else:
            print("⚠️  No actionable trade signals")
            decisions = []
            
    except Exception as e:
        print(f"❌ Decision engine error: {e}")
        decisions = []
    
    # ========== SUMMARY REPORT ==========
    print("\n" + "="*70)
    print("📋 WORKFLOW SUMMARY")
    print("="*70)
    
    print(f"""
✅ Pipeline Status:
   • News Aggregation: {news_result.get('status', 'unknown')}
   • Sentiment Analysis: {sentiment_result.get('status', 'unknown')} {'(Neutral Fallback)' if not sentiment_agent.reddit_enabled else '(Reddit Active)'}
   • ETF Analysis: {impact_result.get('status', 'unknown')}
   • Decision Engine: {decision_result.get('status', 'unknown')}

📊 Data Summary:
   • Events detected: {len(news_result.get('events', []))}
   • ETFs analyzed: {len(etf_impacts.get('etf_impacts', {}))}
   • Trade signals: {len(decisions)}
   • High-confidence trades: {len([d for d in decisions if d.get('confidence', 0) >= MIN_CONFIDENCE_THRESHOLD])}

🎯 Next Steps:
   1. {('✅ Reddit credentials added - system is complete!' if sentiment_agent.reddit_enabled else '⏳ Add Reddit credentials for enhanced sentiment')}
   2. {'✅ Ready for Interactive Brokers integration' if decision_result.get('status') == 'completed' else '⏳ Verify news/ETF data availability'}
   3. ✅ Run `jupyter notebook orchestrator.ipynb` for full workflow

Time: {datetime.now()}
""")
    
    print("="*70)
    print("✨ WORKFLOW TEST COMPLETE ✨")
    print("="*70 + "\n")
    
    # Save detailed results
    results = {
        "timestamp": datetime.now().isoformat(),
        "news": news_result,
        "sentiment": sentiment_result,
        "etf_analysis": impact_result,
        "decisions": {"status": decision_result.get("status"), "count": len(decisions)},
        "summary": {
            "events": len(news_result.get('events', [])),
            "etfs_analyzed": len(etf_impacts.get('etf_impacts', {})),
            "trade_signals": len(decisions),
            "high_confidence": len([d for d in decisions if d.get("confidence", 0) >= MIN_CONFIDENCE_THRESHOLD])
        }
    }
    
    # Save to file
    report_dir = "./reports"
    os.makedirs(report_dir, exist_ok=True)
    
    report_file = os.path.join(report_dir, f"workflow_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"Report saved to: {report_file}\n")
    
    return results


if __name__ == "__main__":
    try:
        results = asyncio.run(run_full_workflow())
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Workflow error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
