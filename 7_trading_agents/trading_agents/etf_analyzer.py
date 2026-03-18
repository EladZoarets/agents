"""ETF Impact Analysis Agent using OpenAI SDK"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
from agents import Agent, Runner, function_tool
import yfinance as yf
import pandas as pd
import numpy as np
from utils.etf_mappings import (
    get_etf_info, get_sector_impact, Sector, EVENT_IMPACT_MATRIX
)
from config.config import TARGET_ETFS, OPENAI_MODEL

logger = logging.getLogger(__name__)


class ETFImpactAnalyzerAgent:
    """Agent for analyzing how news events impact ETF sectors"""
    
    def __init__(self):
        self.agent = Agent(
            name="etf_impact_analyzer",
            instructions="""You are an ETF impact analyst. Your job is to:
1. Receive news classification and sentiment analysis
2. Map events to their impact on different sectors
3. Identify which ETFs will be most affected
4. Calculate probability and magnitude of moves
5. Consider correlations and hedging opportunities
6. Provide clear ACTION signals (CALL/PUT/HOLD)

Use historical patterns and fundamental logic to make predictions.
Be specific about strike prices and expiry dates.
            """
        )
    
    @function_tool
    async def fetch_etf_data(self, symbols: List[str], period: str = "1y") -> Dict:
        """
        Fetch historical ETF price data
        
        Args:
            symbols: List of ETF symbols (e.g., ["XLE", "XLK", "XLF"])
            period: Time period ("1mo", "3mo", "1y", "5y")
        """
        data = {}
        try:
            for symbol in symbols:
                try:
                    etf = yf.Ticker(symbol)
                    hist = etf.history(period=period)
                    
                    current_price = hist['Close'].iloc[-1]
                    previous_close = hist['Close'].iloc[-2]
                    change_pct = ((current_price - previous_close) / previous_close) * 100
                    
                    # Calculate volatility (standard deviation of returns)
                    returns = hist['Close'].pct_change()
                    volatility = returns.std() * np.sqrt(252)  # Annualized
                    
                    data[symbol] = {
                        "current_price": round(current_price, 2),
                        "previous_close": round(previous_close, 2),
                        "change_percent": round(change_pct, 2),
                        "volatility": round(volatility, 4),
                        "52week_high": round(hist['High'].max(), 2),
                        "52week_low": round(hist['Low'].min(), 2),
                        "avg_volume": int(hist['Volume'].mean()),
                    }
                except Exception as e:
                    logger.error(f"Error fetching data for {symbol}: {e}")
                    data[symbol] = {"error": str(e)}
            
            logger.info(f"Fetched data for {len(data)} ETFs")
            return {"status": "success", "data": data}
            
        except Exception as e:
            logger.error(f"Error in fetch_etf_data: {e}")
            return {"status": "error", "message": str(e)}
    
    @function_tool
    async def calculate_sector_impact(self, 
                                     event_type: str,
                                     event_severity: float = 0.8) -> Dict:
        """
        Calculate impact on all sectors from an event
        
        Args:
            event_type: Type of event (war_geopolitical, crisis_recession, rate_cut, etc.)
            event_severity: Severity of event (0-1)
        """
        impacts = {}
        
        # Get base impacts from our matrix
        base_impacts = EVENT_IMPACT_MATRIX.get(event_type, {})
        
        for sector, base_impact in base_impacts.items():
            # Scale by event severity
            adjusted_impact = base_impact * event_severity
            
            # Get ETFs for this sector
            sector_etfs = [sym for sym, info in {
                "XLE": Sector.ENERGY, "XLY": Sector.CONSUMER_DISCRETIONARY
            }.items() if info == sector]
            
            impacts[sector.value] = {
                "impact_score": round(adjusted_impact, 3),
                "direction": "bullish" if adjusted_impact > 0.2 else "bearish" if adjusted_impact < -0.2 else "neutral",
                "magnitude": abs(round(adjusted_impact, 3)),
                "confidence": round(abs(adjusted_impact), 3),
            }
        
        return {
            "event_type": event_type,
            "event_severity": event_severity,
            "sector_impacts": impacts
        }
    
    @function_tool
    async def suggest_etf_positions(self,
                                   event_type: str,
                                   sentiment_score: float,
                                   confidence: float) -> Dict:
        """
        Suggest which ETFs to trade based on event and sentiment
        
        Returns CALL/PUT positions with strike prices
        """
        suggestions = {
            "calls": [],  # Bullish bets
            "puts": []    # Bearish bets
        }
        
        # Get sector impacts
        base_impacts = EVENT_IMPACT_MATRIX.get(event_type, {})
        
        for sector, impact_score in base_impacts.items():
            # Adjust by sentiment
            adjusted_impact = impact_score + (sentiment_score * 0.3)
            
            # Generate action signals
            if adjusted_impact > 0.5 and confidence > 0.7:
                # Strong bullish signal -> Call option
                suggestions["calls"].append({
                    "sector": sector.value,
                    "impact_score": round(adjusted_impact, 3),
                    "recommendation": "BUY CALL",
                    "strength": "strong" if adjusted_impact > 0.7 else "moderate",
                    "expected_move": f"+{round(abs(adjusted_impact) * 100, 1)}%"
                })
            elif adjusted_impact < -0.5 and confidence > 0.7:
                # Strong bearish signal -> Put option
                suggestions["puts"].append({
                    "sector": sector.value,
                    "impact_score": round(adjusted_impact, 3),
                    "recommendation": "BUY PUT",
                    "strength": "strong" if adjusted_impact < -0.7 else "moderate",
                    "expected_move": f"{round(adjusted_impact * 100, 1)}%"
                })
        
        return suggestions
    
    @function_tool
    async def calculate_correlation(self, etf1: str, etf2: str, period: str = "1y") -> float:
        """Calculate correlation between two ETFs"""
        try:
            data1 = yf.download(etf1, period=period, progress=False)
            data2 = yf.download(etf2, period=period, progress=False)
            
            returns1 = data1['Close'].pct_change().dropna()
            returns2 = data2['Close'].pct_change().dropna()
            
            correlation = returns1.corr(returns2)
            return round(correlation, 4)
        except Exception as e:
            logger.error(f"Error calculating correlation: {e}")
            return 0.0
    
    async def run(self,
                 event_classification: Dict,
                 sentiment_data: Dict,
                 etf_symbols: List[str] = None) -> Dict:
        """
        Execute ETF impact analysis workflow
        
        Args:
            event_classification: Classified events from news agent
            sentiment_data: Sentiment analysis results
            etf_symbols: ETFs to analyze (default: all from config)
        
        Returns: Impact analysis with trading suggestions
        """
        logger.info("Starting ETF Impact Analyzer Agent")
        
        symbols = etf_symbols or list(set([
            etf for sector_etfs in TARGET_ETFS.values() 
            for etf in sector_etfs
        ]))
        
        prompt = f"""
Analyze how the identified events will impact ETF sectors and prices.

Events to analyze:
{event_classification}

Current market sentiment:
{sentiment_data}

Your analysis should:
1. For each event, calculate sector-by-sector impact
2. Identify affected ETFs and expected move magnitude
3. Cross-check with sentiment alignment (does sentiment match technical impact?)
4. Suggest specific CALL or PUT trades with confidence levels
5. Flag any hedging opportunities

Target ETFs to analyze: {', '.join(symbols)}

Provide detailed recommendations with:
- etf_impacts: which ETFs move and by how much
- best_calls: top 3 call opportunities
- best_puts: top 3 put opportunities  
- overall_signal: net market direction
- confidence_level: 0-100% on your recommendation

Be specific: give strike suggestions and time horizons.
        """
        
        result = await Runner.run(
            self.agent,
            prompt
        )
        
        return {
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "impact_analysis": result.final_output
        }


async def create_and_run_impact_analyzer(event_data: Dict, sentiment_data: Dict):
    """Convenience function to create and run impact analyzer"""
    agent = ETFImpactAnalyzerAgent()
    return await agent.run(
        event_classification=event_data,
        sentiment_data=sentiment_data
    )
