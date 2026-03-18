# Reddit API Setup Guide for Trading Agents

## ✅ You Already Have
- OpenAI API Key: ✔️ sk-proj-...

## 🎯 Step-by-Step: Get Reddit API Credentials

### Step 1: Review Reddit's Responsible Builder Policy
1. Go to: https://support.reddithelp.com/hc/en-us/articles/42728983564564-Responsible-Builder-Policy
2. **Read and understand** the policy (takes 5 min)
3. Make sure your use case aligns (market sentiment analysis = reasonable)

### Step 2: Create Reddit Application
1. Go to: https://www.reddit.com/prefs/apps
2. Scroll down to **"Create Application"** button
3. Fill in form:
   ```
   Name: Trading Agents News Analyzer
   App Type: Script [SELECT THIS]
   Description: Automated market sentiment analysis from Reddit discussions
   Redirect URI: http://localhost:8080
   (or any valid URI, not important for script apps)
   ```
4. Click **"Create App"**

### Step 3: Get Your Credentials
After creating app, you'll see a card with:
```
┌─────────────────────────────┐
│ Trading Agents News ...     │
│ Type: Script                │
│─────────────────────────────│
│ Client ID: [THIS ONE]       │  ← Copy this
│ Secret:    [THIS ONE]       │  ← Copy this
│ Personal Use Token: [link]  │
└─────────────────────────────┘
```

### Step 4: Add to .env

Copy these three values and add to your `.env` file:

```bash
# In /Users/eladzoarets/Projects/agents/.env
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=TradingAgent/1.0 (by your_reddit_username)
```

## ⚠️ Common Issues & Solutions

### Issue 1: "Policy Violation" or "Responsible Builder Policy" Error
**Solution:**
- You must accept the policy BEFORE creating an app
- Check your Reddit account settings
- Make sure you're logged into the right account
- Clear browser cache and try again

### Issue 2: Can't Find "Create Application" Button
**Solution:**
- Make sure you're at: https://www.reddit.com/prefs/apps (while logged in)
- Not on old.reddit.com - use new Reddit
- Scroll to the BOTTOM of the page
- Button says "Create App" or "Create Application"

### Issue 3: "Invalid Redirect URI"
**Solution:**
- Put `http://localhost:8080` or `http://localhost:3000`
- For scripts, this doesn't matter much
- Just needs to be a valid-looking URL

## 🔐 Security Best Practices

1. **Never commit credentials to git**:
   ```bash
   git add .env
   echo ".env" >> .gitignore
   ```

2. **Rotate secrets quarterly** (Reddit app settings)

3. **Use script type** (not web app) for automation

4. **Have a rate-limiting strategy** (Reddit allows 60 requests/min)

## ✅ Verify It Works

Once you have the credentials, test them:

```bash
cd /Users/eladzoarets/Projects/agents/7_trading_agents

# Create test_reddit.py with:
import praw

reddit = praw.Reddit(
    client_id="your_client_id",
    client_secret="your_client_secret",
    user_agent="TradingAgent/1.0"
)

# Test: fetch top posts from r/stocks
for post in reddit.subreddit("stocks").hot(limit=3):
    print(post.title)

# If you see post titles → ✅ Working!
```

## 📋 Full .env Template

Once you have all credentials:

```bash
# OpenAI (you have this ✅)
OPENAI_API_KEY=sk-proj-...

# Reddit API (get from https://www.reddit.com/prefs/apps)
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=TradingAgent/1.0

# OpenClaw (you have this ✅)
OPENCLAW_WS_URL=ws://127.0.0.1:18792
OPENCLAW_AUTH_TOKEN=e0aced2dc51e67e045546a0a991429fe46697f9ed3e999a1

# Interactive Brokers (if using)
IB_HOST=127.0.0.1
IB_PORT=7497
IB_ACCOUNT=your_account_number
```

## 🚀 Next Steps After Reddit Setup

1. Add Reddit credentials to `.env`
2. Run: `python3 test_sentiment_agent.py`
3. Then run full system: `jupyter notebook orchestrator.ipynb`

## 📞 Still Having Issues?

### If "Policy Violation" persists:
- Reddit may have flagged your account
- Create a fresh Reddit account dedicated to bot use
- Wait 1-2 weeks before applying for API access
- Be very specific about your use case (market analysis)

### If credentials don't work:
- Copy-paste (don't retype) - no extra spaces!
- Check you're using script type, not web app
- Verify the app actually appears in your apps list
- Try again in 5-10 minutes (API caching)

---

Good luck! Once you get Reddit setup, the full system will work perfectly. 🚀
