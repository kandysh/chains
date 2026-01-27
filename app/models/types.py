from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator

# ---------- Enums ----------


class Trend(str, Enum):
    rising = "rising"
    falling = "falling"
    stable = "stable"
    slowing = "slowing"


class YieldCurve(str, Enum):
    normal = "normal"
    inverted = "inverted"
    flat = "flat"


class Liquidity(str, Enum):
    loose = "loose"
    neutral = "neutral"
    tight = "tight"


# ---------- Portfolio ----------


class Asset(BaseModel):
    id: str
    name: Optional[str] = None
    weight: float = Field(..., ge=0, le=1)


class Portfolio(BaseModel):
    assets: List[Asset]

    @model_validator(mode="after")
    def check_weights(self):
        total = sum(a.weight for a in self.assets)
        if round(total, 6) != 1.0:
            raise ValueError("Portfolio weights must sum to 1")
        return self


# ---------- Performance ----------


class AssetContribution(BaseModel):
    id: str
    return_: float = Field(..., alias="return")
    contribution: float

    model_config = {"populate_by_name": True}


class Performance(BaseModel):
    period: str
    portfolio_return: float
    volatility: float
    max_drawdown: float
    asset_contributions: List[AssetContribution]


# ---------- Macro ----------


class MacroMetric(BaseModel):
    value: float
    trend: Trend


class MacroState(BaseModel):
    inflation: MacroMetric
    policy_rate: MacroMetric
    growth: MacroMetric
    yield_curve: YieldCurve
    liquidity: Liquidity


# ---------- Final Input ----------


class AnalysisInput(BaseModel):
    portfolio: Portfolio
    performance: Performance
    macro: Optional[MacroState] = None
