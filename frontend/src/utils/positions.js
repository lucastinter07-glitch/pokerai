export function getPositionsForPlayerCount(n) {
  switch (n) {
    case 2:  return ['BTN/SB', 'BB'];
    case 3:  return ['BTN', 'SB', 'BB'];
    case 4:  return ['BTN', 'CO', 'SB', 'BB'];
    case 5:  return ['BTN', 'CO', 'HJ', 'SB', 'BB'];
    case 6:  return ['BTN', 'CO', 'HJ', 'MP', 'SB', 'BB'];
    case 7:  return ['BTN', 'CO', 'HJ', 'LJ', 'MP', 'SB', 'BB'];
    case 8:  return ['BTN', 'CO', 'HJ', 'LJ', 'MP', 'UTG', 'SB', 'BB'];
    case 9:  return ['BTN', 'CO', 'HJ', 'LJ', 'MP', 'UTG+1', 'UTG', 'SB', 'BB'];
    default: return ['BTN', 'CO', 'HJ', 'MP', 'SB', 'BB'];
  }
}

// Backend Position enum accepts: UTG, MP, CO, BTN, SB, BB
// Map any frontend-only positions to the nearest backend equivalent.
const BACKEND_MAP = {
  'BTN/SB': 'BTN',  // heads-up button/SB → BTN
  'HJ':     'MP',   // hijack → middle position
  'LJ':     'MP',   // lojack → middle position
  'UTG+1':  'UTG',  // utg+1 → UTG
};

export function toBackendPosition(pos) {
  return BACKEND_MAP[pos] ?? pos;
}
