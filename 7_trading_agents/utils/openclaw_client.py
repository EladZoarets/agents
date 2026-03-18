"""OpenClaw WebSocket Client for News Aggregation"""
import asyncio
import json
import logging
import hashlib
import hmac
from typing import Optional, List, Dict, Callable
import websockets
from datetime import datetime

logger = logging.getLogger(__name__)


class OpenClawClient:
    """WebSocket client for OpenClaw news feed"""
    
    def __init__(self, ws_url: str = None, auth_token: str = None):
        # Lazy import config to avoid circular dependencies
        if ws_url is None or auth_token is None:
            try:
                from config.config import OPENCLAW_WS_URL, OPENCLAW_AUTH_TOKEN
                ws_url = ws_url or OPENCLAW_WS_URL
                auth_token = auth_token or OPENCLAW_AUTH_TOKEN
            except ImportError:
                # Fallback if config not available
                ws_url = ws_url or "ws://127.0.0.1:18792"
                auth_token = auth_token or "e0aced2dc51e67e045546a0a991429fe46697f9ed3e999a1"
        
        self.ws_url = ws_url
        self.auth_token = auth_token
        self.websocket = None
        self.is_connected = False
        self.news_buffer: List[Dict] = []
        self.callbacks: List[Callable] = []
        
    def _get_authenticated_url(self) -> str:
        """Build WebSocket URL with token in query string"""
        separator = "&" if "?" in self.ws_url else "?"
        return f"{self.ws_url}{separator}token={self.auth_token}"
        
    async def _handle_challenge(self, challenge_data: Dict) -> str:
        """Handle OpenClaw challenge-response authentication"""
        try:
            nonce = challenge_data.get("payload", {}).get("nonce")
            if not nonce:
                logger.error("No nonce received in challenge")
                return None
            
            # Create HMAC-SHA256 challenge response
            # Format: HMAC-SHA256(nonce, token)
            challenge_response = hmac.new(
                self.auth_token.encode(),
                nonce.encode(),
                hashlib.sha256
            ).hexdigest()
            
            logger.debug(f"Generated challenge response for nonce: {nonce}")
            return challenge_response
        except Exception as e:
            logger.error(f"Error handling challenge: {e}")
            return None
        
    async def connect(self) -> bool:
        """Establish WebSocket connection to OpenClaw with token in URL"""
        try:
            # Use authenticated URL with token in query string
            auth_url = self._get_authenticated_url()
            self.websocket = await websockets.connect(auth_url)
            logger.info(f"Connected to WebSocket at {self.ws_url}")
            
            # Just wait for initial server response (challenge)
            # We don't need to respond to it - connection is authenticated via URL
            try:
                initial_response = await asyncio.wait_for(
                    self.websocket.recv(),
                    timeout=3.0
                )
                challenge_data = json.loads(initial_response)
                logger.debug(f"Received: {challenge_data.get('event')}")
                
                # Connection is authenticated! We can proceed
                self.is_connected = True
                logger.info("✅ Successfully connected to OpenClaw")
                return True
                
            except asyncio.TimeoutError:
                # If no response, we're still connected
                self.is_connected = True
                logger.info("✅ Connected to OpenClaw (no challenge response)")
                return True
                
        except Exception as e:
            logger.error(f"Failed to connect to OpenClaw: {e}")
            return False
    
    async def fetch_news(self, 
                        filters: Optional[Dict] = None,
                        limit: int = 100) -> List[Dict]:
        """
        Fetch news from OpenClaw with optional filters
        
        Args:
            filters: Dict with keywords, categories, date_range, etc.
            limit: Maximum number of news items to fetch
            
        Returns:
            List of news dictionaries with headline, summary, source, timestamp, etc.
        """
        if not self.is_connected:
            await self.connect()
        
        try:
            request_message = {
                "type": "fetch_news",
                "filters": filters or {},
                "limit": limit
            }
            
            await self.websocket.send(json.dumps(request_message))
            
            # Receive news response (may come in chunks)
            news_data = []
            while len(news_data) < limit:
                try:
                    response = await asyncio.wait_for(
                        self.websocket.recv(),
                        timeout=5.0
                    )
                    response_data = json.loads(response)
                    
                    if response_data.get("type") == "news_batch":
                        news_data.extend(response_data.get("news", []))
                    elif response_data.get("type") == "news_end":
                        break
                        
                except asyncio.TimeoutError:
                    break
            
            self.news_buffer = news_data
            logger.info(f"Fetched {len(news_data)} news items from OpenClaw")
            return news_data
            
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []
    
    async def subscribe_to_stream(self, 
                                  keywords: Optional[List[str]] = None,
                                  categories: Optional[List[str]] = None,
                                  callback: Optional[Callable] = None) -> None:
        """
        Subscribe to real-time news stream from OpenClaw
        
        Args:
            keywords: List of keywords to filter (e.g., ["war", "oil", "rate"])
            categories: News categories (e.g., ["geopolitical", "economic"])
            callback: Async function to call on each news item
        """
        if not self.is_connected:
            await self.connect()
        
        if callback:
            self.callbacks.append(callback)
        
        try:
            subscription = {
                "type": "subscribe",
                "keywords": keywords or [],
                "categories": categories or [],
                "real_time": True
            }
            
            await self.websocket.send(json.dumps(subscription))
            logger.info("Subscribed to OpenClaw real-time stream")
            
            # Listen for incoming news
            while self.is_connected:
                try:
                    message = await asyncio.wait_for(
                        self.websocket.recv(),
                        timeout=300.0  # 5 min timeout
                    )
                    news_item = json.loads(message)
                    
                    # Call all registered callbacks
                    for cb in self.callbacks:
                        await cb(news_item)
                        
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error in stream: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Subscription error: {e}")
    
    async def get_news_by_sector(self, sector: str, days: int = 7) -> List[Dict]:
        """Get news for specific sector"""
        filters = {
            "sectors": [sector],
            "date_from": (datetime.now().timestamp() - days * 86400)
        }
        return await self.fetch_news(filters=filters, limit=50)
    
    async def get_breaking_news(self, urgency: str = "high") -> List[Dict]:
        """Get breaking/urgent news only"""
        filters = {
            "urgency_level": urgency,
            "date_from": (datetime.now().timestamp() - 3600)  # Last hour
        }
        return await self.fetch_news(filters=filters, limit=20)
    
    async def disconnect(self) -> None:
        """Close WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            logger.info("Disconnected from OpenClaw")
    
    def get_buffered_news(self) -> List[Dict]:
        """Get cached news from last fetch"""
        return self.news_buffer.copy()
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
