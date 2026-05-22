import React from 'react';
import { SUITS, RANKS } from '../../utils/constants';
import { cardToString } from '../../utils/cardUtils';

export default function SuitSelector({ onSelect, usedCards = [] }) {
  return (
    <div className="suit-grid">
      {SUITS.map((s) => {
        const available = RANKS.filter(
          (r) => !usedCards.some((c) => c && cardToString(c) === r + s.key)
        ).length;
        return (
          <button
            key={s.key}
            className="suit-btn"
            style={{ color: s.color }}
            onClick={() => onSelect(s.key)}
            disabled={available === 0}
          >
            <span className="suit-btn__symbol">{s.symbol}</span>
            <span className="suit-btn__label">{s.label}</span>
            <span className="suit-btn__avail">{available} left</span>
          </button>
        );
      })}
    </div>
  );
}
