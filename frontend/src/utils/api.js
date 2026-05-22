import { API_BASE_URL } from './constants';
import { cardToString } from './cardUtils';
import { toBackendPosition } from './positions';

export async function getRecommendation(gameState) {
  const holeCards  = (gameState.holeCards  || []).map(cardToString).filter(Boolean);
  const boardCards = (gameState.boardCards || []).map(cardToString).filter(Boolean);

  const actionFaced = (gameState.actionFaced || '').toLowerCase();
  const toCall = (actionFaced === 'call' || actionFaced === 'raise')
    ? (gameState.potSize || 0)
    : 0;

  const body = {
    hole_cards:       holeCards,
    position:         toBackendPosition(gameState.position || 'BTN'),
    stack:            gameState.stackSize || 100,
    effective_stack:  gameState.stackSize || 100,
    board:            boardCards,
    pot:              gameState.potSize   || 0,
    to_call:          toCall,
    villain_position: gameState.villainPos
      ? toBackendPosition(gameState.villainPos)
      : null,
  };

  const res = await fetch(`${API_BASE_URL}/recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => String(res.status));
    throw new Error(`Server error ${res.status}: ${text}`);
  }

  return res.json();
}
