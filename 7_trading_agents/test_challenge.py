"""Fixed diagnostic - compute proper challenge response"""
import asyncio
import json
import websockets
import hashlib
import hmac
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENCLAW_URL = "ws://127.0.0.1:18792"
AUTH_TOKEN = "e0aced2dc51e67e045546a0a991429fe46697f9ed3e999a1"


async def test_with_challenge_response():
    """Test with proper challenge-response authentication"""
    print("\n" + "="*60)
    print("OPENCLAW CHALLENGE-RESPONSE AUTH (HMAC-SHA256)")
    print("="*60)
    
    try:
        async with websockets.connect(OPENCLAW_URL) as ws:
            print("✅ WebSocket connected!")
            
            print("\n1. Receiving challenge...")
            challenge_msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
            challenge = json.loads(challenge_msg)
            print(f"   Event: {challenge.get('event')}")
            print(f"   Nonce: {challenge['payload']['nonce']}")
            
            if challenge.get('event') != 'connect.challenge':
                print(f"   ❌ Expected 'connect.challenge', got '{challenge.get('event')}'")
                return
            
            nonce = challenge['payload']['nonce']
            print(f"\n2. Computing challenge response...")
            print(f"   Using HMAC-SHA256(nonce, token)")
            
            # Try method 1: HMAC(nonce with token as key)
            response1 = hmac.new(
                AUTH_TOKEN.encode(),
                nonce.encode(),
                hashlib.sha256
            ).hexdigest()
            print(f"   Response (method 1): {response1[:32]}...")
            
            # Send response
            print(f"\n3. Sending challenge response...")
            auth_response = {
                "type": "auth.challenge_response",
                "payload": {
                    "response": response1,
                    "nonce": nonce
                }
            }
            await ws.send(json.dumps(auth_response))
            
            # Check response
            print(f"   Waiting for authentication result...")
            result = await asyncio.wait_for(ws.recv(), timeout=5.0)
            result_data = json.loads(result)
            print(f"   Response: {json.dumps(result_data, indent=2)[:200]}...")
            
            if result_data.get('event') == 'connect.authenticated':
                print(f"\n✅ AUTHENTICATED!")
                return True
            else:
                print(f"\n❌ Not authenticated: {result_data}")
                
                # Try method 2: token + nonce
                print(f"\n4. Trying method 2: token + nonce concatenation...")
                response2 = hmac.new(
                    nonce.encode(),
                    AUTH_TOKEN.encode(),
                    hashlib.sha256
                ).hexdigest()
                
                await ws.send(json.dumps({
                    "type": "auth.challenge_response",
                    "payload": {"response": response2}
                }))
                
                result2 = await asyncio.wait_for(ws.recv(), timeout=5.0)
                result2_data = json.loads(result2)
                print(f"   Response: {result2_data}")
                
                if result2_data.get('event') == 'connect.authenticated':
                    print(f"✅ Method 2 worked!")
                    return True
                else:
                    print(f"❌ Method 2 also failed")
                    return False
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    await test_with_challenge_response()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted")
