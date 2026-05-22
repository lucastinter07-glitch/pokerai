import React from 'react';

export default function EquityBar({ equity, potOdds }) {
  const equityPct  = Math.round((equity  || 0) * 100);
  const potOddsPct = Math.round((potOdds || 0) * 100);
  const winning    = equityPct >= potOddsPct;
  const fillColor  = winning ? 'var(--action-check)' : 'var(--action-fold)';

  return (
    <div className="equity-bar-wrap">
      <div className="equity-bar-labels">
        <span style={{ color: fillColor }}>Equity {equityPct}%</span>
        <span>Need {potOddsPct}%</span>
      </div>
      <div className="equity-bar-track">
        <div
          className="equity-bar-fill"
          style={{ width: `${Math.min(100, equityPct)}%`, background: fillColor }}
        />
        {potOddsPct > 0 && (
          <div
            className="equity-bar-marker"
            style={{ left: `${Math.min(100, potOddsPct)}%` }}
          />
        )}
      </div>
    </div>
  );
}
