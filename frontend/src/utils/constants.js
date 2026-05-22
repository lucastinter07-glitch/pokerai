export const API_BASE_URL = 'http://192.168.1.31:8000';

export const SUITS = [
  { key: 's', symbol: '♠', label: 'Spades',   color: 'var(--suit-spade)'   },
  { key: 'h', symbol: '♥', label: 'Hearts',   color: 'var(--suit-heart)'   },
  { key: 'd', symbol: '♦', label: 'Diamonds', color: 'var(--suit-diamond)' },
  { key: 'c', symbol: '♣', label: 'Clubs',    color: 'var(--suit-club)'    },
];

export const RANKS = ['A','K','Q','J','T','9','8','7','6','5','4','3','2'];

export const POSITIONS = ['BTN','CO','HJ','LJ','MP','UTG','SB','BB'];

export const STREETS = {
  LANDING:       'landing',
  PREFLOP:       'preflop',
  FLOP:          'flop',
  TURN:          'turn',
  RIVER:         'river',
  HAND_COMPLETE: 'hand_complete',
};

export const STREET_ORDER = ['landing','preflop','flop','turn','river','hand_complete'];

export const ACTION_COLOR_MAP = {
  FOLD:    'var(--action-fold)',
  CHECK:   'var(--action-check)',
  CALL:    'var(--action-call)',
  BET:     'var(--action-raise)',
  RAISE:   'var(--action-raise)',
  'ALL-IN':'var(--action-allin)',
};

export const ACTION_BG_MAP = {
  FOLD:    'var(--action-fold-dim)',
  CHECK:   'var(--action-check-dim)',
  CALL:    'var(--action-call-dim)',
  BET:     'var(--action-raise-dim)',
  RAISE:   'var(--action-raise-dim)',
  'ALL-IN':'var(--action-allin-dim)',
};
