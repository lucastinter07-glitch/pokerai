import React from 'react';
import { ACTION_COLOR_MAP, ACTION_BG_MAP } from '../../utils/constants';

const DEFAULT_ACTIONS = [
  { key: 'fold',   label: 'Fold'  },
  { key: 'check',  label: 'Check' },
  { key: 'call',   label: 'Call'  },
  { key: 'raise',  label: 'Raise' },
  { key: 'all-in', label: 'All-in'},
];

export default function ActionSelector({ value, onChange, actions = DEFAULT_ACTIONS }) {
  return (
    <div className="action-selector">
      {actions.map((a) => {
        const active   = value === a.key;
        const labelKey = a.label.toUpperCase();
        const color = ACTION_COLOR_MAP[labelKey] || 'var(--text-secondary)';
        const bg    = ACTION_BG_MAP[labelKey]    || 'var(--surface-2)';
        return (
          <button
            key={a.key}
            className={`action-pill${active ? ' action-pill--active' : ''}`}
            style={active ? { background: bg, color, borderColor: 'transparent' } : {}}
            onClick={() => onChange(a.key)}
          >
            {a.label}
          </button>
        );
      })}
    </div>
  );
}
