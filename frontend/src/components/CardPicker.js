import React, { useState } from "react";
import "./CardPicker.css";

const RANKS = ["A","K","Q","J","T","9","8","7","6","5","4","3","2"];
const SUITS = [
  { key: "s", symbol: "♠", name: "Spades",   color: "#e8dfc8", isRed: false },
  { key: "h", symbol: "♥", name: "Hearts",   color: "#e05555", isRed: true  },
  { key: "d", symbol: "♦", name: "Diamonds", color: "#e05555", isRed: true  },
  { key: "c", symbol: "♣", name: "Clubs",    color: "#e8dfc8", isRed: false },
];

function formatCard(card) {
  if (!card) return null;
  const rank = card[0];
  const suit = card[1];
  const sym  = { s:"♠", h:"♥", d:"♦", c:"♣" }[suit];
  const red  = suit === "h" || suit === "d";
  return <span style={{ color: red ? "#e05555" : "#e8dfc8" }}>{rank}{sym}</span>;
}

export default function CardPicker({ slot, label, selected, usedCards, onSelect, onClear }) {
  const [open, setOpen]           = useState(false);
  const [pickedSuit, setPickedSuit] = useState(null);

  function openPicker() { setOpen(true); setPickedSuit(null); }
  function close()      { setOpen(false); setPickedSuit(null); }

  function pickCard(card) {
    onSelect(card);
    close();
  }

  return (
    <>
      {/* Slot button */}
      <button
        className={`card-slot ${selected ? "filled" : ""}`}
        onClick={selected ? onClear : openPicker}
      >
        {selected ? formatCard(selected) : <span className="plus-label">+{label}</span>}
      </button>

      {/* Modal overlay */}
      {open && (
        <div className="picker-overlay" onClick={close}>
          <div className="picker-modal" onClick={e => e.stopPropagation()}>

            {/* Step 1 — Suit selection */}
            {!pickedSuit && (
              <>
                <div className="picker-header">
                  <span className="picker-title">Choose a suit</span>
                  <button className="picker-close" onClick={close}>✕</button>
                </div>
                <div className="suit-grid">
                  {SUITS.map(s => {
                    const avail = RANKS.filter(r => !usedCards.includes(r+s.key)).length;
                    return (
                      <button
                        key={s.key}
                        className="suit-btn"
                        style={{ "--suit-color": s.color }}
                        onClick={() => setPickedSuit(s.key)}
                        disabled={avail === 0}
                      >
                        <span className="suit-symbol">{s.symbol}</span>
                        <span className="suit-name">{s.name}</span>
                        <span className="suit-avail">{avail} left</span>
                      </button>
                    );
                  })}
                </div>
              </>
            )}

            {/* Step 2 — Rank selection */}
            {pickedSuit && (() => {
              const s = SUITS.find(x => x.key === pickedSuit);
              return (
                <>
                  <div className="picker-header">
                    <button className="picker-back" onClick={() => setPickedSuit(null)}>
                      ← Back
                    </button>
                    <span className="picker-title" style={{ color: s.color }}>
                      {s.symbol} {s.name}
                    </span>
                    <button className="picker-close" onClick={close}>✕</button>
                  </div>
                  <div className="rank-grid">
                    {RANKS.map(rank => {
                      const card   = rank + pickedSuit;
                      const taken  = usedCards.includes(card);
                      return (
                        <button
                          key={rank}
                          className={`rank-btn ${taken ? "taken" : ""}`}
                          style={{ "--suit-color": s.color }}
                          onClick={() => !taken && pickCard(card)}
                          disabled={taken}
                        >
                          {rank}
                        </button>
                      );
                    })}
                  </div>
                </>
              );
            })()}

          </div>
        </div>
      )}
    </>
  );
}