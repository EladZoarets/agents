"""Trading Agents Package

NOTE: This package should be imported as:
  from agents.news_agent import NewsAggregationAgent
  from agents.sentiment_agent import SentimentAnalysisAgent
  etc.

Do NOT use: from agents import NewsAggregationAgent
as this will cause circular imports with the OpenAI agents SDK.
"""

# Lazy imports to avoid circular dependency with OpenAI agents SDK
def __getattr__(name):
    if name == "NewsAggregationAgent":
        from agents.news_agent import NewsAggregationAgent
        return NewsAggregationAgent
    elif name == "SentimentAnalysisAgent":
        from agents.sentiment_agent import SentimentAnalysisAgent
        return SentimentAnalysisAgent
    elif name == "ETFImpactAnalyzerAgent":
        from agents.etf_analyzer import ETFImpactAnalyzerAgent
        return ETFImpactAnalyzerAgent
    elif name == "TradingDecisionAgent":
        from agents.decision_and_executor import TradingDecisionAgent
        return TradingDecisionAgent
    elif name == "InteractiveBrokersExecutor":
        from agents.decision_and_executor import InteractiveBrokersExecutor
        return InteractiveBrokersExecutor
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "NewsAggregationAgent",
    "SentimentAnalysisAgent",
    "ETFImpactAnalyzerAgent",
    "TradingDecisionAgent",
    "InteractiveBrokersExecutor"
]

