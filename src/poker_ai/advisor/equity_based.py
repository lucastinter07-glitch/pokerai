from poker_ai.advisor.base import Advisor
from poker_ai.core.game_state import GameState, Street
from poker_ai.engine.equity import EquityCalculator
from poker_ai.advisor.rule_based import RuleBasedAdvisor


class EquityBasedAdvisor(Advisor):
    """
    Phase 2 advisor:
    - Preflop: delegates to the rule-based opening chart (unchanged).
    - Postflop: compares our equity to the pot odds we're being offered.
    
    Core decision framework — the most important equation in poker math:
        If equity > pot_odds_required, the call is +EV.
    """
    
    # Thresholds for postflop action. These are simple heuristics — 
    # Phase 3 will replace them with range-based logic.
    RAISE_MARGIN = 0.10      # Need 10% more equity than pot odds to raise
    VALUE_BET_THRESHOLD = 0.65  # Bet for value when we're this strong
    
    def __init__(self, iterations: int = 2000):
        self._equity = EquityCalculator()
        self._preflop = RuleBasedAdvisor()
        self._iterations = iterations
    
    def recommend(self, state: GameState) -> dict:
        """Route to preflop or postflop logic based on street."""
        if state.street == Street.PREFLOP:
            return self._recommend_preflop(state)
        return self._recommend_postflop(state)
    
    def _recommend_preflop(self, state: GameState) -> dict:
        """Preflop: use the rule-based chart."""
        return self._preflop.recommend(state)
    
    def _recommend_postflop(self, state: GameState) -> dict:
        """Postflop: equity vs. pot odds decision framework."""
        equity = self._equity.equity_vs_random(
            state.hole_cards,
            state.board,
            iterations=self._iterations,
        )
        pot_odds = state.pot_odds
        
        # Case 1: No bet to call — we can check or bet
        if state.to_call == 0:
            if equity > self.VALUE_BET_THRESHOLD:
                return {
                    "action": "bet",
                    "reasoning": f"Strong equity ({equity:.1%}) — bet for value.",
                    "equity": equity,
                    "pot_odds": pot_odds,
                }
            return {
                "action": "check",
                "reasoning": f"Moderate equity ({equity:.1%}) — check and see the next card.",
                "equity": equity,
                "pot_odds": pot_odds,
            }
        
        # Case 2: Facing a bet — compare equity to pot odds
        if equity > pot_odds + self.RAISE_MARGIN:
            return {
                "action": "raise",
                "reasoning": (
                    f"Equity {equity:.1%} significantly exceeds pot odds "
                    f"{pot_odds:.1%} — raise for value."
                ),
                "equity": equity,
                "pot_odds": pot_odds,
            }
        
        if equity > pot_odds:
            return {
                "action": "call",
                "reasoning": (
                    f"Equity {equity:.1%} > pot odds {pot_odds:.1%} "
                    f"— profitable call."
                ),
                "equity": equity,
                "pot_odds": pot_odds,
            }
        
        return {
            "action": "fold",
            "reasoning": (
                f"Equity {equity:.1%} < pot odds {pot_odds:.1%} "
                f"— unprofitable to continue."
            ),
            "equity": equity,
            "pot_odds": pot_odds,
        }