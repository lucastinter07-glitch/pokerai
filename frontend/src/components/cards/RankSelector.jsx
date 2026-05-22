import React from 'react';
import { RANKS, SUITS } from '../../utils/constants';
import { cardToString, isRed, suitSymbol } from '../../utils/cardUtils';

export default function RankSelector({ suit, onSelect, onBack, usedCards = [] }) {
  const suitObj  = SUITS.find((s) => s.key === suit);
  const suitCol  = suitObj ? suitObj.color : 'var(--text-primary)';
  const suitSym  = suitSymbol(suit);

  return (
    <>
      <div className="rank-header">
        <button className="picker-back-btn" onClick={onBack}>← Back</button>
        <span className="rank-suit-hint" style={{ color: suitCol }}>{suitSym}</span>
      </div>
      <div className="rank-grid">
        {RANKS.map((rank) => {
          const taken = usedCards.some(
            (c) => c && cardToString(c) === rank + suit
          );
          return (
            <button
              key={rank}
              className="rank-btn"
              style={taken ? {} : { color: isRed(suit) ? 'var(--suit-heart)' : 'var(--suit-spade)' }}
              onClick={() => !taken && onSelect(rank)}
              disabled={taken}
            >
              {rank}
            </button>
          );
        })}
      </div>
    </>
  );
}
