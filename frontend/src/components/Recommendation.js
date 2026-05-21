import React from "react";
import "./Recommendation.css";

export default function Recommendation({ result, toCall }) {
  const action = result.action.toLowerCase();

  return (
    <div className={`reco-wrap reco-${action}`}>
      <p className="reco-action">{result.action.toUpperCase()}</p>

      {result.bet_size != null && (
        <p className="reco-size">→ {result.bet_size}bb</p>
      )}

      <div className="reco-line" />

      <p className="reco-reasoning">{result.reasoning}</p>

      {result.sizing_reasoning && (
        <p className="reco-sizing-note">{result.sizing_reasoning}</p>
      )}

      <div className="reco-metrics">
        <div className="metric">
          <span className="metric-label">Equity</span>
          <span className="metric-value">
            {result.equity != null ? `${(result.equity * 100).toFixed(1)}%` : "—"}
          </span>
        </div>
        <div className="metric">
          <span className="metric-label">Pot Odds</span>
          <span className="metric-value">
            {toCall > 0 ? `${(result.pot_odds * 100).toFixed(1)}%` : "—"}
          </span>
        </div>
        <div className="metric">
          <span className="metric-label">Bet Size</span>
          <span className="metric-value">
            {result.bet_size != null ? `${result.bet_size}bb` : "—"}
          </span>
        </div>
      </div>
    </div>
  );
}