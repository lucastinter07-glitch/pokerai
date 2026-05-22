import React from 'react';
import { ACTION_COLOR_MAP, ACTION_BG_MAP } from '../../utils/constants';

export default function ActionBadge({ action }) {
  const key   = (action || '').toUpperCase();
  const color = ACTION_COLOR_MAP[key] || 'var(--text-primary)';
  const bg    = ACTION_BG_MAP[key]    || 'var(--surface-3)';

  return (
    <span
      className="action-badge"
      style={{ color, background: bg }}
    >
      {action}
    </span>
  );
}
