"""Diagnostic script for OpenClaw WebSocket protocol"""
import asyncio
import json
import websockets
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

OPENCLAW_URL = "ws://127.0.0.1:18792"
AUTH_TOKEN = "e0aced2dc51e67e045546a0a991429fe46697f9ed3e999a1"


async def test_raw_connection():
    """Test raw WebSocket connection and see what OpenClaw expects"""
    print("="*60)
    print("RAW OPENCLAW PROTOCOL DIAGNOSTIC")
    print("="*60)
    
    try:
        print(f"\nConnecting to: {OPENCLAW_URL}")
        async with websockets.connect(OPENCLAW_URL) as ws:
            print("✅ WebSocket connected!")
            
            print("\n1. Waiting for initial server message...")
            try:
                initial_msg = await asyncio.wait_for(ws.recv(), timeout=3.0)
                print(f"   Received: {initial_msg[:200]}...")
                data = json.loads(initial_msg)
                print(f"   Type: {data.get('type', 'unknown')}")
                print(f"   Event: {data.get('event', 'unknown')}")
                if 'payload' in data:
                    print(f"   Payload keys: {list(data['payload'].keys())}")
            except asyncio.TimeoutError:
                print("   ⏱️  Timeout - no initial message")
            
            print("\n2. Sending auth token directly...")
            msg1 = {"type": "auth", "token": AUTH_TOKEN}
            print(f"   Sending: {json.dumps(msg1)[:100]}...")
            try:
                await ws.send(json.dumps(msg1))
                response = await asyncio.wait_for(ws.recv(), timeout=3.0)
                print(f"   Response: {response[:200]}...")
                data = json.loads(response)
                print(f"   Type: {data.get('type', 'unknown')}")
                print(f"   Event: {data.get('event', 'unknown')}")
            except asyncio.TimeoutError:
                print("   ⏱️  Timeout - no response")
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            print("\n3. Sending auth with payload format...")
            msg2 = {
                "type": "auth",
                "payload": {
                    "token": AUTH_TOKEN
                }
            }
            print(f"   Sending: {json.dumps(msg2)}")
            try:
                await ws.send(json.dumps(msg2))
                response = await asyncio.wait_for(ws.recv(), timeout=3.0)
                print(f"   Response: {response[:200]}...")
                data = json.loads(response)
                print(f"   Success: {data.get('status') == 'authenticated' or data.get('event') == 'connect.authenticated'}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
                
    except ConnectionRefusedError:
        print(f"❌ Connection refused - is OpenClaw running at {OPENCLAW_URL}?")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_news_fetch():
    """Test fetching news once authenticated"""
    print("\n" + "="*60)
    print("TESTING NEWS FETCH")
    print("="*60)
    
    try:
        async with websockets.connect(OPENCLAW_URL) as ws:
            print(f"Connected")
            
            # Try authentication with payload format
            print("Authenticating...")
            auth_msg = {
                "type": "auth",
                "payload": {
                    "token": AUTH_TOKEN
                }
            }
            await ws.send(json.dumps(auth_msg))
            
            # Receive response
            response = await asyncio.wait_for(ws.recv(), timeout=5.0)
            data = json.loads(response)
            
            is_auth = data.get('status') == 'authenticated' or data.get('event') == 'connect.authenticated'
            if is_auth:
                print("✅ Authenticated!")
                
                # Try fetching news
                print("\nFetching news...")
                news_req = {
                    "type": "fetch_news",
                    "filters": {},
                    "limit": 5
                }
                await ws.send(json.dumps(news_req))
                
                # Receive news
                news_response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                print(f"News response: {news_response[:300]}...")
            else:
                print(f"❌ Not authenticated: {data}")
                
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    await test_raw_connection()
    print("\n")
    await test_news_fetch()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted")
