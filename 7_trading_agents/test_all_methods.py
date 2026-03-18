"""Test different OpenClaw authentication formats"""
import asyncio
import json
import websockets
import hashlib
import hmac

OPENCLAW_URL = "ws://127.0.0.1:18792"
AUTH_TOKEN = "e0aced2dc51e67e045546a0a991429fe46697f9ed3e999a1"


async def test_method(name: str, auth_message: dict) -> bool:
    """Test a single authentication method"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"Message: {json.dumps(auth_message)[:100]}...")
    print(f"{'='*60}")
    
    try:
        async with websockets.connect(OPENCLAW_URL) as ws:
            # Receive challenge
            challenge = await asyncio.wait_for(ws.recv(), timeout=3.0)
            challenge_data = json.loads(challenge)
            nonce = challenge_data['payload']['nonce']
            print(f"Received nonce: {nonce[:20]}...")
            
            # Prepare message
            if "$NONCE$" in str(auth_message):
                # Replace placeholder with actual nonce
                msg_str = json.dumps(auth_message).replace('"$NONCE$"', f'"{nonce}"')
                auth_msg = json.loads(msg_str)
            else:
                auth_msg = auth_message
            
            if "response" in str(auth_msg).lower() and "$HMAC$" in str(auth_msg):
                # Compute HMAC
                computed = hmac.new(AUTH_TOKEN.encode(), nonce.encode(), hashlib.sha256).hexdigest()
                msg_str = json.dumps(auth_msg).replace('"$HMAC$"', f'"{computed}"')
                auth_msg = json.loads(msg_str)
            
            print(f"Sending: {json.dumps(auth_msg)[:100]}...")
            await ws.send(json.dumps(auth_msg))
            
            # Get response
            response = await asyncio.wait_for(ws.recv(), timeout=3.0)
            response_data = json.loads(response)
            
            is_success = (
                response_data.get('status') == 'authenticated' or 
                response_data.get('event') == 'connect.authenticated'
            )
            
            if is_success:
                print(f"✅ SUCCESS! Event: {response_data.get('event')}")
                return True
            else:
                print(f"❌ Failed. Response: {json.dumps(response_data)[:100]}...")
                return False
                
    except Exception as e:
        print(f"❌ Error: {str(e)[:80]}")
        return False


async def main():
    methods = [
        ("Method 1: auth.challenge_response with HMAC", {
            "type": "auth.challenge_response",
            "nonce": "$NONCE$",
            "response": "$HMAC$"
        }),
        
        ("Method 2: connect.auth with token", {
            "type": "connect.auth",
            "token": AUTH_TOKEN,
            "nonce": "$NONCE$"
        }),
        
        ("Method 3: challenge_response (simple)", {
            "type": "challenge_response",
            "nonce": "$NONCE$",
            "token": AUTH_TOKEN
        }),
        
        ("Method 4: Just token in response field", {
            "type": "auth.challenge_response",
            "response": AUTH_TOKEN,
            "nonce": "$NONCE$"
        }),
        
        ("Method 5: auth_response with HMAC(token,nonce)", {
            "type": "auth_response",
            "response": "$HMAC$"
        }),
        
        ("Method 6: Simple connect with nonce + token", {
            "type": "connect",
            "token": AUTH_TOKEN,
            "nonce": "$NONCE$"
        }),
    ]
    
    print("\n🔍 TESTING OPENCLAW AUTHENTICATION METHODS\n")
    
    results = []
    for name, msg_template in methods:
        result = await test_method(name, msg_template)
        results.append((name, result))
        if result:
            print(f"\n🎉 Found working method!")
            break
    
    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted")
