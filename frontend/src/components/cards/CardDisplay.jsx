import React from 'react';
import { suitSymbol, isRed } from '../../utils/cardUtils';

export default function CardDisplay({ card, size = 'md' }) {
  if (!card) {
    return (
      <div className={`card-display card-display--${size} card-display--empty`}>
        <span>?</span>
      </div>
    );
  }

  const color = isRed(card.suit)
    ? 'var(--suit-heart)'
    : 'var(--suit-spade)';

  return (
    <div
      className={`card-display card-display--${size} card-display--selected`}
      style={{ color }}
    >
      <span className="card-display__rank">{card.rank}</span>
      <span className="card-display__suit">{suitSymbol(card.suit)}</span>
    </div>
  );
}
