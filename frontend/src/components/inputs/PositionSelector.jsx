import React, { useEffect } from 'react';
import { getPositionsForPlayerCount } from '../../utils/positions';

export default function PositionSelector({ value, onChange, numPlayers = 6 }) {
  const positions = getPositionsForPlayerCount(numPlayers);

  // Clear selection if the chosen position is no longer valid for this player count
  useEffect(() => {
    if (value && !positions.includes(value)) {
      onChange(null);
    }
  }, [numPlayers]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="position-selector">
      {positions.map((pos) => (
        <button
          key={pos}
          className={`position-pill${value === pos ? ' position-pill--active' : ''}`}
          onClick={() => onChange(pos)}
        >
          {pos}
        </button>
      ))}
    </div>
  );
}
