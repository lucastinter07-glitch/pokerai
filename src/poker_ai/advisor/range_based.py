"""
Range-based advisor (Phase 4/5).

Improves on EquityBasedAdvisor by modeling opponent as a weighted range
of realistic hands rather than a uniformly-random hand. Phase 5 adds
bet sizing recommendations to every action.
"""

from typing import Optional
from poker_ai.advisor.base import Advisor
from poker_ai.advisor.rule_based import RuleBasedAdvisor
from poker_ai.advisor.ranges import opening_range
from poker_ai.advisor.sizing import (
    BetSizing,
    preflop_open_sizing,
    preflop_three_bet_sizing,
    postflop_bet_sizing,
    postflop_raise_sizing,
    is_in_position,
)
from poker_ai.core.game_state import GameState, Street, Position
from poker_ai.core.hand_range import Range
from poker_ai.engine.equity import EquityCalculator


class RangeBasedAdvisor(Advisor):
    """
    Phase 4/5 advisor: range-based equity + bet sizing recommendations.
    
    Decision framework (unchanged from Phase 4):
        equity > pot_odds + margin -> raise
        equity > pot_odds          -> call
        equity <= pot_odds         -> fold
    
    Phase 5 addition: every BET or RAISE recommendation now includes
    a specific BB amount and reasoning via the sizing module.
    """
    
    RAISE_MARGIN = 0.15
    VALUE_BET_THRESHOLD = 0.60
    
    def __init__(self, iterations: int = 2000):
        self._equity_calc = EquityCalculator()
        self._preflop = RuleBasedAdvisor()
        self._iterations = iterations
    
    def recommend(self, state: GameState) -> dict:
        if state.street == Street.PREFLOP:
            return self._recommend_preflop(state)
        return self._recommend_postflop(state)
    
    # ----------------------------------------------------------------
    # Preflop
    # ----------------------------------------------------------------
    
    def _recommend_preflop(self, state: GameState) -> dict:
        """Preflop: rule-based action + sizing for raises."""
        base = self._preflop.recommend(state)
        action = base["action"]
        
        if action == "raise":
            sizing = self._preflop_sizing(state)
            return {**base, **self._sizing_fields(sizing)}
        
        # Fold — no sizing needed
        return {**base, "bet_size": None, "bet_tier": None, "sizing_reasoning": None}
    
    def _preflop_sizing(self, state: GameState) -> BetSizing:
        """Compute preflop sizing based on context."""
        pos_key = state.position.value
        
        # Facing a raise — we're 3-betting
        if state.to_call > 0:
            villain_pos = state.villain_position.value if state.villain_position else "UTG"
            return preflop_three_bet_sizing(
                open_size=state.to_call,
                hero_pos=pos_key,
                villain_pos=villain_pos,
                effective_stack=state.effective_stack,
            )
        
        # No prior raise — standard open
        return preflop_open_sizing(pos_key, state.effective_stack)
    
    # ----------------------------------------------------------------
    # Postflop
    # ----------------------------------------------------------------
    
    def _recommend_postflop(self, state: GameState) -> dict:
        """Postflop: range-based equity + action + sizing."""
        
        villain_range = self._construct_villain_range(state)
        
        if villain_range.is_empty():
            return self._fallback_random_equity(state)
        
        try:
            equity = self._equity_calc.equity_vs_range(
                state.hole_cards,
                state.board,
                villain_range,
                iterations=self._iterations,
            )
        except ValueError:
            return self._fallback_random_equity(state)
        
        return self._decide(equity, state, villain_range)
    
    def _construct_villain_range(self, state: GameState) -> Range:
        """Build villain's range from their position."""
        pos_key = (
            state.villain_position.value
            if state.villain_position
            else "CO"
        )
        try:
            base_range = opening_range(pos_key)
        except ValueError:
            base_range = opening_range("CO")
        
        blocked = list(state.hole_cards) + list(state.board)
        return base_range.remove_blocked(blocked)
    
    def _decide(self, equity: float, state: GameState, villain_range: Range) -> dict:
        """Apply decision framework and attach sizing."""
        pot_odds = state.pot_odds
        range_size = villain_range.num_combos()
        range_note = f" (modeling villain on {range_size} combos)"
        
        # No bet to call — check or bet
        if state.to_call == 0:
            if equity > self.VALUE_BET_THRESHOLD:
                sizing = postflop_bet_sizing(
                    equity, state.pot, state.stack, state.board
                )
                return {
                    "action": "bet",
                    "reasoning": f"Strong equity ({equity:.1%}) vs. villain's range{range_note} — bet for value.",
                    "equity": equity,
                    "pot_odds": pot_odds,
                    **self._sizing_fields(sizing),
                }
            return {
                "action": "check",
                "reasoning": f"Moderate equity ({equity:.1%}) vs. villain's range{range_note} — check.",
                "equity": equity,
                "pot_odds": pot_odds,
                "bet_size": None,
                "bet_tier": None,
                "sizing_reasoning": None,
            }
        
        # Facing a bet — raise, call, or fold
        if equity > pot_odds + self.RAISE_MARGIN:
            sizing = postflop_raise_sizing(
                equity, state.to_call, state.pot, state.stack, state.board
            )
            return {
                "action": "raise",
                "reasoning": (
                    f"Equity {equity:.1%} significantly exceeds pot odds {pot_odds:.1%}"
                    f"{range_note} — raise for value."
                ),
                "equity": equity,
                "pot_odds": pot_odds,
                **self._sizing_fields(sizing),
            }
        
        if equity > pot_odds:
            return {
                "action": "call",
                "reasoning": (
                    f"Equity {equity:.1%} > pot odds {pot_odds:.1%}"
                    f"{range_note} — profitable call."
                ),
                "equity": equity,
                "pot_odds": pot_odds,
                "bet_size": None,
                "bet_tier": None,
                "sizing_reasoning": None,
            }
        
        return {
            "action": "fold",
            "reasoning": (
                f"Equity {equity:.1%} < pot odds {pot_odds:.1%}"
                f"{range_note} — unprofitable to continue."
            ),
            "equity": equity,
            "pot_odds": pot_odds,
            "bet_size": None,
            "bet_tier": None,
            "sizing_reasoning": None,
        }
    
    def _sizing_fields(self, sizing: BetSizing) -> dict:
        """Convert a BetSizing into the three dict fields."""
        return {
            "bet_size": sizing.amount,
            "bet_tier": sizing.tier.value,
            "sizing_reasoning": sizing.reasoning,
        }
    
    def _fallback_random_equity(self, state: GameState) -> dict:
        """Fallback when range construction fails."""
        equity = self._equity_calc.equity_vs_random(
            state.hole_cards, state.board, iterations=self._iterations
        )
        return self._decide(equity, state, Range())