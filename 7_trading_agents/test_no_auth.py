"""Test OpenClaw without authentication requirement"""
import asyncio
import json
import websockets

OPENCLAW_URL = "ws://127.0.0.1:18792"
AUTH_TOKEN = "e0aced2dc51e67e045546a0a991429fe46697f9ed3e999a1"


async def test_no_auth_with_token_in_url():
    """Test with token in URL"""
    print("\nMethod: Token in URL query string")
    url = f"{OPENCLAW_URL}?token={AUTH_TOKEN}"
    print(f"URL: {url}")
    
    try:
        async with websockets.connect(url) as ws:
            print("✅ Connected")
            
            # Try to fetch news directly
            req = {"type": "fetch_news", "limit": 5}
            print(f"Sending news request...")
            await ws.send(json.dumps(req))
            
            resp = await asyncio.wait_for(ws.recv(), timeout=3.0)
            print(f"✅ Response: {resp[:100]}...")
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)[:80]}")
        return False


async def test_just_send_request():
    """Test sending news request immediately without auth"""
    print("\nMethod: Direct news request (no auth)")
    
    try:
        async with websockets.connect(OPENCLAW_URL) as ws:
            print("✅ Connected")
            
            # Just send a news request
            req = {"type": "fetch_news", "limit": 5}
            print(f"Sending: {json.dumps(req)}")
            await ws.send(json.dumps(req))
            
            # Try to get response
            resp = await asyncio.wait_for(ws.recv(), timeout=3.0)
            resp_data = json.loads(resp)
            print(f"Response type: {resp_data.get('type')}")
            print(f"Response event: {resp_data.get('event')}")
            
            if resp_data.get('type') == 'news_batch' or 'news' in resp_data:
                print(f"✅ Got news: {len(resp_data.get('news', []))} items")
                return True
            else:
                print(f"Got response but not news: {json.dumps(resp_data)[:100]}")
                return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)[:80]}")
        return False


async def test_ignore_challenge():
    """Test ignoring the challenge and just sending requests"""
    print("\nMethod: Ignore challenge, send requests directly")
    
    try:
        async with websockets.connect(OPENCLAW_URL) as ws:
            print("✅ Connected")
            
            # Receive and ignore challenge
            challenge = await asyncio.wait_for(ws.recv(), timeout=3.0)
            print(f"Received (ignoring): {json.loads(challenge).get('event')}")
            
            # Send request anyway
            req = {"type": "fetch_news", "limit": 3}
            print(f"Sending news request anyway...")
            await ws.send(json.dumps(req))
            
            resp = await asyncio.wait_for(ws.recv(), timeout=3.0)
            print(f"Response: {resp[:100]}...")
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)[:80]}")
        return False


async def main():
    print("="*60)
    print("TESTING OPENCLAW WITHOUT AUTHENTICATION")
    print("="*60)
    
    results = []
    
    r1 = await test_no_auth_with_token_in_url()
    results.append(("Token in URL", r1))
    
    r2 = await test_just_send_request()
    results.append(("Direct request", r2))
    
    r3 = await test_ignore_challenge()
    results.append(("Ignore challenge", r3))
    
    print(f"\n{'='*60}")
    print("RESULTS")
    print(f"{'='*60}")
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted")
