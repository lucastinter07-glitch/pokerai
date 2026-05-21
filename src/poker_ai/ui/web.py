import streamlit as st
from poker_ai.core.game_state import GameState, Position
from poker_ai.advisor.range_based import RangeBasedAdvisor
from poker_ai.utils.cards import format_card, RANKS, SUITS, SUIT_SYMBOLS

st.set_page_config(page_title="Poker AI Advisor", page_icon="♠", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500&display=swap');
.stApp {
    background: #0a1f16;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -10%, #1a4a30 0%, transparent 70%),
        radial-gradient(ellipse 60% 40% at 80% 80%, #0d2e1e 0%, transparent 60%);
}
.main .block-container { max-width: 720px; padding-top: 1.8rem; padding-bottom: 5rem; }
html, body, [class*="st-"], .stMarkdown, p, label, div { font-family: 'Inter', sans-serif; }
h1 {
    font-family: 'Cormorant Garamond', serif !important;
    font-weight: 700 !important; font-size: 2.6rem !important;
    color: #e8d5a3 !important; letter-spacing: 0.02em;
    border-bottom: 1px solid rgba(200,160,80,0.3);
    padding-bottom: 0.5rem; margin-bottom: 0.2rem !important;
}
h2 {
    font-family: 'Inter', sans-serif !important; font-weight: 500 !important;
    color: #8aab94 !important; font-size: 0.72rem !important;
    margin-top: 1.4rem !important; margin-bottom: 0.5rem !important;
    letter-spacing: 0.2em; text-transform: uppercase;
}
.stButton > button {
    background: rgba(255,255,255,0.04); color: #e8d5a3 !important;
    border: 1px solid rgba(200,160,80,0.25); border-radius: 10px;
    font-family: 'JetBrains Mono', monospace; font-weight: 700;
    font-size: 1.1rem; min-height: 52px; transition: all 0.15s ease;
}
.stButton > button:hover:not(:disabled) {
    background: rgba(200,160,80,0.12); border-color: rgba(200,160,80,0.6);
    transform: translateY(-1px);
}
.stButton > button:disabled { opacity: 0.18; cursor: not-allowed; }
.stButton > button[kind="primary"] {
    background: linear-gradient(160deg, #c8a050 0%, #a07030 100%);
    color: #0a1f16 !important; border: none;
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.2rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; min-height: 56px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(160deg, #deb060 0%, #b08040 100%);
    transform: translateY(-2px);
}
.stNumberInput input, .stSelectbox > div > div {
    background: rgba(255,255,255,0.05) !important; color: #e8d5a3 !important;
    border: 1px solid rgba(200,160,80,0.2) !important; border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
}
label { color: #8aab94 !important; font-size: 0.8rem !important; letter-spacing: 0.05em; }
[data-testid="stMetricValue"] {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 2rem !important; color: #c8a050 !important; font-weight: 700 !important;
}
[data-testid="stMetricLabel"] {
    color: #6a8a74 !important; text-transform: uppercase;
    letter-spacing: 0.15em; font-size: 0.68rem !important;
}
hr { border-color: rgba(200,160,80,0.15) !important; margin: 1.8rem 0 !important; }
.stCaption p { color: #6a8a74 !important; font-size: 0.8rem !important; }
.reco-wrap {
    background: linear-gradient(160deg, rgba(255,255,255,0.04) 0%, rgba(0,0,0,0.2) 100%);
    border: 1px solid rgba(200,160,80,0.3); border-radius: 12px;
    padding: 2rem 1.5rem 1.6rem; text-align: center; margin: 1rem 0;
}
.reco-action {
    font-family: 'Cormorant Garamond', serif; font-size: 3.4rem;
    font-weight: 700; letter-spacing: 0.15em; line-height: 1; margin: 0;
}
.reco-size {
    font-family: 'JetBrains Mono', monospace; font-size: 1.4rem;
    font-weight: 500; color: rgba(232,213,163,0.85); margin: 0.4rem 0 0;
}
.reco-raise,.reco-bet  { color: #7ec87e; }
.reco-call,.reco-check { color: #c8a050; }
.reco-fold             { color: #c87070; }
.reco-line { width: 40px; height: 1px; background: rgba(200,160,80,0.3); margin: 1rem auto 0.8rem; }
.reco-reasoning { font-style: italic; font-size: 0.9rem; color: #a8b8a0; line-height: 1.6; margin: 0; }
.reco-sizing-note { font-size: 0.8rem; color: #6a8a74; margin-top: 0.5rem; font-family: 'JetBrains Mono', monospace; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────

SLOTS = ["hole_1","hole_2","flop_1","flop_2","flop_3","turn","river"]

if "cards" not in st.session_state:
    st.session_state.cards = {s: None for s in SLOTS}

SUIT_META = {
    "s": ("♠", "Spades",   "#e8dfc8"),
    "h": ("♥", "Hearts",   "#d96060"),
    "d": ("♦", "Diamonds", "#d96060"),
    "c": ("♣", "Clubs",    "#e8dfc8"),
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def used_cards():
    return {c for c in st.session_state.cards.values() if c}

def hole_cards():
    return [c for c in (st.session_state.cards["hole_1"], st.session_state.cards["hole_2"]) if c]

def board_cards():
    out = []
    for s in ["flop_1","flop_2","flop_3","turn","river"]:
        c = st.session_state.cards[s]
        if not c: break
        out.append(c)
    return out

# ── Card picker dialog ─────────────────────────────────────────────────────────
# Key insight: NO st.rerun() inside the dialog.
# Instead we use a st.radio (suit selector) + conditional rank rendering,
# all in a single render pass. Widget changes update state without closing dialog.

@st.dialog("Select a card", width="small")
def card_picker(slot: str):
    taken = used_cards()
    if st.session_state.cards[slot]:
        taken.discard(st.session_state.cards[slot])

    # Suit selector using radio buttons styled as segmented control
    suit_options = ["♠  Spades", "♥  Hearts", "♦  Diamonds", "♣  Clubs"]
    suit_keys    = ["s", "h", "d", "c"]
    suit_colors  = ["#e8dfc8", "#d96060", "#d96060", "#e8dfc8"]

    st.markdown(
        "<p style='color:#8aab94;font-size:0.72rem;letter-spacing:0.2em;"
        "text-transform:uppercase;margin-bottom:0.4rem'>Suit</p>",
        unsafe_allow_html=True,
    )

    selected_label = st.radio(
        "suit_radio",
        options=suit_options,
        horizontal=True,
        label_visibility="collapsed",
        key=f"suit_radio_{slot}",
    )

    suit_idx  = suit_options.index(selected_label)
    suit      = suit_keys[suit_idx]
    sym, name, color = SUIT_META[suit]

    st.markdown(
        f"<p style='color:{color};font-family:JetBrains Mono;"
        f"font-size:0.85rem;font-weight:700;margin:0.8rem 0 0.4rem;"
        f"letter-spacing:0.05em'>{sym} {name} — choose rank</p>",
        unsafe_allow_html=True,
    )

    # Render ranks in a 4-column grid — fits on any phone screen
    # A K Q J / T 9 8 7 / 6 5 4 3 / 2
    rows = [RANKS[0:4], RANKS[4:8], RANKS[8:12], RANKS[12:13]]
    for row in rows:
        cols = st.columns(4)
        for i, rank in enumerate(row):
            card  = rank + suit
            taken_card = card in taken
            with cols[i]:
                lbl = rank if not taken_card else "·"
                if st.button(
                    lbl,
                    key=f"r_{card}_{slot}",
                    disabled=taken_card,
                    use_container_width=True,
                ):
                    st.session_state.cards[slot] = card
                    st.rerun()  # This closes dialog — which is correct, we're done

# ── Slot buttons ───────────────────────────────────────────────────────────────

def slot_btn(slot: str, label: str):
    card = st.session_state.cards[slot]
    display = format_card(card) if card else f"+ {label}"
    if st.button(display, key=f"s_{slot}", use_container_width=True):
        if card:
            st.session_state.cards[slot] = None
            st.rerun()
        else:
            card_picker(slot)

# ── Page ───────────────────────────────────────────────────────────────────────

st.markdown("<h1>Poker AI</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='color:#6a8a74;font-style:italic;margin-top:-0.3rem;"
    "font-size:0.9rem;'>Range-based advisor · No-Limit Hold'em</p>",
    unsafe_allow_html=True,
)

st.markdown("<h2>Your Hand</h2>", unsafe_allow_html=True)
h1, h2 = st.columns(2)
with h1: slot_btn("hole_1", "Card 1")
with h2: slot_btn("hole_2", "Card 2")

st.markdown("<h2>Board</h2>", unsafe_allow_html=True)
bc = st.columns(5)
for col, sl, lb in zip(bc,
    ["flop_1","flop_2","flop_3","turn","river"],
    ["Flop","Flop","Flop","Turn","River"]):
    with col: slot_btn(sl, lb)

r_col, _ = st.columns([1, 4])
with r_col:
    if st.button("↺ Reset", key="reset"):
        for s in SLOTS: st.session_state.cards[s] = None
        st.rerun()

st.markdown("<h2>Game Context</h2>", unsafe_allow_html=True)
g1, g2 = st.columns(2)
with g1:
    pos   = st.selectbox("Your position", ["UTG","MP","CO","BTN","SB","BB"], index=3)
    stack = st.number_input("Stack (BB)", min_value=1.0, value=100.0, step=10.0)
with g2:
    pot     = st.number_input("Pot (BB)",     min_value=0.0, value=1.5,  step=0.5)
    to_call = st.number_input("To call (BB)", min_value=0.0, value=0.0,  step=0.5)

st.markdown("<h2>Opponent</h2>", unsafe_allow_html=True)
st.caption("Specify who's betting to model their range accurately.")
villain_raw = st.selectbox(
    "Villain position",
    ["(none — opening or no bet)", "UTG","MP","CO","BTN","SB","BB"], index=0
)
villain_pos = Position(villain_raw) if villain_raw != "(none — opening or no bet)" else None

st.divider()

if st.button("Get Recommendation", type="primary", use_container_width=True):
    hole  = hole_cards()
    board = board_cards()

    if len(hole) != 2:
        st.error("Select both hole cards first.")
        st.stop()
    if len(board) not in (0, 3, 4, 5):
        st.error(f"Board needs 0, 3, 4, or 5 cards — got {len(board)}.")
        st.stop()

    try:
        state = GameState(
            hole_cards=hole, position=Position(pos), stack=stack,
            board=board, pot=pot, to_call=to_call, villain_position=villain_pos,
        )
        with st.spinner("Calculating..."):
            res = RangeBasedAdvisor(iterations=2000).recommend(state)

        action      = res["action"].lower()
        action_lbl  = res["action"].upper()
        reasoning   = res.get("reasoning", "")
        sizing_note = res.get("sizing_reasoning", "")
        bet_size    = res.get("bet_size")
        equity      = res.get("equity")
        pot_odds_v  = res.get("pot_odds", 0)

        size_html = f'<p class="reco-size">→ {bet_size}bb</p>' if bet_size is not None else ""
        sn_html   = f'<p class="reco-sizing-note">{sizing_note}</p>' if sizing_note else ""

        st.markdown(
            '<div class="reco-wrap">'
            f'<p class="reco-action reco-{action}">{action_lbl}</p>'
            f'{size_html}'
            '<div class="reco-line"></div>'
            f'<p class="reco-reasoning">{reasoning}</p>'
            f'{sn_html}'
            '</div>',
            unsafe_allow_html=True,
        )

        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Equity",   f"{equity:.1%}"     if equity   is not None else "—")
        with m2: st.metric("Pot Odds", f"{pot_odds_v:.1%}" if to_call > 0           else "—")
        with m3: st.metric("Bet Size", f"{bet_size}bb"     if bet_size is not None  else "—")

    except ValueError as e:
        st.error(str(e))