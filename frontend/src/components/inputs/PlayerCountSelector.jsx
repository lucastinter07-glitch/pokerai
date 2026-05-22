import React from 'react';

export default function PlayerCountSelector({ value, onChange }) {
  return (
    <div className="stepper">
      <button
        className="stepper__btn"
        onClick={() => onChange(Math.max(2, value - 1))}
        disabled={value <= 2}
      >
        −
      </button>
      <span className="stepper__value">{value}</span>
      <button
        className="stepper__btn"
        onClick={() => onChange(Math.min(9, value + 1))}
        disabled={value >= 9}
      >
        +
      </button>
    </div>
  );
}
