"""Trading Decision & Executor Agents using OpenAI SDK"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from agents import Agent, Runner, function_tool
from dataclasses import dataclass
import json
from config.config import (
    MIN_CONFIDENCE_THRESHOLD, OPTION_EXPIRY_DAYS_SHORT,
    CALL_STRIKE_OFFSET, PUT_STRIKE_OFFSET
)

logger = logging.getLogger(__name__)


@dataclass
class TradeDecision:
    """Represents a single trade decision"""
    etf_symbol: str
    trade_type: str  # CALL or PUT
    strike_price: float
    expiry_date: str
    quantity: int
    reasoning: str
    confidence: float
    expected_move: float  # Expected % move


class TradingDecisionAgent:
    """Agent for making final trading decisions"""
    
    def __init__(self):
        self.agent = Agent(
            name="trading_decision_engine",
            instructions="""You are a trading decision engine. Your job is to:
1. Receive impact analysis and sentiment data
2. Apply risk management rules
3. Make BUY/SELL/HOLD decisions
4. Specify exact strike prices and quantities
5. Track reasoning for each decision

Be conservative. Only trade when confidence > 70%.
Always consider risk/reward ratio and position sizing.
Account for volatility and liquidity.
            """
        )
        self.decisions: List[TradeDecision] = []
    
    @function_tool
    async def calculate_confidence_score(self,
                                        impact_score: float,
                                        sentiment_alignment: float,
                                        historical_accuracy: float = 0.65) -> float:
        """
        Calculate overall confidence in a trade
        
        Confidence = (impact_score × 0.6) + (sentiment_alignment × 0.4)
        """
        confidence = (impact_score * 0.6) + (sentiment_alignment * 0.4)
        
        # Adjust by historical accuracy
        confidence = confidence * historical_accuracy
        
        return round(min(confidence, 1.0), 3)
    
    @function_tool
    async def apply_risk_management(self,
                                   base_confidence: float,
                                   volatility: float,
                                   account_size: float = 100000) -> Dict:
        """
        Apply risk management rules
        
        Returns: position size in dollars
        """
        if base_confidence < MIN_CONFIDENCE_THRESHOLD:
            return {
                "trade_decision": "SKIP",
                "reason": f"Confidence {base_confidence} below threshold {MIN_CONFIDENCE_THRESHOLD}",
                "position_size": 0
            }
        
        # Risk 2% of account per trade
        base_risk = account_size * 0.02
        
        # Reduce position size if volatility is high
        volatility_adjustment = 1.0 / (1.0 + volatility)
        
        position_size = base_risk * base_confidence * volatility_adjustment
        
        return {
            "trade_decision": "PROCEED",
            "position_size": round(position_size, 2),
            "max_loss": round(position_size * 0.05, 2),  # 5% stop loss
            "target_profit": round(position_size * 0.15, 2),  # 15% target
            "volatility_adjustment": round(volatility_adjustment, 3)
        }
    
    @function_tool
    async def calculate_strike_price(self,
                                    etf_symbol: str,
                                    current_price: float,
                                    trade_type: str,  # CALL or PUT
                                    expected_move_percent: float) -> Dict:
        """
        Calculate optimal strike price based on expected move
        
        For CALL: strike = current × (1 + offset)
        For PUT: strike = current × (1 - offset)
        """
        if trade_type.upper() == "CALL":
            # Strike slightly above current, adjust by expected move
            strike = current_price * (1 + CALL_STRIKE_OFFSET + (expected_move_percent * 0.01))
        elif trade_type.upper() == "PUT":
            # Strike slightly below current
            strike = current_price * (1 + PUT_STRIKE_OFFSET - (abs(expected_move_percent) * 0.01))
        else:
            raise ValueError(f"Invalid trade_type: {trade_type}")
        
        # Round to nearest 0.50 for clean strikes
        strike = round(strike * 2) / 2
        
        return {
            "etf_symbol": etf_symbol,
            "current_price": current_price,
            "strike_price": strike,
            "trade_type": trade_type,
            "strikes_away": round(((strike - current_price) / current_price) * 100, 2)
        }
    
    @function_tool
    async def calculate_expiry_date(self, trade_type: str, event_severity: float) -> str:
        """
        Calculate option expiry date based on event severity
        
        Shorter expiry = higher probability but higher theta
        """
        # Base: 3 weeks (21 days) for short-term trades
        days = OPTION_EXPIRY_DAYS_SHORT
        
        # Adjust by event severity
        if event_severity > 0.8:
            days = int(21 * 0.8)  # Tighten to 17 days for major events
        elif event_severity < 0.4:
            days = int(21 * 1.2)  # Extend to 25 days for subtle moves
        
        expiry = datetime.now() + timedelta(days=days)
        
        # Adjust to next Friday (standard options expiry)
        while expiry.weekday() != 4:  # 4 = Friday
            expiry += timedelta(days=1)
        
        return expiry.strftime("%Y-%m-%d")
    
    async def run(self,
                 impact_analysis: Dict,
                 sentiment_data: Dict,
                 etf_prices: Dict) -> List[TradeDecision]:
        """
        Execute trading decision workflow
        
        Returns: List of TradeDecision objects ready for execution
        """
        logger.info("Starting Trading Decision Agent")
        
        prompt = f"""
Make final trading decisions based on all available analysis.

Impact Analysis:
{impact_analysis}

Sentiment Data:
{sentiment_data}

Current ETF Prices:
{etf_prices}

For each promising opportunity:
1. Calculate confidence score (must be > 0.7 to trade)
2. Determine position size
3. Calculate strike prices
4. Select expiry date
5. Set stop loss and take profit levels
6. Write clear reasoning

Provide JSON output with:
- trades: array of {
    "etf_symbol": "XLE",
    "trade_type": "CALL",
    "strike_price": 100.50,
    "expiry_date": "2026-04-03",
    "quantity": 5,
    "confidence": 0.82,
    "stop_loss_price": 1.00,
    "take_profit_price": 5.00,
    "reasoning": "War event + bullish sentiment = strong signal"
  }
- summary: {
    "total_trades": 3,
    "total_capital_required": 5000,
    "average_confidence": 0.78,
    "biggest_opportunity": "XLE CALL"
  }
        """
        
        result = await Runner.run(
            self.agent,
            prompt
        )
        
        return {
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "trade_decisions": result.final_output
        }


class InteractiveBrokersExecutor:
    """Agent for executing trades via Interactive Brokers API
    
    Note: @function_tool decorators removed to avoid JSON schema validation issues
    """
    
    def __init__(self):
        self.agent = Agent(
            name="ib_executor",
            instructions="""You are an Interactive Brokers trading executor. Your job is to:
1. Receive trade decisions
2. Validate all order parameters
3. Execute orders on IB API
4. Log all trades with timestamps
5. Track position P&L
6. Set alerts and stops

Be extremely careful with risk management.
Never exceed position size limits.
Always confirm orders before execution.
            """
        )
        self.executed_trades: List[Dict] = []
    
    async def validate_trade_order(self, trade: Dict) -> Dict:
        """Validate order parameters before execution"""
        required_fields = ["etf_symbol", "trade_type", "strike_price", "quantity", "expiry_date"]
        
        for field in required_fields:
            if field not in trade or trade[field] is None:
                return {
                    "valid": False,
                    "error": f"Missing required field: {field}"
                }
        
        return {
            "valid": True,
            "trade": trade
        }
    
    async def execute_ib_order(self,
                              etf_symbol: str,
                              trade_type: str,
                              strike_price: float,
                              quantity: int,
                              expiry_date: str) -> Dict:
        """
        Execute order via Interactive Brokers API
        
        This is a simplified mock - in production connect to ibapi
        """
        try:
            # In production: connect to IB TWS/Gateway
            # ibapi calls here
            
            order = {
                "order_id": len(self.executed_trades) + 1,
                "timestamp": datetime.now().isoformat(),
                "etf_symbol": etf_symbol,
                "trade_type": trade_type,
                "strike_price": strike_price,
                "quantity": quantity,
                "expiry_date": expiry_date,
                "status": "EXECUTED",
                "execution_price": strike_price * 1.02,  # Mock: 2% slippage
            }
            
            self.executed_trades.append(order)
            logger.info(f"Executed order: {etf_symbol} {trade_type} x{quantity}")
            
            return order
            
        except Exception as e:
            logger.error(f"Failed to execute order: {e}")
            return {
                "status": "ERROR",
                "message": str(e)
            }
    
    async def set_stop_loss_take_profit(self,
                                       order_id: int,
                                       stop_loss: float,
                                       take_profit: float) -> Dict:
        """Set stop loss and take profit orders"""
        return {
            "order_id": order_id,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "status": "SET"
        }
    
    async def run(self, trade_decisions: List[Dict]) -> Dict:
        """Execute all approved trades"""
        logger.info(f"Starting execution of {len(trade_decisions)} trades")
        
        results = []
        for trade in trade_decisions:
            # Validate
            validation = await self.validate_trade_order(trade)
            if not validation["valid"]:
                logger.warning(f"Skipping invalid trade: {validation['error']}")
                continue
            
            # Execute
            result = await self.execute_ib_order(
                etf_symbol=trade["etf_symbol"],
                trade_type=trade["trade_type"],
                strike_price=trade["strike_price"],
                quantity=trade["quantity"],
                expiry_date=trade["expiry_date"]
            )
            
            if result.get("status") == "EXECUTED":
                # Set stops
                await self.set_stop_loss_take_profit(
                    order_id=result["order_id"],
                    stop_loss=trade.get("stop_loss_price", 0),
                    take_profit=trade.get("take_profit_price", 0)
                )
            
            results.append(result)
        
        return {
            "status": "execution_complete",
            "timestamp": datetime.now().isoformat(),
            "trades_executed": len([r for r in results if r.get("status") == "EXECUTED"]),
            "executed_trades": results
        }
