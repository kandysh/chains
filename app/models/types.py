from enum import Enum
from typing import List

from pydantic import BaseModel, Field, model_validator


class Trend(str, Enum):
    rising = "rising"
    falling = "falling"
    stable = "stable"
    slowing = "slowing"


class Asset(BaseModel):
    id: str
    name: str | None = None
    weight: float = Field(..., ge=0, le=1)


class Portfolio(BaseModel):
    assets: List[Asset]

    @model_validator(mode="after")
    def check_weights(self):
        total = sum(a.weight for a in self.assets)
        if abs(total - 1.0) > 1e-6:
            raise ValueError("Portfolio weights must sum to 1")
        return self


class AssetContribution(BaseModel):
    id: str
    return_: float
    contribution: float


class Performance(BaseModel):
    period: str
    portfolio_return: float
    volatility: float
    max_drawdown: float
    asset_contributions: List[AssetContribution]


class MacroMetric(BaseModel):
    value: float
    trend: Trend


class MacroState(BaseModel):
    inflation: MacroMetric
    policy_rate: MacroMetric
    growth: MacroMetric
    yield_curve: str  # "normal" | "inverted"
    liquidity: str  # "loose" | "neutral" | "tight"


class AnalysisInput(BaseModel):
    portfolio: Portfolio
    performance: Performance
    macro: MacroState
