import React, { useState } from 'react';
import { useSession } from '../context/SessionContext';
import ScreenWrapper from '../components/layout/ScreenWrapper';
import NumberInput from '../components/inputs/NumberInput';
import PlayerCountSelector from '../components/inputs/PlayerCountSelector';
import { dollarsToBB } from '../utils/currency';

export default function LandingScreen() {
  const { startSession } = useSession();

  const [smallBlind,   setSmallBlind]   = useState(0.25);
  const [bigBlind,     setBigBlind]     = useState(0.50);
  const [numPlayers,   setNumPlayers]   = useState(6);
  const [stackDollars, setStackDollars] = useState(50);

  function handleStart() {
    if (!bigBlind || bigBlind <= 0 || !stackDollars || stackDollars <= 0) return;
    startSession({ smallBlind, bigBlind, numPlayers, startingStack: dollarsToBB(stackDollars, bigBlind) });
  }

  return (
    <ScreenWrapper isLanding>
      <div className="landing-brand">
        <div className="landing-title">NEXBET AI</div>
        <div className="landing-subtitle">Decision Engine</div>
      </div>

      <div className="landing-form">
        {/* Blind row: fixed 320px max-width, centered */}
        <div style={{
          display:       'grid',
          gridTemplateColumns: '1fr 1fr',
          gap:           'var(--space-3)',
          maxWidth:      '320px',
          width:         '100%',
          margin:        '0 auto',
        }}>
          <NumberInput
            label="Small Blind"
            value={smallBlind}
            onChange={setSmallBlind}
            prefix="$"
            placeholder="0.25"
          />
          <NumberInput
            label="Big Blind"
            value={bigBlind}
            onChange={setBigBlind}
            prefix="$"
            placeholder="0.50"
          />
        </div>

        <div>
          <div className="field-label-row">Players</div>
          <PlayerCountSelector value={numPlayers} onChange={setNumPlayers} />
        </div>

        <NumberInput
          label="Starting Stack"
          value={stackDollars}
          onChange={setStackDollars}
          prefix="$"
          placeholder="50.00"
        />

        <div>
          <div className="field-label-row">
            Username
            <span className="badge-soon">Coming soon</span>
          </div>
          <div className="input-disabled">Username</div>
        </div>

        <button
          className="btn-primary"
          onClick={handleStart}
          disabled={!bigBlind || bigBlind <= 0 || !stackDollars || stackDollars <= 0}
          style={{ marginTop: 'var(--space-2)' }}
        >
          Start Session
        </button>
      </div>
    </ScreenWrapper>
  );
}
