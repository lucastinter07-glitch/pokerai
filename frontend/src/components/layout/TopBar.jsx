import React from 'react';
import { useSession } from '../../context/SessionContext';
import { formatStack } from '../../utils/stackTracker';

export default function TopBar() {
  const { state, resetHand, goToLanding } = useSession();
  const { currentScreen, currentStack, sessionPnL, bigBlind } = state;

  if (currentScreen === 'landing') return null;

  const inActiveHand = currentScreen !== 'hand_complete';

  function handleHome() {
    if (!inActiveHand) {
      goToLanding();
      return;
    }
    if (window.confirm('Return to setup? Current hand progress will be lost.')) {
      goToLanding();
    }
  }

  function handleNewHand() {
    if (!inActiveHand) {
      resetHand();
      return;
    }
    if (window.confirm('Start a new hand? Current hand progress will be lost.')) {
      resetHand();
    }
  }

  const pnlAbs    = Math.abs(sessionPnL).toFixed(2);
  const pnlSign   = sessionPnL >= 0 ? '+' : '-';
  const pnlColor  = sessionPnL > 0 ? 'var(--action-check)' : sessionPnL < 0 ? 'var(--action-fold)' : 'var(--text-muted)';

  return (
    <div className="top-bar">
      <button className="top-bar__brand" onClick={handleHome}>
        NEXBET AI
      </button>
      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)' }}>
        {sessionPnL !== 0 && (
          <span className="top-bar__pnl" style={{ color: pnlColor }}>
            {pnlSign}${pnlAbs}
          </span>
        )}
        <span className="top-bar__stack">
          ↕ <span>{formatStack(currentStack)}</span>
        </span>
      </div>
      <button className="top-bar__new-hand" onClick={handleNewHand}>
        New Hand
      </button>
    </div>
  );
}
