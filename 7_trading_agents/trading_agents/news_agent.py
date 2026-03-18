"""News Aggregation Agent using OpenAI SDK"""
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from agents import Agent, Runner, function_tool
import json
from utils.openclaw_client import OpenClawClient
from config.config import OPENAI_MODEL, EVENT_KEYWORDS

logger = logging.getLogger(__name__)


class NewsAggregationAgent:
    """Agent for fetching and processing news from OpenClaw"""
    
    def __init__(self):
        self.openclaw = OpenClawClient()
        self.agent = Agent(
            name="news_aggregator",
            instructions="""You are a financial news analyst agent. Your job is to:
1. Fetch global news from OpenClaw covering key topics: geopolitical events, economic news, company earnings, policy changes
2. Parse and structure the news into actionable insights
3. For each news item, identify: headline, source, timestamp, category (war/crisis/rates/earnings/policy), key entities (companies, countries, sectors)
4. Score relevance to financial markets (0-1)
5. Output structured JSON with all findings

Be thorough and extract ALL relevant market-moving news.
            """
        )
    
    @function_tool
    async def fetch_news_from_openclaw(self, 
                                       sectors: Optional[List[str]] = None,
                                       days_back: int = 7,
                                       urgency: Optional[str] = None) -> Dict:
        """
        Fetch news from OpenClaw
        
        Args:
            sectors: List of sectors to focus on (e.g., ["energy", "technology"])
            days_back: Number of days to look back
            urgency: Filter by urgency level ("breaking", "high", "medium", "low")
        """
        try:
            await self.openclaw.connect()
            
            filters = {}
            if sectors:
                filters["sectors"] = sectors
            if urgency:
                filters["urgency_level"] = urgency
            
            filters["date_from"] = (datetime.now() - timedelta(days=days_back)).timestamp()
            
            news_items = await self.openclaw.fetch_news(filters=filters, limit=100)
            
            logger.info(f"Fetched {len(news_items)} news items from OpenClaw")
            return {
                "status": "success",
                "count": len(news_items),
                "news": news_items
            }
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return {
                "status": "error",
                "message": str(e),
                "news": []
            }
    
    @function_tool
    async def classify_news_event(self, headline: str, summary: Optional[str] = None) -> Dict:
        """
        Classify a news event into categories
        
        Returns event type, severity (0-1), and affected sectors
        """
        event_data = {
            "headline": headline,
            "summary": summary or "",
            "classifications": []
        }
        
        # Check for event keywords
        for event_type, keywords in EVENT_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw.lower() in headline.lower())
            if matches > 0:
                event_data["classifications"].append({
                    "type": event_type,
                    "confidence": min(0.3 + (matches * 0.2), 1.0)  # Higher confidence with more keyword matches
                })
        
        return event_data
    
    @function_tool
    async def parse_market_entities(self, news_text: str) -> Dict:
        """
        Extract market-relevant entities from news text
        Returns: companies, countries, sectors, asset classes mentioned
        """
        # This is a simplified implementation
        # In production, you'd use NER (Named Entity Recognition)
        entities = {
            "companies": [],
            "countries": [],
            "sectors": [],
            "asset_classes": []
        }
        
        # List of keywords to match
        company_keywords = ["OPEC", "Saudi", "Tesla", "Apple", "Microsoft", "Fed", "ECB"]
        sector_keywords = ["energy", "tech", "financial", "consumer", "healthcare"]
        
        for company in company_keywords:
            if company.lower() in news_text.lower():
                entities["companies"].append(company)
        
        for sector in sector_keywords:
            if sector.lower() in news_text.lower():
                entities["sectors"].append(sector)
        
        return entities
    
    async def run(self, 
                 sectors: Optional[List[str]] = None,
                 urgency: Optional[str] = "high") -> Dict:
        """
        Execute the news aggregation workflow
        
        Args:
            sectors: Sectors to analyze (e.g., ["energy", "technology"])
            urgency: Minimum urgency level to include
        
        Returns: Dictionary with all parsed news and classifications
        """
        logger.info("Starting News Aggregation Agent")
        
        prompt = f"""
You are analyzing financial news to identify market-moving events.

Task:
1. Fetch news from our OpenClaw system
2. For each news item, classify it as one of: WAR_GEOPOLITICAL, CRISIS_RECESSION, RATE_CHANGE, EARNINGS, POLICY_CHANGE, OTHER
3. Score confidence (0-1) for how much this impacts financial markets
4. Identify affected sectors and asset classes
5. Return structured analysis

Sectors to prioritize: {sectors or 'all'}
Only include high urgency news: {urgency == 'high'}

Complete this analysis and provide a JSON response with:
- news_items: array of classified news
- total_high_impact: count of high-confidence events
- affected_sectors: list of sectors with impact scores
- recommendation: brief summary of market implications
        """
        
        # Run agent with tools
        result = await Runner.run(
            self.agent,
            prompt
        )
        
        await self.openclaw.disconnect()
        
        return {
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "analysis": result.final_output
        }


async def create_and_run_news_agent(sectors: List[str] = None):
    """Convenience function to create and run news agent"""
    agent = NewsAggregationAgent()
    return await agent.run(sectors=sectors)
