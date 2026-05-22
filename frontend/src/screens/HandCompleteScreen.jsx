import React, { useState } from 'react';
import { useSession } from '../context/SessionContext';
import ScreenWrapper from '../components/layout/ScreenWrapper';
import NumberInput from '../components/inputs/NumberInput';
import { ACTION_COLOR_MAP } from '../utils/constants';
import { bbToDollars, dollarsToBB, formatDollars } from '../utils/currency';

export default function HandCompleteScreen() {
  const { state, startNextHand } = useSession();
  const { handSummary, handHistory, currentStack, estimatedStack, bigBlind, handCount } = state;

  const estimatedDollars = bbToDollars(estimatedStack ?? currentStack, bigBlind);
  const [confirmedDollars, setConfirmedDollars] = useState(() => estimatedDollars);

  function handleNextHand() {
    const stackBB = dollarsToBB(confirmedDollars || estimatedDollars, bigBlind);
    startNextHand(stackBB);
  }

  return (
    <ScreenWrapper title="Hand Complete">
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 'var(--space-3)' }}>
        <span className="hand-complete-header">Hand Complete</span>
        {handCount > 0 && <span className="hand-count">#{handCount}</span>}
      </div>

      <div className="section-label">Decisions</div>
      <div className="summary-table">
        {handSummary.length === 0 && (
          <div style={{ color: 'var(--text-muted)', fontSize: '12px' }}>No actions recorded</div>
        )}
        {handSummary.map((row, i) => {
          const recAction = row.recommendation?.action?.toUpperCase();
          const recColor  = recAction ? (ACTION_COLOR_MAP[recAction] || 'var(--text-secondary)') : 'var(--text-muted)';
          return (
            <div key={i} className="summary-row">
              <span className="summary-row__street">{row.street}</span>
              <span className="summary-row__action">{row.action || '—'}</span>
              <span className="summary-row__rec" style={{ color: recColor }}>
                {recAction || '—'}
              </span>
            </div>
          );
        })}
      </div>

      <div className="section-label">Stack Update</div>
      <p style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: 'var(--space-1)' }}>
        Estimated: <span style={{ color: 'var(--text-secondary)' }}>{formatDollars(estimatedDollars)}</span>
        <span style={{ color: 'var(--text-muted)', marginLeft: 'var(--space-2)', fontSize: '10px' }}>(rough — confirm below)</span>
      </p>
      <NumberInput
        label="Confirm Stack"
        value={confirmedDollars}
        onChange={setConfirmedDollars}
        prefix="$"
        placeholder={estimatedDollars.toFixed(2)}
      />

      <button className="btn-primary" onClick={handleNextHand}>
        Start Next Hand
      </button>

      {handHistory.length > 0 && (
        <>
          <div className="section-label">Hand History</div>
          <div className="hand-history-list">
            {[...handHistory].reverse().map((h) => (
              <div key={h.handNum} className="hand-history-entry">
                <span className="hand-history-entry__num">#{h.handNum}</span>
                <div className="hand-history-entry__streets">
                  {h.summary.length === 0 ? (
                    <span style={{ color: 'var(--text-muted)', fontSize: '10px' }}>no actions</span>
                  ) : (
                    h.summary.map((row) => {
                      const recAction = row.recommendation?.action?.toLowerCase();
                      const matched   = recAction === row.action;
                      const color     = ACTION_COLOR_MAP[row.action?.toUpperCase()] || 'var(--text-muted)';
                      return (
                        <span key={row.street} className="hand-history-pill" style={{ color }}>
                          {row.street.slice(0, 3).toUpperCase()}·{row.action?.toUpperCase()}
                          {recAction && (
                            <span style={{ color: matched ? 'var(--action-check)' : 'var(--action-fold)', marginLeft: '2px' }}>
                              {matched ? '✓' : '✗'}
                            </span>
                          )}
                        </span>
                      );
                    })
                  )}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </ScreenWrapper>
  );
}
