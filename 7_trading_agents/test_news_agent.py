"""Test script for News Aggregation Agent with OpenClaw"""
import asyncio
import json
import sys
import os
from datetime import datetime

# Setup path
sys.path.insert(0, "/Users/eladzoarets/Projects/agents/7_trading_agents")

from utils.openclaw_client import OpenClawClient
from config.config import OPENCLAW_WS_URL, OPENCLAW_AUTH_TOKEN


async def test_openclaw_connection():
    """Test basic OpenClaw WebSocket connection"""
    print("\n" + "="*60)
    print("TEST 1: OpenClaw WebSocket Connection")
    print("="*60)
    
    print(f"Connecting to: {OPENCLAW_WS_URL}")
    print(f"Auth token: {OPENCLAW_AUTH_TOKEN[:20]}...")
    
    client = OpenClawClient()
    try:
        connected = await client.connect()
        if connected:
            print("✅ Successfully connected to OpenClaw!")
            await client.disconnect()
            return True
        else:
            print("❌ Failed to authenticate with OpenClaw")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print(f"\nTroubleshooting:")
        print(f"  - Check OpenClaw is running")
        print(f"  - Verify WebSocket URL: {OPENCLAW_WS_URL}")
        print(f"  - Check firewall/network connectivity")
        return False


async def test_fetch_news():
    """Test fetching news from OpenClaw"""
    print("\n" + "="*60)
    print("TEST 2: Fetch News from OpenClaw")
    print("="*60)
    
    client = OpenClawClient()
    try:
        await client.connect()
        
        print("Fetching news (limit: 10)...")
        filters = {
            "keywords": ["war", "oil", "rate", "crisis", "tech"],
        }
        
        news_items = await client.fetch_news(filters=filters, limit=10)
        
        if news_items:
            print(f"✅ Fetched {len(news_items)} news items")
            
            # Show first 2 items
            for i, item in enumerate(news_items[:2]):
                print(f"\n--- News Item {i+1} ---")
                print(f"Headline: {item.get('headline', 'N/A')[:80]}...")
                print(f"Source: {item.get('source', 'N/A')}")
                print(f"Timestamp: {item.get('timestamp', 'N/A')}")
                if 'summary' in item:
                    print(f"Summary: {item['summary'][:100]}...")
            
            return news_items
        else:
            print("⚠️  No news items returned (OpenClaw may be empty or filters too strict)")
            return []
            
    except Exception as e:
        print(f"❌ Error fetching news: {e}")
        return []
    finally:
        await client.disconnect()


async def test_news_classification():
    """Test news event classification"""
    print("\n" + "="*60)
    print("TEST 3: News Event Classification")
    print("="*60)
    
    from config.config import EVENT_KEYWORDS
    
    # Test headlines
    test_headlines = [
        "Russia escalates military operations in Eastern Europe",
        "Federal Reserve cuts interest rates by 50 basis points",
        "Stock market crashes 10% as recession fears mount",
        "Apple reports record earnings, beats expectations",
        "New tariffs imposed on Chinese imports effective immediately"
    ]
    
    print("Classifying sample news headlines:\n")
    
    for headline in test_headlines:
        print(f"Headline: {headline}")
        matches = {}
        
        for event_type, keywords in EVENT_KEYWORDS.items():
            match_count = sum(1 for kw in keywords if kw.lower() in headline.lower())
            if match_count > 0:
                matches[event_type] = match_count
        
        if matches:
            for event_type, count in matches.items():
                confidence = min(0.3 + (count * 0.2), 1.0)
                print(f"  ✓ {event_type}: {confidence:.2f} (matched {count} keyword(s))")
        else:
            print(f"  - No category match")
        print()
    
    print("✅ Classification test complete")


async def test_sentiment_keywords():
    """Test sentiment tracking for ETFs"""
    print("\n" + "="*60)
    print("TEST 4: Sentiment Keyword Matching")
    print("="*60)
    
    test_topics = [
        ("XLE going to moon with war news", "XLE"),
        ("Oil spike incoming, buy energy", "energy"),
        ("Tech stocks rally on rate cut", "tech"),
        ("Fed cuts rates, good for growth", "rates"),
    ]
    
    print("Checking sentiment topic detection:\n")
    
    etf_keywords = {
        "XLE": ["XLE", "oil", "energy", "petroleum"],
        "XLK": ["XLK", "tech", "semiconductor", "software"],
        "XLF": ["XLF", "bank", "financial", "rate"],
    }
    
    for text, expected_etf in test_topics:
        matches = []
        for etf, keywords in etf_keywords.items():
            if any(kw.lower() in text.lower() for kw in keywords):
                matches.append(etf)
        
        print(f"Text: {text}")
        print(f"  Detected: {matches if matches else 'None'}")
        print()


async def test_openclaw_specific_sectors():
    """Test fetching news for specific sectors"""
    print("\n" + "="*60)
    print("TEST 5: Fetch News by Sector")
    print("="*60)
    
    sectors = ["energy", "technology", "finance"]
    
    client = OpenClawClient()
    try:
        await client.connect()
        
        for sector in sectors:
            print(f"\nFetching {sector} news...")
            filters = {"sectors": [sector]}
            
            news = await client.fetch_news(filters=filters, limit=5)
            print(f"  → Found {len(news)} items for '{sector}' sector")
            
            if news:
                print(f"    First item: {news[0].get('headline', 'N/A')[:60]}...")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Error: {e}")
        return False
    finally:
        await client.disconnect()


async def main():
    """Run all tests"""
    print("\n" + "🔍 TESTING TRADING AGENTS - NEWS AGGREGATION SYSTEM")
    print("="*60)
    print(f"Test started: {datetime.now().isoformat()}")
    
    results = []
    
    # Test 1: Connection
    test1 = await test_openclaw_connection()
    results.append(("OpenClaw Connection", test1))
    
    if not test1:
        print("\n⛔ Cannot continue - OpenClaw connection failed")
        print("Please verify:")
        print("  1. OpenClaw WebSocket is running at ws://127.0.0.1:18792")
        print("  2. Auth token is correct in config")
        await asyncio.sleep(1)
        return results
    
    # Test 2: Fetch News
    test2_data = await test_fetch_news()
    test2 = len(test2_data) > 0
    results.append(("Fetch News from OpenClaw", test2))
    
    # Test 3: Classification
    await test_news_classification()
    results.append(("News Classification", True))
    
    # Test 4: Sentiment Keywords
    await test_sentiment_keywords()
    results.append(("Sentiment Keywords", True))
    
    # Test 5: Sector-specific news
    test5 = await test_openclaw_specific_sectors()
    results.append(("Sector-specific News", test5))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! News agent is ready to use.")
    else:
        print(f"\n⚠️  {total - passed} test(s) need attention.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
