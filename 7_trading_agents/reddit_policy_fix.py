"""
REDDIT API POLICY ISSUE - SOLUTION
===================================

The message you're getting:
"In order to create an application or use our API you can read our full policies here"

This is Reddit BLOCKING you from creating an app until you understand their rules.
"""

import webbrowser
import os

print("\n" + "="*70)
print("🔴 REDDIT POLICY ACCEPTANCE FLOW")
print("="*70)

print("""

THE PROBLEM:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Reddit now requires you to:
1. ✅ UNDERSTAND their Responsible Builder Policy
2. ✅ ACKNOWLEDGE using API responsibly
3. ✅ THEN create an application

This is a security measure. You MUST follow these steps in order.


THE SOLUTION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1️⃣ : Accept the Policy
   👉 Go to: https://support.reddithelp.com/hc/en-us/articles/42728983564564
   
   • READ the "Responsible Builder Policy" 
   • Scroll down and click "AGREE" or "ACCEPT" button
   • You MUST do this first
   
   ⏱️  This takes 5 minutes


Step 2️⃣ : Create the App
   👉 Then go to: https://www.reddit.com/prefs/apps
   
   • Click "Create Application" at bottom
   • Name: "Trading Agents News"
   • Type: SELECT "script" (NOT "web app" or "installed app")
   • Description: "Market sentiment analysis from Reddit"
   • Redirect URI: http://localhost:8080 (can be anything for scripts)
   • Click "CREATE APP"


Step 3️⃣ : Copy Your Credentials
   
   After creating, you'll see a card like:
   
   ┌──────────────────────────────────────┐
   │  [🤖] Trading Agents News             │
   │  Type: script                          │
   │─────────────────────────────────────  │
   │  Client ID: abcd1234efgh5678ijkl9012 │ ← COPY THIS
   │  Secret:    xyz9876uvwx5432mnop1234  │ ← COPY THIS
   │  Personal Use Token: [info link]     │
   └──────────────────────────────────────┘
   
   Copy those two strings


Step 4️⃣ : Add to .env
   
   Open: /Users/eladzoarets/Projects/agents/7_trading_agents/.env
   
   Replace:
   REDDIT_CLIENT_ID=abcd1234efgh5678ijkl9012
   REDDIT_CLIENT_SECRET=xyz9876uvwx5432mnop1234
   REDDIT_USER_AGENT=TradingAgent/1.0


Step 5️⃣ : Test It
   
   cd /Users/eladzoarets/Projects/agents/7_trading_agents
   python3 test_reddit.py
   
   If you see posts from Reddit → ✅ WORKING!


COMMON MISTAKES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ "I clicked create app but got a policy error"
   → You didn't accept the policy first!
   → Go back to the policy link above and click ACCEPT
   → Wait 30 seconds
   → Try again

❌ "The credentials don't work"
   → Make sure there are NO EXTRA SPACES
   → Copy-paste, don't type them
   → Make sure you selected "script" type, not web app
   → Wait 5-10 minutes for Reddit to sync

❌ "I can't find the 'Create Application' button"
   → Must be on REDDIT.COM (not old.reddit.com)
   → Must be logged in
   → Scroll ALL THE WAY TO BOTTOM of page
   → Click "Create another app" or "Create Application"

❌ "Still not working after 30 minutes"
   → Create a NEW Reddit account
   → Wait 2-3 days
   → Try the API access then
   → Reddit sometimes blocks new accounts


TIMELINE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 5 min  : Read policy & accept
✅ 2 min  : Create app
✅ 2 min  : Copy credentials
✅ 1 min  : Add to .env
✅ 1 min  : Test with test_reddit.py

Total: 11 minutes to get working!


QUESTIONS?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Reddit Policy: https://support.reddithelp.com/hc/en-us/articles/42728983564564
Create App:    https://www.reddit.com/prefs/apps
PRAW Docs:     https://praw.readthedocs.io/

Once you have Reddit working, your full system is ready to go! 🚀

""")

print("="*70)
print("\n")

# Ask if user wants to open the policy page
try:
    response = input("❓ Open Reddit prefs page now? (y/n): ").strip().lower()
    if response == 'y':
        print("Opening https://www.reddit.com/prefs/apps ...\n")
        webbrowser.open("https://www.reddit.com/prefs/apps")
except:
    pass

print("📝 Next: Follow the 5 steps above and come back with your credentials!\n")
