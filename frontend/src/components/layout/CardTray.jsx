import React from 'react';
import { useSession } from '../../context/SessionContext';
import CardDisplay from '../cards/CardDisplay';

export default function CardTray() {
  const { state } = useSession();
  const { currentScreen, holeCards, boardCards } = state;

  if (currentScreen === 'landing' || currentScreen === 'hand_complete') return null;

  const [h1, h2] = holeCards;
  const [b1, b2, b3, b4, b5] = boardCards;

  return (
    <div className="card-tray">
      <span className="card-tray__label">Cards</span>
      <CardDisplay card={h1} size="sm" />
      <CardDisplay card={h2} size="sm" />
      <div className="card-tray__divider" />
      <CardDisplay card={b1} size="sm" />
      <CardDisplay card={b2} size="sm" />
      <CardDisplay card={b3} size="sm" />
      <div className="card-tray__divider" />
      <CardDisplay card={b4} size="sm" />
      <div className="card-tray__divider" />
      <CardDisplay card={b5} size="sm" />
    </div>
  );
}
