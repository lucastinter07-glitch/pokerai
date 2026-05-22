export function applyAction(currentStack, action, amountBB) {
  switch (action) {
    case 'call':
    case 'raise':
    case 'all-in':
      return Math.max(0, currentStack - (amountBB || 0));
    case 'check':
    case 'fold':
    default:
      return currentStack;
  }
}

export function formatStack(bb) {
  return `${Math.round(bb * 10) / 10}bb`;
}
