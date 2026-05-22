import React, { useState } from 'react';

export default function ReasoningBlock({ reasoning, sizingReasoning, defaultExpanded = false }) {
  const [expanded, setExpanded] = useState(defaultExpanded);

  if (!reasoning) return null;

  return (
    <div className="reasoning-block">
      <button
        className="reasoning-block__toggle"
        onClick={() => setExpanded((v) => !v)}
      >
        <span>Reasoning</span>
        <span>{expanded ? '▲' : '▼'}</span>
      </button>
      {expanded && (
        <div className="reasoning-block__content inner-scroll">
          <p>{reasoning}</p>
          {sizingReasoning && (
            <p style={{ marginTop: 'var(--space-2)', color: 'var(--text-muted)' }}>
              {sizingReasoning}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
