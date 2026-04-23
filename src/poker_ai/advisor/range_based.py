"""
Range-based advisor (Phase 4).

Improves on EquityBasedAdvisor by modeling opponent as a weighted range
of realistic hands rather than a uniformly-random hand. This produces
much more accurate equity estimates and better decisions.
"""

from typing import Optional
from poker_ai.advisor.base import Advisor
from poker_ai.advisor.rule_based import RuleBasedAdvisor
from poker_ai.advisor.ranges import opening_range, calling_range
from poker_ai.core.game_state import GameState, Street, Position
from poker_ai.core.hand_range import Range
from poker_ai.engine.equity import EquityCalculator


class RangeBasedAdvisor(Advisor):
    """
    Phase 4 advisor: uses realistic opponent ranges for equity estimation.
    
    Decision framework is unchanged from Phase 2:
        equity > pot_odds + margin -> raise
        equity > pot_odds          -> call
        equity <= pot_odds         -> fold
    
    The upgrade is entirely in the equity input: we now model villain as
    holding a realistic range of hands for their position and action,
    rather than any two random cards.
    """
    
    RAISE_MARGIN = 0.15
    VALUE_BET_THRESHOLD = 0.60  # Slightly lower than Phase 2 since range equity is more meaningful
    
    def __init__(self, iterations: int = 2000):
        self._equity = EquityCalculator()
        self._preflop = RuleBasedAdvisor()
        self._iterations = iterations
    
    def recommend(self, state: GameState) -> dict:
        if state.street == Street.PREFLOP:
            return self._recommend_preflop(state)
        return self._recommend_postflop(state)
    
    def _recommend_preflop(self, state: GameState) -> dict:
        # Preflop still uses the rule-based chart.
        # Phase 5 can upgrade this with range-based preflop decisions.
        return self._preflop.recommend(state)
    
    def _recommend_postflop(self, state: GameState) -> dict:
        """Postflop decision using range-based equity."""
        
        # Step 1: Construct villain's likely range
        villain_range = self._construct_villain_range(state)
        
        if villain_range.is_empty():
            # Fallback: villain's assumed range has no valid combos given blocked cards
            # This is rare but can happen; fall back to random-hand equity
            return self._fallback_random_equity(state)
        
        # Step 2: Compute equity vs. that range
        try:
            equity = self._equity.equity_vs_range(
                state.hole_cards,
                state.board,
                villain_range,
                iterations=self._iterations,
            )
        except ValueError:
            return self._fallback_random_equity(state)
        
        pot_odds = state.pot_odds
        
        # Step 3: Apply the same decision framework as Phase 2
        return self._decide(equity, pot_odds, state, villain_range)
    
    def _construct_villain_range(self, state: GameState) -> Range:
        """
        Build villain's range based on their position and the betting context.
        
        Simplified model for Phase 4:
        - If villain_position is set, use their opening range (they were the raiser).
        - Otherwise, assume a generic "continuation range" — roughly the top 25% of hands.
        """
        # Determine villain's base range
        if state.villain_position is not None:
            pos_key = state.villain_position.value
            try:
                base_range = opening_range(pos_key)
            except ValueError:
                # Unknown position — use a wide default
                base_range = opening_range("CO")
        else:
            # No villain position specified — assume a moderately tight range (CO-ish)
            base_range = opening_range("CO")
        
        # Remove combos that conflict with known cards
        blocked = list(state.hole_cards) + list(state.board)
        return base_range.remove_blocked(blocked)
    
    def _decide(self, equity: float, pot_odds: float, state: GameState, villain_range: Range) -> dict:
        """Apply the decision framework given computed equity."""
        
        range_size = villain_range.num_combos()
        range_note = f" (modeling villain on {range_size} combos)"
        
        # No bet to call — choose bet or check
        if state.to_call == 0:
            if equity > self.VALUE_BET_THRESHOLD:
                return {
                    "action": "bet",
                    "reasoning": f"Strong equity ({equity:.1%}) vs. villain's range{range_note} — bet for value.",
                    "equity": equity,
                    "pot_odds": pot_odds,
                }
            return {
                "action": "check",
                "reasoning": f"Moderate equity ({equity:.1%}) vs. villain's range{range_note} — check.",
                "equity": equity,
                "pot_odds": pot_odds,
            }
        
        # Facing a bet
        if equity > pot_odds + self.RAISE_MARGIN:
            return {
                "action": "raise",
                "reasoning": (
                    f"Equity {equity:.1%} significantly exceeds pot odds {pot_odds:.1%}"
                    f"{range_note} — raise for value."
                ),
                "equity": equity,
                "pot_odds": pot_odds,
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
            }
        
        return {
            "action": "fold",
            "reasoning": (
                f"Equity {equity:.1%} < pot odds {pot_odds:.1%}"
                f"{range_note} — unprofitable to continue."
            ),
            "equity": equity,
            "pot_odds": pot_odds,
        }
    
    def _fallback_random_equity(self, state: GameState) -> dict:
        """Fallback when range construction fails — use random-hand equity."""
        equity = self._equity.equity_vs_random(
            state.hole_cards, state.board, iterations=self._iterations
        )
        # Empty range as a placeholder
        return self._decide(equity, state.pot_odds, state, Range())