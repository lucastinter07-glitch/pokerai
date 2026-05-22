import React from 'react';
import NumberInput from './NumberInput';

const INCREMENTS = [1, 5, 10];

export default function PotSizeInput({ valueDollars, onChangeDollars }) {
  function adjust(delta) {
    onChangeDollars(Math.max(0, (valueDollars || 0) + delta));
  }

  return (
    <div className="pot-size-input">
      <NumberInput
        label="Pot Size"
        value={valueDollars || ''}
        onChange={onChangeDollars}
        prefix="$"
        placeholder="0.00"
      />
      <div className="pot-increments">
        {INCREMENTS.slice().reverse().map((n) => (
          <button key={`-${n}`} className="pot-inc-btn pot-inc-btn--neg" onClick={() => adjust(-n)}>
            −${n}
          </button>
        ))}
        {INCREMENTS.map((n) => (
          <button key={`+${n}`} className="pot-inc-btn pot-inc-btn--pos" onClick={() => adjust(n)}>
            +${n}
          </button>
        ))}
      </div>
    </div>
  );
}
