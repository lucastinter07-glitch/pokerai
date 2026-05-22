import { useState, useCallback } from 'react';

export function useCardPicker(onComplete) {
  const [step,         setStep]         = useState('suit');
  const [selectedSuit, setSelectedSuit] = useState(null);

  const selectSuit = useCallback((suit) => {
    setSelectedSuit(suit);
    setStep('rank');
  }, []);

  const selectRank = useCallback((rank) => {
    if (selectedSuit && onComplete) {
      onComplete({ rank, suit: selectedSuit });
    }
    setStep('suit');
    setSelectedSuit(null);
  }, [selectedSuit, onComplete]);

  const reset = useCallback(() => {
    setStep('suit');
    setSelectedSuit(null);
  }, []);

  return { step, selectedSuit, selectSuit, selectRank, reset };
}
