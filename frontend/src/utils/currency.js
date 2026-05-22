export function dollarsToBB(dollars, bigBlind) {
  return bigBlind > 0 ? dollars / bigBlind : 0;
}

export function bbToDollars(bb, bigBlind) {
  return bb * bigBlind;
}

export function formatDollars(amount) {
  return `$${Number(amount).toFixed(2)}`;
}
