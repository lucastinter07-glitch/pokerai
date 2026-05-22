import React from 'react';

export default function NumberInput({ value, onChange, label, placeholder, suffix, prefix }) {
  return (
    <div className="number-input-wrap">
      {label && <span className="number-input-label">{label}</span>}
      <div className="number-input-field">
        {prefix && <span className="number-input-prefix">{prefix}</span>}
        <input
          type="number"
          inputMode="decimal"
          value={value === 0 ? '' : value}
          placeholder={placeholder || '0'}
          onChange={(e) => {
            const v = parseFloat(e.target.value);
            onChange(isNaN(v) ? 0 : v);
          }}
        />
        {suffix && <span className="number-input-suffix">{suffix}</span>}
      </div>
    </div>
  );
}
