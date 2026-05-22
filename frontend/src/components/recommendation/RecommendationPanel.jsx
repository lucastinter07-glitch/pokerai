import React from 'react';
import ActionBadge from './ActionBadge';
import EquityBar from './EquityBar';
import ReasoningBlock from './ReasoningBlock';
import { bbToDollars, formatDollars } from '../../utils/currency';

export default function RecommendationPanel({ result, loading, error, bigBlind = 0.50 }) {
  if (loading) {
    return (
      <div className="recommendation-panel">
        <span className="spinner" />
        <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Calculating…</span>
      </div>
    );
  }

  if (error) return <div className="error-box">{error}</div>;
  if (!result) return null;

  const { action, equity, pot_odds, bet_size, bet_tier, reasoning, sizing_reasoning } = result;

  return (
    <div className="recommendation-panel">
      <div className="recommendation-panel__top">
        <ActionBadge action={action} />
        <EquityBar equity={equity} potOdds={pot_odds} />
      </div>

      {(bet_size || bet_tier) && (
        <div className="recommendation-panel__meta">
          {bet_size && (
            <span>
              Bet{' '}
              <span className="recommendation-panel__bet">
                {formatDollars(bbToDollars(bet_size, bigBlind))}
              </span>
              <span style={{ color: 'var(--text-muted)' }}> ({bet_size}bb)</span>
            </span>
          )}
          {bet_tier && <span style={{ color: 'var(--text-muted)' }}>{bet_tier}</span>}
        </div>
      )}

      <ReasoningBlock reasoning={reasoning} sizingReasoning={sizing_reasoning} />
    </div>
  );
}
