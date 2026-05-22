import React from 'react';
import ActionBadge from './ActionBadge';
import EquityBar from './EquityBar';
import ReasoningBlock from './ReasoningBlock';
import { bbToDollars, formatDollars } from '../../utils/currency';

export default function RecommendationModal({
  result,
  error,
  loading,
  onConfirm,
  onStay,
  onRetry,
  confirmLabel = 'Confirm & Continue',
  stayLabel    = 'Stay on this street',
  bigBlind     = 0.50,
}) {
  return (
    <div className="rec-modal-overlay">
      <div className="rec-modal">

        {loading && (
          <div className="rec-modal__loading">
            <span className="spinner-lg" />
            <p className="rec-modal__loading-text">Calculating best action…</p>
          </div>
        )}

        {!loading && error && (
          <div className="rec-modal__error">
            <p className="rec-modal__error-text">{error}</p>
            <button className="btn-secondary" onClick={onRetry}>Try Again</button>
            <button className="btn-ghost" onClick={onStay}>{stayLabel}</button>
          </div>
        )}

        {!loading && !error && result && (
          <>
            <div className="rec-modal__top">
              <ActionBadge action={result.action} />
              <EquityBar equity={result.equity} potOdds={result.pot_odds} />
            </div>

            {(result.bet_size || result.bet_tier) && (
              <div className="rec-modal__bet">
                {result.bet_size && (
                  <span>
                    Bet{' '}
                    <strong className="rec-modal__bet-amount">
                      {formatDollars(bbToDollars(result.bet_size, bigBlind))}
                    </strong>
                    <span className="rec-modal__bet-bb"> ({result.bet_size}bb)</span>
                  </span>
                )}
                {result.bet_tier && (
                  <span className="rec-modal__tier">{result.bet_tier}</span>
                )}
              </div>
            )}

            <ReasoningBlock
              reasoning={result.reasoning}
              sizingReasoning={result.sizing_reasoning}
              defaultExpanded
            />

            <div className="rec-modal__actions">
              <button className="btn-primary" onClick={onConfirm}>{confirmLabel}</button>
              <button className="btn-ghost" onClick={onStay}>{stayLabel}</button>
            </div>
          </>
        )}

      </div>
    </div>
  );
}
