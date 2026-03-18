"""Sentiment Analysis Agent using OpenAI SDK"""
import logging
from typing import List, Dict, Optional
from datetime import datetime
from agents import Agent, Runner, function_tool
from config.config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT

logger = logging.getLogger(__name__)

# Try to import Reddit libraries, but make it optional
try:
    import praw
    from textblob import TextBlob
    REDDIT_AVAILABLE = True
except ImportError:
    REDDIT_AVAILABLE = False


class SentimentAnalysisAgent:
    """Agent for analyzing market sentiment from Reddit and other sources"""
    
    def __init__(self):
        self.reddit = None
        self.reddit_enabled = False
        self.agent = Agent(
            name="sentiment_analyzer",
            instructions="""You are a market sentiment analyst. Your job is to:
1. Analyze social media discussions (Reddit) for market sentiment
2. Identify trending tickers and sectors
3. Calculate bullish/bearish sentiment scores (-1.0 to 1.0)
4. Detect unusual activity or consensus patterns
5. Cross-reference with actual price action

Be specific about which sectors and ETFs show strong sentiment signals.
Distinguish between retail hype and legitimate fundamental analysis.

NOTE: If Reddit API is unavailable, return neutral sentiment (0.0) for all sectors.
            """
        )
        # Try to initialize Reddit if credentials are available
        if REDDIT_AVAILABLE and REDDIT_CLIENT_ID != "PASTE_YOUR_CLIENT_ID_HERE":
            self.connect_reddit()
    
    def connect_reddit(self):
        """Initialize Reddit API connection"""
        if not REDDIT_AVAILABLE:
            logger.warning("Reddit libraries not available. Sentiment analysis will use neutral scores.")
            return
            
        if REDDIT_CLIENT_ID == "PASTE_YOUR_CLIENT_ID_HERE":
            logger.warning("Reddit credentials not configured. Sentiment analysis will use neutral scores.")
            return
            
        try:
            self.reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT
            )
            self.reddit_enabled = True
            logger.info("✓ Connected to Reddit API")
        except Exception as e:
            logger.warning(f"Could not connect to Reddit: {e}. Will use neutral sentiment scores.")
    
    @function_tool
    async def scrape_reddit_sentiment(self, 
                                      subreddits: List[str] = None,
                                      keywords: List[str] = None,
                                      time_filter: str = "week") -> Dict:
        """
        Scrape Reddit for market sentiment
        
        Args:
            subreddits: List of subreddits (default: r/stocks, r/investing, r/energy, etc.)
            keywords: Keywords to search for (e.g., ["XLE", "oil", "energy"])
            time_filter: Time period ("day", "week", "month")
        """
        default_subreddits = ["stocks", "investing", "wallstreetbets", "energy", "technology"]
        subs = subreddits or default_subreddits
        
        sentiment_data = {
            "timestamp": datetime.now().isoformat(),
            "subreddits_analyzed": subs,
            "posts": [],
            "summary": {},
            "reddit_available": self.reddit_enabled
        }
        
        # If Reddit is not available, return neutral sentiment
        if not self.reddit_enabled:
            logger.info("Reddit API unavailable - returning neutral sentiment scores")
            sentiment_data["summary"] = {
                "average_sentiment": 0.0,
                "total_posts": 0,
                "total_engagement": 0,
                "sentiment_label": "neutral",
                "note": "Reddit API not available - using neutral sentiment"
            }
            return sentiment_data
        
        try:
            for subreddit_name in subs:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                for post in subreddit.top(time_filter=time_filter, limit=50):
                    # Filter by keywords if provided
                    if keywords:
                        if not any(kw.lower() in post.title.lower() for kw in keywords):
                            continue
                    
                    # Simple sentiment analysis
                    text = f"{post.title} {post.selftext}"
                    from textblob import TextBlob
                    blob = TextBlob(text)
                    
                    post_data = {
                        "title": post.title,
                        "score": post.score,
                        "comments": post.num_comments,
                        "sentiment": round(blob.sentiment.polarity, 3),  # -1 to 1
                        "subreddit": subreddit_name,
                        "created_utc": post.created_utc,
                    }
                    
                    sentiment_data["posts"].append(post_data)
            
            # Calculate aggregate sentiment
            if sentiment_data["posts"]:
                avg_sentiment = sum(p["sentiment"] for p in sentiment_data["posts"]) / len(sentiment_data["posts"])
                total_engagement = sum(p["score"] + p["comments"] for p in sentiment_data["posts"])
                
                sentiment_data["summary"] = {
                    "average_sentiment": round(avg_sentiment, 3),
                    "total_posts": len(sentiment_data["posts"]),
                    "total_engagement": total_engagement,
                    "sentiment_label": "bullish" if avg_sentiment > 0.2 else "bearish" if avg_sentiment < -0.2 else "neutral"
                }
            
            logger.info(f"Analyzed {len(sentiment_data['posts'])} Reddit posts")
            return sentiment_data
            
        except Exception as e:
            logger.error(f"Error scraping Reddit: {e}")
            # Return neutral sentiment on error
            return {
                "status": "error",
                "reddit_available": False,
                "message": str(e),
                "summary": {
                    "average_sentiment": 0.0,
                    "sentiment_label": "neutral"
                }
            }
    
    @function_tool
    async def analyze_sector_sentiment(self, sector: str, days: int = 7) -> Dict:
        """Analyze sentiment specifically for a sector (e.g., 'energy', 'tech')"""
        sector_keywords = {
            "energy": ["XLE", "oil", "energy", "gas", "petroleum"],
            "technology": ["XLK", "tech", "semiconductor", "software", "AI"],
            "consumer": ["XLY", "consumer", "retail", "shopping", "demand"],
            "finance": ["XLF", "bank", "financial", "stock market", "rate"],
        }
        
        keywords = sector_keywords.get(sector.lower(), [sector])
        result = await self.scrape_reddit_sentiment(keywords=keywords)
        
        # Add sector context
        result["sector"] = sector
        result["sector_context"] = f"Analyzing posts related to {sector} sector"
        
        # If Reddit unavailable, ensure we have neutral sentiment
        if not self.reddit_enabled and "summary" not in result:
            result["summary"] = {
                "average_sentiment": 0.0,
                "total_posts": 0,
                "sentiment_label": "neutral"
            }
        
        return result
    
    @function_tool
    async def calculate_sentiment_confidence(self, 
                                           sentiment_score: float,
                                           engagement_volume: int,
                                           post_count: int) -> Dict:
        """
        Calculate confidence in sentiment signal
        
        High confidence = consistent sentiment + high engagement + many posts
        """
        # Normalize metrics
        engagement_conf = min(engagement_volume / 10000, 1.0)  # Normalize to 0-1
        consistency_conf = abs(sentiment_score)  # 0 = conflicting, 1 = unanimous
        volume_conf = min(post_count / 100, 1.0)  # More posts = more confidence
        
        overall_confidence = (engagement_conf * 0.4 + consistency_conf * 0.4 + volume_conf * 0.2)
        
        return {
            "overall_confidence": round(overall_confidence, 3),
            "engagement_confidence": round(engagement_conf, 3),
            "consistency_confidence": round(consistency_conf, 3),
            "volume_confidence": round(volume_conf, 3),
            "signal_strength": "strong" if overall_confidence > 0.7 else "moderate" if overall_confidence > 0.4 else "weak"
        }
    
    async def run(self, 
                 sectors: List[str] = None,
                 keywords: List[str] = None) -> Dict:
        """
        Execute sentiment analysis workflow
        
        Args:
            sectors: Sectors to analyze (e.g., ["energy", "technology"])
            keywords: Specific keywords/ETFs to analyze
        
        Returns: Sentiment analysis results with confidence scores
        """
        logger.info("Starting Sentiment Analysis Agent")
        
        if not self.reddit_enabled:
            logger.warning("⚠️  Reddit API not configured - using neutral sentiment for all sectors")
        
        default_sectors = sectors or ["energy", "technology", "finance", "consumer"]
        
        prompt = f"""
Analyze current market sentiment from Reddit discussions (or use neutral if unavailable).

Task:
1. Scan Reddit communities for discussion about: {', '.join(default_sectors)}
2. Find mentions of relevant ETFs and keywords: {', '.join(keywords or ['XLE', 'XLK', 'XLF', 'XLY'])}
3. Calculate sentiment score for each sector/ETF
4. Identify trending topics and consensus views
5. Assess confidence in the sentiment signals

Provide structured analysis with:
- sentiment_by_sector: dict with sector -> sentiment_score
- trending_tickers: list of most discussed ETFs
- consensus_view: what the majority thinks is happening
- sentiment_confidence: how confident we are in these signals (0-1)
- unusual_activity: any surprising sentiment patterns
- reddit_status: whether real Reddit data was used or neutral fallback

Be honest about signal strength - don't overstate weak signals.
If Reddit is unavailable, use neutral sentiment (0.0) for all sectors.
        """
        
        result = await Runner.run(
            self.agent,
            prompt
        )
        
        return {
            "status": "completed",
            "reddit_enabled": self.reddit_enabled,
            "timestamp": datetime.now().isoformat(),
            "sentiment_analysis": result.final_output
        }


async def create_and_run_sentiment_agent(sectors: List[str] = None, keywords: List[str] = None):
    """Convenience function to create and run sentiment agent"""
    agent = SentimentAnalysisAgent()
    return await agent.run(sectors=sectors, keywords=keywords)
