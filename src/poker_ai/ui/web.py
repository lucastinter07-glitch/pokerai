import streamlit as st
from poker_ai.core.game_state import GameState, Position
from poker_ai.advisor.range_based import RangeBasedAdvisor
from poker_ai.utils.cards import format_card, RANKS, SUITS


# ---------- Page Config ----------

st.set_page_config(
    page_title="Poker AI Advisor",
    page_icon="♠",
    layout="centered",
)


# ---------- Custom CSS ----------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@500;700&family=Inter:wght@400;500&display=swap');

.stApp {
    background:
        radial-gradient(ellipse at top, #134a3a 0%, #0d3b2e 45%, #082720 100%);
    background-attachment: fixed;
}

.main .block-container {
    max-width: 780px;
    padding-top: 2.5rem;
    padding-bottom: 4rem;
}

html, body, [class*="st-"], .stMarkdown, p, label {
    color: #f5ebd0 !important;
    font-family: 'Inter', sans-serif;
}

h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    color: #f5ebd0 !important;
    letter-spacing: 0.01em;
}

h1 {
    font-weight: 700 !important;
    font-size: 2.8rem !important;
    border-bottom: 1px solid rgba(212, 165, 116, 0.35);
    padding-bottom: 0.6rem;
    margin-bottom: 0.3rem !important;
}

h2 {
    font-weight: 600 !important;
    color: #d4a574 !important;
    font-size: 1.4rem !important;
    margin-top: 1.5rem !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

h3 {
    font-weight: 400 !important;
    font-style: italic;
    font-size: 1.25rem !important;
}

.stCaption, [data-testid="stCaptionContainer"] {
    color: #b8a88a !important;
    font-style: italic;
    font-size: 0.95rem !important;
}

.stButton > button {
    background: rgba(245, 235, 208, 0.04);
    color: #f5ebd0 !important;
    border: 1px solid rgba(212, 165, 116, 0.4);
    border-radius: 3px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
    font-size: 1.05rem;
    transition: all 0.15s ease;
    min-height: 3.2rem;
}

.stButton > button:hover {
    background: rgba(212, 165, 116, 0.15);
    border-color: #d4a574;
    color: #ffffff !important;
    transform: translateY(-1px);
}

.stButton > button:disabled {
    opacity: 0.25;
    cursor: not-allowed;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(180deg, #d4a574 0%, #b88a5a 100%);
    color: #0d3b2e !important;
    border: none;
    font-family: 'Playfair Display', serif;
    font-size: 1.25rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    min-height: 3.8rem;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(180deg, #e6b684 0%, #c89a6a 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
}

.stNumberInput input, .stSelectbox > div > div {
    background: rgba(0, 0, 0, 0.25) !important;
    color: #f5ebd0 !important;
    border: 1px solid rgba(212, 165, 116, 0.3) !important;
    font-family: 'JetBrains Mono', monospace !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Playfair Display', serif !important;
    font-size: 2.5rem !important;
    color: #d4a574 !important;
    font-weight: 700 !important;
}

[data-testid="stMetricLabel"] {
    color: #b8a88a !important;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    font-size: 0.75rem !important;
}

hr {
    border-color: rgba(212, 165, 116, 0.25) !important;
    margin: 2rem 0 !important;
}

.reco-banner {
    text-align: center;
    padding: 2rem 1rem;
    border: 1px solid rgba(212, 165, 116, 0.4);
    border-radius: 4px;
    background: rgba(0, 0, 0, 0.25);
    margin: 1rem 0;
}
.reco-action {
    font-family: 'Playfair Display', serif;
    font-size: 3.5rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    margin: 0;
}
.reco-raise, .reco-bet { color: #a8d4a0; }
.reco-call, .reco-check { color: #d4a574; }
.reco-fold { color: #c47878; }
.reco-reasoning {
    font-style: italic;
    font-size: 1.1rem;
    color: #d8c89a;
    margin-top: 1rem;
    line-height: 1.5;
}
</style>
""", unsafe_allow_html=True)


# ---------- Header ----------

st.markdown("<h1>Poker AI Advisor</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='color: #b8a88a; font-style: italic; margin-top: -0.5rem;'>"
    "Range-based recommendations for No-Limit Hold'em</p>",
    unsafe_allow_html=True,
)


# ---------- Session State ----------

SLOT_NAMES = ["hole_1", "hole_2", "flop_1", "flop_2", "flop_3", "turn", "river"]

if "cards" not in st.session_state:
    st.session_state.cards = {slot: None for slot in SLOT_NAMES}
if "picker_open" not in st.session_state:
    st.session_state.picker_open = None


# ---------- Helpers ----------

def used_cards() -> set[str]:
    return {c for c in st.session_state.cards.values() if c is not None}

def get_hole_cards() -> list[str]:
    return [c for c in (st.session_state.cards["hole_1"], st.session_state.cards["hole_2"]) if c]

def get_board_cards() -> list[str]:
    board = []
    for slot in ["flop_1", "flop_2", "flop_3", "turn", "river"]:
        card = st.session_state.cards[slot]
        if card is None:
            break
        board.append(card)
    return board

def open_picker(slot: str):
    st.session_state.picker_open = slot

def assign_card(card: str):
    slot = st.session_state.picker_open
    if slot:
        st.session_state.cards[slot] = card
        st.session_state.picker_open = None

def clear_slot(slot: str):
    st.session_state.cards[slot] = None

def reset_all_cards():
    for slot in SLOT_NAMES:
        st.session_state.cards[slot] = None
    st.session_state.picker_open = None


# ---------- Card Slot Rendering ----------

def render_slot(slot: str, placeholder: str):
    card = st.session_state.cards[slot]
    if card is None:
        if st.button(f"＋  {placeholder}", key=f"slot_{slot}", use_container_width=True):
            open_picker(slot)
            st.rerun()
    else:
        if st.button(format_card(card), key=f"slot_{slot}", use_container_width=True):
            clear_slot(slot)
            st.rerun()


def render_card_picker():
    slot = st.session_state.picker_open
    if slot is None:
        return
    
    st.divider()
    label = slot.replace("_", " ").title()
    st.markdown(f"### Select card for <span style='color:#d4a574'>{label}</span>", unsafe_allow_html=True)
    
    if st.button("✕ Cancel", key="cancel_picker"):
        st.session_state.picker_open = None
        st.rerun()
    
    taken = used_cards()
    
    for rank in RANKS:
        cols = st.columns(4)
        for idx, suit in enumerate(SUITS):
            card = rank + suit
            with cols[idx]:
                if st.button(
                    format_card(card),
                    key=f"pick_{card}",
                    use_container_width=True,
                    disabled=(card in taken),
                ):
                    assign_card(card)
                    st.rerun()
    
    st.divider()


# ---------- Cards UI ----------

st.markdown("<h2>Hole Cards</h2>", unsafe_allow_html=True)

hole_cols = st.columns(2)
with hole_cols[0]:
    render_slot("hole_1", "Card 1")
with hole_cols[1]:
    render_slot("hole_2", "Card 2")

st.markdown("<h2>Community Board</h2>", unsafe_allow_html=True)

board_cols = st.columns(5)
for idx, (slot, label) in enumerate([
    ("flop_1", "Flop"),
    ("flop_2", "Flop"),
    ("flop_3", "Flop"),
    ("turn", "Turn"),
    ("river", "River"),
]):
    with board_cols[idx]:
        render_slot(slot, label)

render_card_picker()

col_reset, _ = st.columns([1, 3])
with col_reset:
    if st.button("Reset Cards"):
        reset_all_cards()
        st.rerun()


# ---------- Game Context UI ----------

st.markdown("<h2>Game Context</h2>", unsafe_allow_html=True)

ctx_cols = st.columns(2)
with ctx_cols[0]:
    position_str = st.selectbox(
        "Your position",
        options=["UTG", "MP", "CO", "BTN", "SB", "BB"],
        index=3,
    )
    stack = st.number_input("Your stack (BB)", min_value=1.0, value=100.0, step=10.0)

with ctx_cols[1]:
    pot = st.number_input("Pot size (BB)", min_value=0.0, value=1.5, step=0.5)
    to_call = st.number_input("Amount to call (BB)", min_value=0.0, value=0.0, step=0.5)


# ---------- Villain Modeling UI (NEW) ----------

st.markdown("<h2>Opponent Profile</h2>", unsafe_allow_html=True)
st.caption(
    "When there's betting action, who is the aggressor? "
    "This tells the advisor what range of hands to model them on."
)

villain_pos_str = st.selectbox(
    "Villain's position",
    options=["(none / not facing a bet)", "UTG", "MP", "CO", "BTN", "SB", "BB"],
    index=0,
    help=(
        "UTG villains have tight ranges; BTN villains have loose ranges. "
        "If preflop or no bet to face, leave as 'none'."
    ),
)


# ---------- Compute & Display ----------

st.divider()

if st.button("Get Recommendation", type="primary", use_container_width=True):
    hole = get_hole_cards()
    board = get_board_cards()
    
    if len(hole) != 2:
        st.error("Please select both hole cards before getting a recommendation.")
        st.stop()
    
    if len(board) not in (0, 3, 4, 5):
        st.error(
            f"Board has {len(board)} card(s). Select 0 (preflop), "
            "3 (flop), 4 (turn), or 5 (river) cards consecutively."
        )
        st.stop()
    
    # Parse villain position
    villain_position: Position | None = None
    if villain_pos_str != "(none / not facing a bet)":
        villain_position = Position(villain_pos_str)
    
    try:
        state = GameState(
            hole_cards=hole,
            position=Position(position_str),
            stack=stack,
            board=board,
            pot=pot,
            to_call=to_call,
            villain_position=villain_position,
        )
        
        with st.spinner("Modeling villain's range and calculating equity..."):
            advisor = RangeBasedAdvisor(iterations=2000)
            result = advisor.recommend(state)
        
        action = result["action"].lower()
        action_display = result["action"].upper()
        
        st.markdown(
            f"""
            <div class="reco-banner">
                <p class="reco-action reco-{action}">{action_display}</p>
                <p class="reco-reasoning">{result["reasoning"]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        metric_cols = st.columns(2)
        with metric_cols[0]:
            if result["equity"] is not None:
                st.metric("Your Equity", f"{result['equity']:.1%}")
            else:
                st.metric("Your Equity", "—")
        with metric_cols[1]:
            if to_call > 0:
                st.metric("Pot Odds Needed", f"{result['pot_odds']:.1%}")
            else:
                st.metric("Pot Odds Needed", "—")
    
    except ValueError as e:
        st.error(f"Input error: {e}")