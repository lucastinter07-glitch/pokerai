export function cardToString(card) {
  if (!card) return null;
  return `${card.rank}${card.suit}`;
}

export function suitSymbol(suitKey) {
  return { s: '♠', h: '♥', d: '♦', c: '♣' }[suitKey] || '';
}

export function suitColor(suitKey) {
  return {
    s: 'var(--suit-spade)',
    c: 'var(--suit-club)',
    h: 'var(--suit-heart)',
    d: 'var(--suit-diamond)',
  }[suitKey] || 'var(--text-primary)';
}

export function isRed(suitKey) {
  return suitKey === 'h' || suitKey === 'd';
}
