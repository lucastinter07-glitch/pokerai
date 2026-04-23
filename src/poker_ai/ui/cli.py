from poker_ai.core.game_state import GameState, Position
from poker_ai.advisor.equity_based import EquityBasedAdvisor


VALID_RANKS = set("23456789TJQKA")
VALID_SUITS = set("hdcs")


def parse_cards(raw: str) -> list[str]:
    """
    Accept 'Ah Ks' or 'AhKs' — return ['Ah', 'Ks'].
    Blank input returns [].
    Raises ValueError with a helpful message for bad input.
    """
    raw = raw.strip().replace(" ", "")
    if not raw:
        return []
    
    if len(raw) % 2 != 0:
        raise ValueError(
            f"Card input must be even length (2 chars per card). Got '{raw}'."
        )
    
    cards = [raw[i:i+2] for i in range(0, len(raw), 2)]
    for c in cards:
        rank, suit = c[0], c[1]
        if rank not in VALID_RANKS:
            raise ValueError(
                f"Invalid rank '{rank}' in card '{c}'. "
                f"Valid ranks: 2-9, T, J, Q, K, A."
            )
        if suit not in VALID_SUITS:
            raise ValueError(
                f"Invalid suit '{suit}' in card '{c}'. "
                f"Valid suits: h (hearts), d (diamonds), c (clubs), s (spades)."
            )
    return cards


def prompt_float(label: str, default: float) -> float:
    """Ask for a float; use default if the user just hits Enter."""
    raw = input(f"{label} [default {default}]: ").strip()
    return float(raw) if raw else default


def main():
    print("=== Poker AI — Phase 2: Equity-Based Advisor ===\n")
    print("All amounts in big blinds (BB). Press Enter to accept defaults.")
    print("For preflop, leave the board cards prompt empty (just press Enter).\n")
    
    try:
        # Hand + position
        hole = parse_cards(input("Your hole cards (e.g., 'Ah Ks'): "))
        if len(hole) != 2:
            raise ValueError(f"Need exactly 2 hole cards, got {len(hole)}.")
        
        pos_str = input("Position (UTG, MP, CO, BTN, SB, BB): ").strip().upper()
        position = Position(pos_str)
        
        # Board — blank for preflop
        board_raw = input("Board cards (e.g., 'Qh 7d 2c', or press Enter for preflop): ")
        board = parse_cards(board_raw)
        if len(board) not in (0, 3, 4, 5):
            raise ValueError(
                f"Board must be 0 (preflop), 3 (flop), 4 (turn), or 5 (river) cards. "
                f"Got {len(board)}."
            )
        
        # Pot context
        pot = prompt_float("Pot size", 1.5)
        to_call = prompt_float("Amount to call", 0.0)
        stack = prompt_float("Your stack", 100.0)
        
        state = GameState(
            hole_cards=hole,
            position=position,
            stack=stack,
            board=board,
            pot=pot,
            to_call=to_call,
        )
        
        advisor = EquityBasedAdvisor(iterations=2000)
        result = advisor.recommend(state)
        
        print("\n" + "=" * 50)
        print("RECOMMENDATION")
        print("=" * 50)
        print(f"Action:       {result['action'].upper()}")
        print(f"Reasoning:    {result['reasoning']}")
        if result["equity"] is not None:
            print(f"Your equity:  {result['equity']:.1%}")
        if state.to_call > 0:
            print(f"Pot odds:     {result['pot_odds']:.1%}")
        print("=" * 50)
    
    except ValueError as e:
        print(f"\n[Input error] {e}")
        print("Please restart and try again.")


if __name__ == "__main__":
    main()