import React, { useState, useCallback } from 'react';
import CardDisplay from './CardDisplay';
import SuitSelector from './SuitSelector';
import RankSelector from './RankSelector';
import { useCardPicker } from '../../hooks/useCardPicker';

export default function CardPicker({ onCardSelected, label, existingCard, usedCards = [] }) {
  const [open, setOpen] = useState(false);

  const handleComplete = useCallback((card) => {
    onCardSelected(card);
    setOpen(false);
  }, [onCardSelected]);

  const { step, selectedSuit, selectSuit, selectRank, reset } = useCardPicker(handleComplete);

  function handleClear() {
    onCardSelected(null);
  }

  function handleClose() {
    setOpen(false);
    reset();
  }

  if (existingCard) {
    return (
      <div className="card-picker-filled">
        <CardDisplay card={existingCard} size="md" />
        <button className="card-clear-btn" onClick={handleClear} aria-label="Clear card">×</button>
      </div>
    );
  }

  return (
    <>
      <button className="card-slot-btn" onClick={() => setOpen(true)}>
        <span className="card-slot-btn__plus">+</span>
        <span>{label}</span>
      </button>

      {open && (
        <div className="card-picker-overlay" onClick={handleClose}>
          <div className="card-picker-sheet" onClick={(e) => e.stopPropagation()}>
            <div className="card-picker-sheet__header">
              <span className="card-picker-sheet__title">
                {step === 'suit' ? 'Choose suit' : 'Choose rank'}
              </span>
              <button className="card-picker-sheet__close" onClick={handleClose}>✕</button>
            </div>

            {step === 'suit' ? (
              <SuitSelector onSelect={selectSuit} usedCards={usedCards} />
            ) : (
              <RankSelector
                suit={selectedSuit}
                onSelect={selectRank}
                onBack={reset}
                usedCards={usedCards}
              />
            )}
          </div>
        </div>
      )}
    </>
  );
}
