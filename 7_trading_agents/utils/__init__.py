"""Trading Agents Utilities Package

NOTE: Import directly from specific modules:
  from utils.openclaw_client import OpenClawClient
  from utils.etf_mappings import EVENT_IMPACT_MATRIX, get_etf_info
  
Do NOT use circular imports from this __init__.py
"""

import sys
import os

# Ensure we can find config and other modules
_current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    if name == "OpenClawClient":
        from utils.openclaw_client import OpenClawClient
        return OpenClawClient
    elif name == "ETF_DATABASE":
        from utils.etf_mappings import ETF_DATABASE
        return ETF_DATABASE
    elif name == "EVENT_IMPACT_MATRIX":
        from utils.etf_mappings import EVENT_IMPACT_MATRIX
        return EVENT_IMPACT_MATRIX
    elif name == "Sector":
        from utils.etf_mappings import Sector
        return Sector
    elif name == "get_etf_info":
        from utils.etf_mappings import get_etf_info
        return get_etf_info
    elif name == "get_etfs_by_sector":
        from utils.etf_mappings import get_etfs_by_sector
        return get_etfs_by_sector
    elif name == "get_sector_impact":
        from utils.etf_mappings import get_sector_impact
        return get_sector_impact
    elif name == "get_correlated_etfs":
        from utils.etf_mappings import get_correlated_etfs
        return get_correlated_etfs
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "OpenClawClient",
    "ETF_DATABASE",
    "EVENT_IMPACT_MATRIX",
    "Sector",
    "get_etf_info",
    "get_etfs_by_sector",
    "get_sector_impact",
    "get_correlated_etfs"
]
