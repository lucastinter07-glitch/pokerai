"""
FastAPI backend for the Poker AI Advisor.

Exposes a single POST /recommend endpoint that accepts game state
and returns a recommendation from the RangeBasedAdvisor.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from poker_ai.core.game_state import GameState, Position
from poker_ai.advisor.range_based import RangeBasedAdvisor

app = FastAPI(title="Poker AI Advisor", version="1.0.0")

# Allow React dev server to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request / Response models ──────────────────────────────────────────────────

class RecommendRequest(BaseModel):
    hole_cards: list[str]           # ["Ah", "Ks"]
    position: str                   # "BTN"
    stack: float = 100.0
    board: list[str] = []           # [] for preflop
    pot: float = 1.5
    to_call: float = 0.0
    effective_stack: float = 100.0
    villain_position: Optional[str] = None   # "UTG" or null
    iterations: int = 2000


class RecommendResponse(BaseModel):
    action: str                     # "fold" | "check" | "call" | "bet" | "raise"
    reasoning: str
    equity: Optional[float]
    pot_odds: float
    bet_size: Optional[float]
    bet_tier: Optional[str]
    sizing_reasoning: Optional[str]


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    """Simple health check."""
    return {"status": "ok"}


@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    """
    Run the range-based advisor and return a recommendation.
    Called by the React frontend on every 'Get Recommendation' tap.
    """
    villain_pos = Position(req.villain_position) if req.villain_position else None

    state = GameState(
        hole_cards=req.hole_cards,
        position=Position(req.position),
        stack=req.stack,
        board=req.board,
        pot=req.pot,
        to_call=req.to_call,
        effective_stack=req.effective_stack,
        villain_position=villain_pos,
    )

    advisor = RangeBasedAdvisor(iterations=req.iterations)
    result  = advisor.recommend(state)

    return RecommendResponse(
        action          = result["action"],
        reasoning       = result["reasoning"],
        equity          = result.get("equity"),
        pot_odds        = result["pot_odds"],
        bet_size        = result.get("bet_size"),
        bet_tier        = result.get("bet_tier"),
        sizing_reasoning= result.get("sizing_reasoning"),
    )