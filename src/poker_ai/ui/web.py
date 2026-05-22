"""
Poker AI - Phase 7: UI Polish
Drop-in replacement for src/poker_ai/ui/web.py

No-scroll constraint: everything fits in the viewport at all times.
All state managed via st.session_state.
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from poker_ai.core.game_state import GameState, Position, Street
from poker_ai.advisor.range_based import RangeBasedAdvisor
from poker_ai.utils.cards import RANKS, SUITS, SUIT_SYMBOLS, SUIT_COLORS, all_cards, format_card

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Poker AI",
    page_icon="♠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── GLOBAL CSS ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&family=DM+Mono:wght@300;400&display=swap');

/* ── Reset & Base ── */
* { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    height: 100vh !important;
    max-height: 100vh !important;
    overflow: hidden !important;
    background: #0a0d12 !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #e2e8f0 !important;
}

[data-testid="stMainBlockContainer"] {
    padding: 0 !important;
    max-width: 100% !important;
}

[data-testid="stVerticalBlock"] { gap: 0 !important; }

/* Hide Streamlit chrome */
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"],
[data-testid="collapsedControl"] { display: none !important; }

section[data-testid="stSidebar"] { display: none !important; }

/* ── Design Tokens ── */
:root {
    --bg-base:      #0a0d12;
    --bg-surface:   #111520;
    --bg-card:      #161c2a;
    --bg-raised:    #1d2438;
    --bg-input:     #1a2035;
    --border:       rgba(255,255,255,0.07);
    --border-hover: rgba(255,255,255,0.14);
    --border-accent:#2a6fdb;
    --accent:       #3b82f6;
    --accent-dim:   #1d4ed8;
    --accent-glow:  rgba(59,130,246,0.15);
    --green:        #10b981;
    --green-dim:    rgba(16,185,129,0.12);
    --red:          #ef4444;
    --red-dim:      rgba(239,68,68,0.12);
    --amber:        #f59e0b;
    --amber-dim:    rgba(245,158,11,0.12);
    --text-primary: #e2e8f0;
    --text-secondary:#94a3b8;
    --text-muted:   #4a5568;
    --suit-heart:   #f87171;
    --suit-diamond: #f87171;
    --suit-spade:   #e2e8f0;
    --suit-club:    #e2e8f0;
    --radius-sm:    6px;
    --radius-md:    10px;
    --radius-lg:    14px;
    --radius-xl:    20px;
}

/* ── Streamlit element overrides ── */
.stButton > button {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    border-radius: var(--radius-md) !important;
    transition: all 0.15s ease !important;
    border: 1px solid var(--border) !important;
    background: var(--bg-raised) !important;
    color: var(--text-primary) !important;
    padding: 0.45rem 1rem !important;
    line-height: 1.4 !important;
}
.stButton > button:hover {
    border-color: var(--border-hover) !important;
    background: #232c42 !important;
}
.stButton > button:focus { outline: none !important; box-shadow: none !important; }

.stSelectbox [data-baseweb="select"] > div,
.stNumberInput input,
.stTextInput input {
    background: var(--bg-input) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
}
.stSelectbox [data-baseweb="select"] > div:hover,
.stNumberInput input:hover,
.stTextInput input:hover {
    border-color: var(--border-hover) !important;
}
.stSelectbox [data-baseweb="select"] > div:focus-within,
.stNumberInput input:focus,
.stTextInput input:focus {
    border-color: var(--border-accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
}

/* Dropdown menu */
[data-baseweb="popover"], [data-baseweb="menu"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
}
[data-baseweb="option"] { color: var(--text-primary) !important; }
[data-baseweb="option"]:hover { background: var(--bg-raised) !important; }

/* Number input buttons */
.stNumberInput button {
    background: var(--bg-input) !important;
    border-color: var(--border) !important;
    color: var(--text-secondary) !important;
}

label, .stSelectbox label, .stNumberInput label, .stTextInput label {
    color: var(--text-secondary) !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Divider */
hr { border-color: var(--border) !important; margin: 0 !important; }

/* Remove extra padding on columns */
[data-testid="column"] { padding: 0 !important; }
[data-testid="stHorizontalBlock"] { gap: 0 !important; }

/* ── Custom Components ── */

.pai-shell {
    display: grid;
    grid-template-rows: 52px 1fr;
    height: 100vh;
    background: var(--bg-base);
    overflow: hidden;
}

.pai-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 24px;
    border-bottom: 1px solid var(--border);
    background: var(--bg-surface);
    flex-shrink: 0;
}

.pai-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: -0.01em;
}

.pai-logo-icon {
    width: 28px;
    height: 28px;
    background: var(--accent);
    border-radius: 7px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    color: white;
    font-weight: 700;
}

.pai-session-badge {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: var(--text-secondary);
    background: var(--bg-card);
    border: 1px solid var(--border);
    padding: 5px 12px;
    border-radius: 20px;
}

.pai-dot-green { width:7px; height:7px; border-radius:50%; background:var(--green); }
.pai-dot-amber { width:7px; height:7px; border-radius:50%; background:var(--amber); }

/* ── Landing Page ── */
.pai-landing {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    background: var(--bg-base);
}

.pai-landing-card {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-xl);
    padding: 40px 44px;
    width: 520px;
    max-width: 96vw;
}

.pai-landing-title {
    font-size: 26px;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: -0.03em;
    margin-bottom: 4px;
}

.pai-landing-sub {
    font-size: 13px;
    color: var(--text-secondary);
    margin-bottom: 32px;
    font-weight: 300;
}

.pai-section-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 12px;
}

.pai-input-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 14px;
}

.pai-divider {
    border-top: 1px solid var(--border);
    margin: 24px 0;
}

.pai-start-btn {
    width: 100%;
    padding: 14px;
    background: var(--accent) !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    color: white !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    cursor: pointer;
    transition: background 0.15s;
    letter-spacing: -0.01em;
}
.pai-start-btn:hover { background: #2563eb !important; }

/* ── Main App Layout ── */
.pai-body {
    display: grid;
    grid-template-columns: 280px 1fr 300px;
    height: calc(100vh - 52px);
    overflow: hidden;
}

.pai-panel {
    border-right: 1px solid var(--border);
    padding: 20px 18px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    gap: 14px;
}

.pai-panel-right {
    border-left: 1px solid var(--border);
    border-right: none;
    padding: 20px 18px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    gap: 14px;
}

.pai-center {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    padding: 24px 32px;
    overflow: hidden;
    gap: 16px;
    background: var(--bg-base);
    background-image: radial-gradient(ellipse at 50% 100%, rgba(59,130,246,0.04) 0%, transparent 70%);
}

/* ── Panel Header ── */
.pai-panel-header {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
}

/* ── Stat Row ── */
.pai-stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 9px 12px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
}
.pai-stat-label { font-size: 12px; color: var(--text-secondary); }
.pai-stat-value { font-size: 14px; font-weight: 500; color: var(--text-primary); font-family: 'DM Mono', monospace; }
.pai-stat-value.green { color: var(--green); }
.pai-stat-value.red { color: var(--red); }
.pai-stat-value.amber { color: var(--amber); }

/* ── Playing Card ── */
.pai-card-slot {
    width: 62px;
    height: 88px;
    border-radius: 8px;
    border: 1.5px dashed var(--border-hover);
    background: var(--bg-card);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.12s;
    flex-shrink: 0;
}
.pai-card-slot:hover {
    border-color: var(--accent);
    background: var(--accent-glow);
}

.pai-card {
    width: 62px;
    height: 88px;
    border-radius: 8px;
    border: 1.5px solid rgba(255,255,255,0.12);
    background: #1e2535;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.12s;
    flex-shrink: 0;
    position: relative;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
}
.pai-card:hover { border-color: var(--accent); transform: translateY(-2px); }

.pai-card-rank {
    font-size: 22px;
    font-weight: 700;
    line-height: 1;
    font-family: 'DM Mono', monospace;
}
.pai-card-suit { font-size: 18px; line-height: 1; margin-top: 2px; }
.pai-card-rank.red, .pai-card-suit.red { color: var(--suit-heart); }
.pai-card-rank.black, .pai-card-suit.black { color: var(--suit-spade); }

.pai-card-area {
    display: flex;
    align-items: center;
    gap: 10px;
}

/* ── Street Label ── */
.pai-street-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
    text-align: center;
}

/* ── Board Section ── */
.pai-board-row {
    display: flex;
    align-items: center;
    gap: 10px;
}

.pai-board-group {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
}

.pai-hole-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
}

/* ── Action Buttons ── */
.pai-action-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 6px;
    width: 100%;
}

.pai-action-btn {
    padding: 9px 0;
    border-radius: var(--radius-md);
    border: 1px solid var(--border);
    background: var(--bg-card);
    color: var(--text-secondary);
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.12s;
    text-align: center;
    font-family: 'DM Sans', sans-serif;
    letter-spacing: 0.01em;
}
.pai-action-btn:hover { border-color: var(--border-hover); color: var(--text-primary); background: var(--bg-raised); }
.pai-action-btn.selected { border-color: var(--accent); background: var(--accent-glow); color: var(--accent); }

/* ── Recommendation Box ── */
.pai-rec-box {
    width: 100%;
    padding: 16px 20px;
    border-radius: var(--radius-lg);
    border: 1px solid var(--border);
    background: var(--bg-card);
}

.pai-rec-action {
    font-size: 24px;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin-bottom: 4px;
}
.pai-rec-action.FOLD  { color: var(--red); }
.pai-rec-action.CALL  { color: var(--amber); }
.pai-rec-action.CHECK { color: var(--text-primary); }
.pai-rec-action.BET   { color: var(--green); }
.pai-rec-action.RAISE { color: var(--green); }

.pai-rec-detail {
    font-size: 12px;
    color: var(--text-secondary);
    line-height: 1.5;
}

.pai-equity-bar-wrap {
    margin-top: 12px;
    height: 4px;
    background: var(--bg-raised);
    border-radius: 2px;
    overflow: hidden;
}
.pai-equity-bar { height: 100%; border-radius: 2px; transition: width 0.4s ease; }

/* ── Card Picker Overlay ── */
.pai-picker-wrap {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 14px;
    width: 100%;
}

.pai-picker-title {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin-bottom: 10px;
}

.pai-picker-grid {
    display: grid;
    grid-template-columns: repeat(13, 1fr);
    gap: 3px;
}

.pai-pick-btn {
    aspect-ratio: 1;
    border-radius: 5px;
    border: 1px solid var(--border);
    background: var(--bg-card);
    font-size: 10px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.1s;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    line-height: 1;
    gap: 1px;
    padding: 2px;
}
.pai-pick-btn:hover { border-color: var(--accent); background: var(--accent-glow); }
.pai-pick-btn.used { opacity: 0.2; cursor: not-allowed; }
.pai-pick-btn.selected { border-color: var(--accent); background: var(--accent-glow); }
.pai-pick-btn .pr { font-size: 11px; }
.pai-pick-btn .ps { font-size: 9px; }
.pai-pick-btn.red .pr, .pai-pick-btn.red .ps { color: var(--suit-heart); }
.pai-pick-btn.black .pr, .pai-pick-btn.black .ps { color: var(--suit-spade); }

/* ── Street Progress ── */
.pai-progress {
    display: flex;
    gap: 4px;
    align-items: center;
}
.pai-progress-step {
    height: 3px;
    border-radius: 2px;
    flex: 1;
    background: var(--border);
    transition: background 0.2s;
}
.pai-progress-step.done { background: var(--accent); }
.pai-progress-step.active { background: var(--green); }

/* ── History Log ── */
.pai-log-entry {
    font-size: 12px;
    color: var(--text-secondary);
    padding: 8px 10px;
    background: var(--bg-card);
    border-radius: var(--radius-sm);
    border-left: 2px solid var(--border);
    font-family: 'DM Mono', monospace;
    margin-bottom: 4px;
}
.pai-log-entry.fold  { border-left-color: var(--red); }
.pai-log-entry.call  { border-left-color: var(--amber); }
.pai-log-entry.raise { border-left-color: var(--green); }
.pai-log-entry.bet   { border-left-color: var(--green); }

/* ── Next-Hand Button ── */
.pai-next-btn {
    width: 100%;
    padding: 10px;
    border-radius: var(--radius-md);
    border: 1px solid var(--border);
    background: transparent;
    color: var(--text-secondary);
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.12s;
    font-family: 'DM Sans', sans-serif;
    letter-spacing: -0.01em;
}
.pai-next-btn:hover { border-color: var(--border-hover); color: var(--text-primary); background: var(--bg-raised); }

/* ── Scrollable log area ── */
.pai-log-scroll {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    scrollbar-width: thin;
    scrollbar-color: var(--bg-raised) transparent;
}

/* placeholder for future features */
.pai-future-badge {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--text-muted);
    background: var(--bg-card);
    border: 1px solid var(--border);
    padding: 3px 8px;
    border-radius: 20px;
    display: inline-block;
}

</style>
""", unsafe_allow_html=True)


# ─── SESSION STATE INIT ───────────────────────────────────────────────────────

def init_state():
    defaults = {
        # Setup
        "phase": "landing",          # landing | game
        "small_blind": 1.0,
        "big_blind": 2.0,
        "num_players": 6,
        "starting_stack": 200.0,
        "username": "",
        "current_stack": 200.0,
        "session_pnl": 0.0,
        "hand_number": 0,
        # Hand state
        "cards": {
            "h1": None, "h2": None,
            "b1": None, "b2": None, "b3": None, "b4": None, "b5": None,
        },
        "picker_open": None,
        "position": "BTN",
        "villain_position": "UTG",
        "pot": 3.0,
        "to_call": 0.0,
        "hand_action": None,
        "recommendation": None,
        "hand_log": [],
        "current_street": "PREFLOP",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ─── HELPERS ─────────────────────────────────────────────────────────────────

POSITIONS = ["UTG", "MP", "CO", "BTN", "SB", "BB"]
STREETS   = ["PREFLOP", "FLOP", "TURN", "RIVER"]

SUIT_SYMBOL = {"h": "♥", "d": "♦", "s": "♠", "c": "♣"}
SUIT_COLOR  = {"h": "red", "d": "red", "s": "black", "c": "black"}

def used_cards():
    return {v for v in st.session_state.cards.values() if v is not None}

def get_hole_cards():
    h = [st.session_state.cards["h1"], st.session_state.cards["h2"]]
    return [c for c in h if c is not None]

def get_board_cards():
    board = []
    for k in ["b1","b2","b3","b4","b5"]:
        c = st.session_state.cards[k]
        if c: board.append(c)
    return board

def street_from_board(board):
    n = len(board)
    if n == 0: return "PREFLOP"
    if n <= 3: return "FLOP"
    if n == 4: return "TURN"
    return "RIVER"

def card_html(card, slot_key, size="normal"):
    """Render a filled card as HTML."""
    rank = card[:-1]
    suit = card[-1]
    sym  = SUIT_SYMBOL[suit]
    col  = SUIT_COLOR[suit]
    w, h = ("62px", "88px") if size == "normal" else ("50px", "70px")
    return f"""
    <div class="pai-card" style="width:{w};height:{h};" title="Click to change">
        <span class="pai-card-rank {col}">{rank}</span>
        <span class="pai-card-suit {col}">{sym}</span>
    </div>
    """

def empty_slot_html(size="normal"):
    w, h = ("62px", "88px") if size == "normal" else ("50px", "70px")
    return f'<div class="pai-card-slot" style="width:{w};height:{h};">＋</div>'

def get_action_color(action):
    if action is None: return "var(--text-muted)"
    a = action.upper()
    if a == "FOLD":  return "var(--red)"
    if a in ("BET","RAISE"): return "var(--green)"
    if a == "CALL": return "var(--amber)"
    return "var(--text-primary)"

def equity_color(eq):
    if eq >= 0.65: return "var(--green)"
    if eq >= 0.45: return "var(--amber)"
    return "var(--red)"


# ─── CARD PICKER ─────────────────────────────────────────────────────────────

def render_card_picker(slot_key):
    """Compact 13×4 grid card picker."""
    used = used_cards()
    rank_order = ["A","K","Q","J","T","9","8","7","6","5","4","3","2"]
    suit_order = ["s","h","d","c"]

    st.markdown('<div class="pai-picker-wrap"><div class="pai-picker-title">Select card</div><div class="pai-picker-grid">', unsafe_allow_html=True)

    cols = st.columns(13)
    for ci, rank in enumerate(rank_order):
        for suit in suit_order:
            card = rank + suit
            sym  = SUIT_SYMBOL[suit]
            col  = SUIT_COLOR[suit]
            is_used     = card in used and card != st.session_state.cards.get(slot_key)
            is_selected = st.session_state.cards.get(slot_key) == card
            css_class   = ("used" if is_used else "") + f" {col}" + (" selected" if is_selected else "")
            with cols[ci]:
                if st.button(
                    f"{rank}\n{sym}",
                    key=f"pick_{slot_key}_{card}",
                    disabled=is_used,
                    use_container_width=True,
                ):
                    st.session_state.cards[slot_key] = card
                    st.session_state.picker_open = None
                    st.session_state.recommendation = None
                    st.rerun()

    st.markdown('</div></div>', unsafe_allow_html=True)

    if st.button("✕  Cancel", key=f"cancel_picker_{slot_key}"):
        st.session_state.picker_open = None
        st.rerun()


# ─── RUN ADVISOR ─────────────────────────────────────────────────────────────

def run_advisor():
    hole  = get_hole_cards()
    board = get_board_cards()
    if len(hole) < 2:
        return {"error": "Enter both hole cards first."}
    pos_map = {p: getattr(Position, p) for p in POSITIONS}
    try:
        state = GameState(
            hole_cards=hole,
            position=pos_map[st.session_state.position],
            stack=st.session_state.current_stack / st.session_state.big_blind,
            board=board,
            pot=st.session_state.pot / st.session_state.big_blind,
            to_call=st.session_state.to_call / st.session_state.big_blind,
            num_players=st.session_state.num_players,
            effective_stack=st.session_state.current_stack / st.session_state.big_blind,
            villain_position=pos_map.get(st.session_state.villain_position),
        )
        advisor = RangeBasedAdvisor()
        return advisor.recommend(state)
    except Exception as e:
        return {"error": str(e)}


# ─── TOP BAR ─────────────────────────────────────────────────────────────────

def render_topbar():
    phase = st.session_state.phase
    session_active = phase == "game"
    pnl = st.session_state.session_pnl
    pnl_str = f"+${pnl:.0f}" if pnl >= 0 else f"-${abs(pnl):.0f}"
    pnl_col = "#10b981" if pnl >= 0 else "#ef4444"

    hand_n = st.session_state.hand_number
    dot = "pai-dot-green" if session_active else "pai-dot-amber"
    status = f"Hand #{hand_n}" if session_active else "Setup"

    st.markdown(f"""
    <div class="pai-topbar">
        <div class="pai-logo">
            <div class="pai-logo-icon">♠</div>
            Poker AI
        </div>
        <div style="display:flex;align-items:center;gap:12px;">
            {"" if not session_active else f'<span style="font-size:13px;color:{pnl_col};font-weight:600;font-family:DM Mono,monospace;">{pnl_str}</span>'}
            <div class="pai-session-badge">
                <div class="{dot}"></div>
                <span>{status}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── LANDING PAGE ─────────────────────────────────────────────────────────────

def render_landing():
    st.markdown('<div class="pai-landing">', unsafe_allow_html=True)

    with st.container():
        st.markdown("""
        <div class="pai-landing-card">
            <div class="pai-landing-title">Poker AI Assistant</div>
            <div class="pai-landing-sub">Real-time decision support for No-Limit Hold'em cash games</div>
        </div>
        """, unsafe_allow_html=True)

        # Use Streamlit inputs overlaid via columns trick inside landing card
        # We'll render them below since Streamlit can't nest inside raw HTML divs
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("##### Game Setup")
            c1, c2 = st.columns(2)
            with c1:
                sb = st.number_input("Small Blind ($)", min_value=0.25, max_value=100.0,
                                      value=float(st.session_state.small_blind), step=0.25, key="inp_sb")
            with c2:
                bb = st.number_input("Big Blind ($)", min_value=0.5, max_value=200.0,
                                      value=float(st.session_state.big_blind), step=0.5, key="inp_bb")

            c3, c4 = st.columns(2)
            with c3:
                n_players = st.number_input("Players", min_value=2, max_value=9,
                                             value=st.session_state.num_players, step=1, key="inp_players")
            with c4:
                stack = st.number_input("Starting Stack ($)", min_value=10.0, max_value=10000.0,
                                         value=float(st.session_state.starting_stack), step=10.0, key="inp_stack")

            st.markdown("---")
            username = st.text_input("Username (coming soon)", placeholder="Optional — future profile feature",
                                      key="inp_username", disabled=True)

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            if st.button("▶  Begin Session", use_container_width=True, key="btn_start"):
                st.session_state.small_blind   = sb
                st.session_state.big_blind     = bb
                st.session_state.num_players   = n_players
                st.session_state.starting_stack = stack
                st.session_state.current_stack = stack
                st.session_state.pot           = round(sb + bb, 2)
                st.session_state.hand_number   = 1
                st.session_state.phase         = "game"
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ─── LEFT PANEL — Context ────────────────────────────────────────────────────

def render_left_panel():
    st.markdown('<div class="pai-panel-header">Session Context</div>', unsafe_allow_html=True)

    bb = st.session_state.big_blind
    stack = st.session_state.current_stack
    stack_bb = stack / bb

    # Stack
    st.markdown(f"""
    <div class="pai-stat-row">
        <span class="pai-stat-label">Stack</span>
        <span class="pai-stat-value">${stack:.0f} <span style="color:var(--text-muted);font-size:11px">({stack_bb:.0f}bb)</span></span>
    </div>
    """, unsafe_allow_html=True)

    # Session P&L
    pnl = st.session_state.session_pnl
    pnl_cls = "green" if pnl >= 0 else "red"
    pnl_str = f"+${pnl:.0f}" if pnl >= 0 else f"-${abs(pnl):.0f}"
    st.markdown(f"""
    <div class="pai-stat-row">
        <span class="pai-stat-label">Session P&amp;L</span>
        <span class="pai-stat-value {pnl_cls}">{pnl_str}</span>
    </div>
    """, unsafe_allow_html=True)

    # Blinds
    st.markdown(f"""
    <div class="pai-stat-row">
        <span class="pai-stat-label">Blinds</span>
        <span class="pai-stat-value">${st.session_state.small_blind:.2f}/${st.session_state.big_blind:.2f}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="pai-panel-header" style="margin-top:4px">Your Position</div>', unsafe_allow_html=True)

    st.session_state.position = st.selectbox(
        "Hero position", POSITIONS,
        index=POSITIONS.index(st.session_state.position),
        label_visibility="collapsed", key="sel_pos"
    )

    st.markdown('<div class="pai-panel-header" style="margin-top:4px">Villain Position</div>', unsafe_allow_html=True)
    st.session_state.villain_position = st.selectbox(
        "Villain position", POSITIONS,
        index=POSITIONS.index(st.session_state.villain_position),
        label_visibility="collapsed", key="sel_vpos"
    )

    st.markdown('<div class="pai-panel-header" style="margin-top:4px">Pot & Bet</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.session_state.pot = st.number_input(
            "Pot ($)", min_value=0.0, max_value=50000.0,
            value=float(st.session_state.pot), step=1.0, key="inp_pot",
            label_visibility="visible"
        )
    with c2:
        st.session_state.to_call = st.number_input(
            "To Call ($)", min_value=0.0, max_value=50000.0,
            value=float(st.session_state.to_call), step=1.0, key="inp_call",
            label_visibility="visible"
        )

    # Spacer + Next Hand
    st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)

    if st.button("→  Next Hand", use_container_width=True, key="btn_next_hand"):
        # Update stack & P&L based on pot result (neutral here — user tracks)
        st.session_state.hand_number += 1
        # Reset hand state
        for k in ["h1","h2","b1","b2","b3","b4","b5"]:
            st.session_state.cards[k] = None
        st.session_state.picker_open   = None
        st.session_state.recommendation = None
        st.session_state.hand_action   = None
        st.session_state.pot           = round(st.session_state.small_blind + st.session_state.big_blind, 2)
        st.session_state.to_call       = 0.0
        st.rerun()

    if st.button("⚙  End Session", use_container_width=True, key="btn_end"):
        # Ask for stack update then return to landing
        st.session_state.phase = "landing"
        st.rerun()


# ─── CENTER — Cards & Board ───────────────────────────────────────────────────

def render_center():
    board  = get_board_cards()
    street = street_from_board(board)
    st.session_state.current_street = street

    # ── Street Progress ──
    steps = ["PREFLOP","FLOP","TURN","RIVER"]
    bars  = []
    for s in steps:
        si = steps.index(s)
        ci = steps.index(street)
        css = "done" if si < ci else ("active" if si == ci else "")
        bars.append(f'<div class="pai-progress-step {css}"></div>')
    st.markdown(
        f'<div style="width:100%;display:flex;gap:4px;margin-bottom:4px">{"".join(bars)}</div>'
        f'<div style="font-size:11px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:var(--text-muted);text-align:center;margin-bottom:8px">{street}</div>',
        unsafe_allow_html=True
    )

    # ── Hole Cards ──
    st.markdown('<div style="display:flex;flex-direction:column;align-items:center;gap:6px;margin-bottom:8px">', unsafe_allow_html=True)
    st.markdown('<div class="pai-street-label">Your Hand</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    h1c, h2c = st.columns([1,1], gap="small")
    for slot, col in [("h1", h1c), ("h2", h2c)]:
        with col:
            card = st.session_state.cards[slot]
            label = card if card else "＋"
            btn_style = ""
            if card:
                suit = card[-1]
                clr = "#f87171" if suit in "hd" else "#e2e8f0"
                label = f"{card[:-1]} {SUIT_SYMBOL[suit]}"
            if st.button(label, key=f"slot_{slot}", use_container_width=True):
                st.session_state.picker_open = slot if st.session_state.picker_open != slot else None
                st.rerun()

    # ── Card Picker (if open) ──
    if st.session_state.picker_open in ("h1","h2","b1","b2","b3","b4","b5"):
        render_card_picker(st.session_state.picker_open)

    # ── Board Cards ──
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="pai-street-label">Board</div>', unsafe_allow_html=True)
    st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)

    board_cols = st.columns(5, gap="small")
    board_slots = ["b1","b2","b3","b4","b5"]
    # Only allow entering board cards in sequence
    for i, (slot, col) in enumerate(zip(board_slots, board_cols)):
        with col:
            card = st.session_state.cards[slot]
            prev_filled = i == 0 or st.session_state.cards[board_slots[i-1]] is not None
            if card:
                suit = card[-1]
                label = f"{card[:-1]}{SUIT_SYMBOL[suit]}"
                disabled = False
            else:
                label = "＋"
                disabled = not prev_filled
            if st.button(label, key=f"slot_{slot}", use_container_width=True, disabled=disabled):
                st.session_state.picker_open = slot if st.session_state.picker_open != slot else None
                st.rerun()

    # ── Recommendation ──
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    rec = st.session_state.recommendation

    if rec and "error" not in rec:
        action = rec.get("action","").upper()
        equity = rec.get("equity")
        reasoning = rec.get("reasoning","")
        pot_odds  = rec.get("pot_odds", 0)

        eq_pct   = f"{equity*100:.0f}%" if equity is not None else "—"
        eq_color = equity_color(equity) if equity is not None else "var(--text-muted)"
        eq_bar_w = f"{equity*100:.0f}%" if equity is not None else "0%"
        eq_bar_col = eq_color

        st.markdown(f"""
        <div class="pai-rec-box">
            <div style="display:flex;align-items:baseline;gap:16px;margin-bottom:6px;">
                <span class="pai-rec-action {action}">{action}</span>
                <span style="font-size:13px;color:var(--text-secondary);">
                    Equity: <span style="color:{eq_color};font-weight:600;">{eq_pct}</span>
                    &nbsp;·&nbsp; Pot odds: {pot_odds*100:.0f}%
                </span>
            </div>
            <div class="pai-rec-detail">{reasoning}</div>
            <div class="pai-equity-bar-wrap">
                <div class="pai-equity-bar" style="width:{eq_bar_w};background:{eq_bar_col};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Log to hand history
        if "logged_rec" not in st.session_state or st.session_state.logged_rec != (st.session_state.hand_number, action):
            entry = {
                "hand": st.session_state.hand_number,
                "street": street,
                "action": action,
                "equity": eq_pct,
            }
            st.session_state.hand_log.insert(0, entry)
            st.session_state.logged_rec = (st.session_state.hand_number, action)

    elif rec and "error" in rec:
        st.markdown(f"""
        <div class="pai-rec-box">
            <div style="color:var(--red);font-size:13px;">{rec['error']}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="pai-rec-box" style="text-align:center;padding:24px;">
            <div style="color:var(--text-muted);font-size:13px;">Enter cards and hit Analyze</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Analyze Button ──
    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
    if st.button("⚡  Analyze Hand", use_container_width=True, key="btn_analyze"):
        st.session_state.recommendation = run_advisor()
        st.rerun()


# ─── RIGHT PANEL — Actions & Log ─────────────────────────────────────────────

def render_right_panel():
    st.markdown('<div class="pai-panel-header">Facing Action</div>', unsafe_allow_html=True)

    actions = ["Fold","Check","Call","Bet","Raise","All-in"]
    current = st.session_state.hand_action

    # 2×3 button grid
    r1 = st.columns(3, gap="small")
    r2 = st.columns(3, gap="small")
    for i, act in enumerate(actions):
        col = r1[i] if i < 3 else r2[i-3]
        with col:
            selected = current == act
            label = f"✓ {act}" if selected else act
            if st.button(label, key=f"action_{act}", use_container_width=True):
                st.session_state.hand_action = act
                st.rerun()

    # ── Hand History ──
    st.markdown('<div class="pai-panel-header" style="margin-top:8px">Hand History</div>', unsafe_allow_html=True)
    st.markdown('<div class="pai-future-badge">Analytics coming in a future phase</div>', unsafe_allow_html=True)
    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)

    log = st.session_state.hand_log
    if not log:
        st.markdown('<div style="font-size:12px;color:var(--text-muted);padding:8px 0;">No hands analyzed yet.</div>', unsafe_allow_html=True)
    else:
        scroll_html = '<div class="pai-log-scroll">'
        for entry in log[:20]:
            act_cls = entry["action"].lower()
            scroll_html += f"""
            <div class="pai-log-entry {act_cls}">
                H#{entry['hand']} · {entry['street']}<br>
                <span style="color:var(--text-primary);font-weight:500">{entry['action']}</span>
                {f"· eq {entry['equity']}" if entry.get('equity') != '—' else ""}
            </div>
            """
        scroll_html += '</div>'
        st.markdown(scroll_html, unsafe_allow_html=True)


# ─── MAIN RENDER ─────────────────────────────────────────────────────────────

render_topbar()

if st.session_state.phase == "landing":
    render_landing()

else:
    # 3-column layout
    left, center, right = st.columns([280, 600, 300], gap="small")

    with left:
        render_left_panel()

    with center:
        render_center()

    with right:
        render_right_panel()