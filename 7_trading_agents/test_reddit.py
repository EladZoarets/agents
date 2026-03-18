"""Test script to verify Reddit API credentials work"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, "/Users/eladzoarets/Projects/agents/7_trading_agents")

# Load environment
load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

print("\n" + "="*60)
print("REDDIT API CREDENTIALS TEST")
print("="*60)

print(f"\n📋 Checking .env file:")
print(f"  REDDIT_CLIENT_ID: {'✅ Found' if REDDIT_CLIENT_ID else '❌ Missing'}")
print(f"  REDDIT_CLIENT_SECRET: {'✅ Found' if REDDIT_CLIENT_SECRET else '❌ Missing'}")
print(f"  REDDIT_USER_AGENT: {'✅ Found' if REDDIT_USER_AGENT else '❌ Missing'}")

if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT]):
    print("\n⚠️  Missing Reddit credentials.")
    print("\n📖 Follow this guide to get them:")
    print("   👉 Open: REDDIT_SETUP.md")
    print("   Link: https://www.reddit.com/prefs/apps")
    sys.exit(1)

print(f"\n✅ All credentials found! Testing connection...\n")

try:
    import praw
    print(f"✅ PRAW library installed")
    
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    
    print(f"✅ Reddit client initialized")
    
    # Test: get a few posts from r/stocks
    print(f"\n📊 Fetching 3 hot posts from r/stocks...\n")
    
    count = 0
    for post in reddit.subreddit("stocks").hot(limit=3):
        count += 1
        print(f"  {count}. {post.title[:70]}")
        print(f"     Score: {post.score}, Comments: {post.num_comments}\n")
    
    print("="*60)
    print("✅ SUCCESS! Reddit API is working!")
    print("="*60)
    print("\nYou can now run the full trading system:")
    print("  jupyter notebook orchestrator.ipynb")
    
except ImportError:
    print("❌ PRAW library not installed")
    print("\n   Install with: pip install praw")
    
except praw.exceptions.InvalidAuthentication:
    print("❌ Invalid Reddit credentials")
    print("\n   • Check your REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET")
    print("   • Make sure there are no extra spaces")
    print("   • Regenerate credentials if needed")
    print("   • Wait 5-10 minutes for Reddit API to update")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"\n   Type: {type(e).__name__}")
    print(f"   Suggestion: Check Reddit API setup guide")
