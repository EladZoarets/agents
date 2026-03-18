"""ETF Sector Mappings and Related Utilities"""
from typing import Dict, List, Set
from dataclasses import dataclass
from enum import Enum

class Sector(Enum):
    """ETF Sector Categories"""
    ENERGY = "energy"
    CONSUMER_DISCRETIONARY = "consumer_discretionary"
    CONSUMER_STAPLES = "consumer_staples"
    TECHNOLOGY = "technology"
    FINANCIALS = "financials"
    HEALTHCARE = "healthcare"
    INDUSTRIALS = "industrials"
    UTILITIES = "utilities"
    MATERIALS = "materials"
    REAL_ESTATE = "real_estate"
    COMMODITIES = "commodities"
    BONDS = "bonds"
    MIXED = "mixed"


@dataclass
class ETFInfo:
    """Information about an ETF"""
    symbol: str
    name: str
    sector: Sector
    description: str
    typical_holdings: List[str]


# ETF Database with sector mappings
ETF_DATABASE: Dict[str, ETFInfo] = {
    # ENERGY
    "XLE": ETFInfo(
        symbol="XLE",
        name="Energy Select Sector SPDR",
        sector=Sector.ENERGY,
        description="Oil, gas, energy companies",
        typical_holdings=["XOM", "CVX", "COP", "MPC", "EOG"]
    ),
    "VDE": ETFInfo(
        symbol="VDE",
        name="Vanguard Energy ETF",
        sector=Sector.ENERGY,
        description="US energy sector exposure",
        typical_holdings=["XOM", "CVX", "COP"]
    ),
    
    # CONSUMER DISCRETIONARY
    "XLY": ETFInfo(
        symbol="XLY",
        name="Consumer Discretionary Select Sector SPDR",
        sector=Sector.CONSUMER_DISCRETIONARY,
        description="Retail, automotive, entertainment",
        typical_holdings=["AMZN", "TSLA", "HOME", "NWL", "RH"]
    ),
    "VDC": ETFInfo(
        symbol="VDC",
        name="Vanguard Consumer Discretionary ETF",
        sector=Sector.CONSUMER_DISCRETIONARY,
        description="Discretionary consumer spending",
        typical_holdings=["AMZN", "TSLA", "HD"]
    ),
    
    # CONSUMER STAPLES
    "XLP": ETFInfo(
        symbol="XLP",
        name="Consumer Staples Select Sector SPDR",
        sector=Sector.CONSUMER_STAPLES,
        description="Food, beverages, household products (defensive)",
        typical_holdings=["PG", "KO", "WMT", "JNJ", "MO"]
    ),
    
    # TECHNOLOGY
    "XLK": ETFInfo(
        symbol="XLK",
        name="Technology Select Sector SPDR",
        sector=Sector.TECHNOLOGY,
        description="Software, semiconductors, IT services",
        typical_holdings=["MSFT", "AAPL", "NVDA", "AVGO", "CSCO"]
    ),
    "VGT": ETFInfo(
        symbol="VGT",
        name="Vanguard Information Technology ETF",
        sector=Sector.TECHNOLOGY,
        description="US technology sector",
        typical_holdings=["MSFT", "AAPL", "NVDA"]
    ),
    "QQQ": ETFInfo(
        symbol="QQQ",
        name="Invesco QQQ Trust",
        sector=Sector.TECHNOLOGY,
        description="Nasdaq-100 (heavily tech-weighted)",
        typical_holdings=["AAPL", "MSFT", "NVDA", "AMZN", "TSLA"]
    ),
    
    # FINANCIALS
    "XLF": ETFInfo(
        symbol="XLF",
        name="Financial Select Sector SPDR",
        sector=Sector.FINANCIALS,
        description="Banks, insurance, real estate services",
        typical_holdings=["BRK", "JPM", "BAC", "WFC", "GS"]
    ),
    "VFV": ETFInfo(
        symbol="VFV",
        name="Vanguard Financials ETF",
        sector=Sector.FINANCIALS,
        description="US financial sector",
        typical_holdings=["JPM", "BAC", "GS"]
    ),
    
    # HEALTHCARE
    "XLV": ETFInfo(
        symbol="XLV",
        name="Health Care Select Sector SPDR",
        sector=Sector.HEALTHCARE,
        description="Pharmaceuticals, biotech, medical devices",
        typical_holdings=["JNJ", "UNH", "LLY", "MRK", "ABBV"]
    ),
    
    # INDUSTRIALS
    "XLI": ETFInfo(
        symbol="XLI",
        name="Industrial Select Sector SPDR",
        sector=Sector.INDUSTRIALS,
        description="Aerospace, defense, manufacturing, transport",
        typical_holdings=["BA", "CAT", "GD", "LMT", "RTX"]
    ),
    
    # UTILITIES
    "XLU": ETFInfo(
        symbol="XLU",
        name="Utilities Select Sector SPDR",
        sector=Sector.UTILITIES,
        description="Electric, gas, water utilities (defensive)",
        typical_holdings=["NEE", "DUK", "SO", "D", "EXC"]
    ),
    
    # MATERIALS
    "XLB": ETFInfo(
        symbol="XLB",
        name="Materials Select Sector SPDR",
        sector=Sector.MATERIALS,
        description="Chemicals, metals, mining, forestry",
        typical_holdings=["LIN", "APD", "ECL", "SHW", "NEM"]
    ),
    
    # REAL ESTATE
    "XLRE": ETFInfo(
        symbol="XLRE",
        name="Real Estate Select Sector SPDR",
        sector=Sector.REAL_ESTATE,
        description="REITs and real estate services",
        typical_holdings=["PLD", "EQIX", "DLR", "SPG", "WELL"]
    ),
    "VNQ": ETFInfo(
        symbol="VNQ",
        name="Vanguard Real Estate ETF",
        sector=Sector.REAL_ESTATE,
        description="US real estate/REIT exposure",
        typical_holdings=["PLD", "EQIX", "DLR"]
    ),
    
    # BROAD/DIVERSIFIED
    "SPY": ETFInfo(
        symbol="SPY",
        name="S&P 500 SPDR",
        sector=Sector.MIXED,
        description="Broad US market (all sectors)",
        typical_holdings=["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN"]
    ),
    "IVV": ETFInfo(
        symbol="IVV",
        name="iShares Core S&P 500 ETF",
        sector=Sector.MIXED,
        description="S&P 500 index",
        typical_holdings=["AAPL", "MSFT", "NVDA"]
    ),
    
    # BONDS
    "TLT": ETFInfo(
        symbol="TLT",
        name="20+ Year Treasury Bond ETF",
        sector=Sector.BONDS,
        description="Long-term US government bonds",
        typical_holdings=[]
    ),
    "BND": ETFInfo(
        symbol="BND",
        name="Vanguard Total Bond Market ETF",
        sector=Sector.BONDS,
        description="Total US bond market",
        typical_holdings=[]
    ),
    
    # COMMODITIES
    "DBC": ETFInfo(
        symbol="DBC",
        name="Commodities ETF",
        sector=Sector.COMMODITIES,
        description="Broad commodity exposure (oil, metals, agriculture)",
        typical_holdings=[]
    ),
    "GLD": ETFInfo(
        symbol="GLD",
        name="SPDR Gold Shares",
        sector=Sector.COMMODITIES,
        description="Gold bullion tracking",
        typical_holdings=[]
    ),
}


# Event Impact Scenarios - How different events affect sectors
EVENT_IMPACT_MATRIX = {
    "war_geopolitical": {
        Sector.ENERGY: 0.85,  # Oil spikes
        Sector.INDUSTRIALS: 0.70,  # Defense spending
        Sector.CONSUMER_DISCRETIONARY: -0.60,  # Consumer fear
        Sector.REAL_ESTATE: -0.50,  # Flight to safety
        Sector.FINANCIALS: -0.65,  # Credit risk
        Sector.TECHNOLOGY: 0.50,  # Safe haven
        Sector.UTILITIES: -0.30,
        Sector.HEALTHCARE: 0.20,
    },
    "crisis_recession": {
        Sector.CONSUMER_DISCRETIONARY: -0.85,  # Weak demand
        Sector.FINANCIALS: -0.80,  # Defaults rise
        Sector.INDUSTRIALS: -0.75,
        Sector.ENERGY: -0.60,
        Sector.CONSUMER_STAPLES: 0.40,  # Defensive
        Sector.HEALTHCARE: 0.35,  # Essential
        Sector.UTILITIES: 0.45,  # Defensive
        Sector.TECHNOLOGY: -0.50,  # Growth concerns
    },
    "rate_cut": {
        Sector.TECHNOLOGY: 0.75,  # Growth stocks boost
        Sector.CONSUMER_DISCRETIONARY: 0.65,  # Spending ↑
        Sector.REAL_ESTATE: 0.70,  # Borrowing cheaper
        Sector.UTILITIES: -0.50,  # Bonds attractive
        Sector.FINANCIALS: -0.60,  # Margin compression
        Sector.ENERGY: -0.20,
        Sector.INDUSTRIALS: 0.50,
    },
    "rate_hike": {
        Sector.FINANCIALS: 0.65,  # Margins expand
        Sector.UTILITIES: 0.70,
        Sector.ENERGY: 0.20,
        Sector.TECHNOLOGY: -0.70,  # Growth stocks hurt
        Sector.CONSUMER_DISCRETIONARY: -0.60,  # Higher borrowing costs
        Sector.REAL_ESTATE: -0.65,
        Sector.INDUSTRIALS: -0.40,
    },
    "tariffs": {
        Sector.INDUSTRIALS: 0.50,  # Domestic mfg benefit
        Sector.CONSUMER_DISCRETIONARY: -0.65,  # Price increases
        Sector.TECHNOLOGY: -0.50,  # Supply chain
        Sector.MATERIALS: -0.40,
        Sector.ENERGY: 0.20,
    },
    "green_subsidy": {
        Sector.ENERGY: -0.30,  # Traditional energy pressure
        Sector.UTILITIES: 0.40,  # Green infrastructure
        Sector.INDUSTRIALS: 0.50,  # Clean tech manufacturing
        Sector.MATERIALS: 0.30,
        Sector.TECHNOLOGY: 0.60,  # Solar, battery tech
    },
}


def get_etf_info(symbol: str) -> ETFInfo:
    """Get detailed information about an ETF"""
    return ETF_DATABASE.get(symbol.upper())


def get_etfs_by_sector(sector: Sector) -> List[str]:
    """Get all ETF symbols for a given sector"""
    return [
        symbol for symbol, info in ETF_DATABASE.items()
        if info.sector == sector
    ]


def get_sector_impact(event_type: str, sector: Sector) -> float:
    """
    Get expected impact of an event on a sector
    
    Returns: Float from -1.0 to +1.0
    -1.0: Very negative impact
    0.0: Neutral
    +1.0: Very positive impact
    """
    impacts = EVENT_IMPACT_MATRIX.get(event_type, {})
    return impacts.get(sector, 0.0)


def get_correlated_etfs(primary_etf: str, correlation_threshold: float = 0.5) -> List[str]:
    """
    Get ETFs that move together with the primary ETF
    (Used for portfolio diversification checks)
    """
    primary_info = get_etf_info(primary_etf)
    if not primary_info:
        return []
    
    # Return other ETFs in the same sector
    correlated = get_etfs_by_sector(primary_info.sector)
    correlated.remove(primary_etf) if primary_etf in correlated else None
    return correlated


def is_defensive_sector(sector: Sector) -> bool:
    """Check if a sector is considered defensive (less volatile)"""
    defensive = [Sector.CONSUMER_STAPLES, Sector.UTILITIES, Sector.HEALTHCARE]
    return sector in defensive


def is_growth_sector(sector: Sector) -> bool:
    """Check if a sector is considered growth-oriented"""
    growth = [Sector.TECHNOLOGY, Sector.CONSUMER_DISCRETIONARY, Sector.INDUSTRIALS]
    return sector in growth
