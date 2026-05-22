import React, { useState } from 'react';
import { useSession } from '../context/SessionContext';
import { useRecommendation } from '../hooks/useRecommendation';
import ScreenWrapper from '../components/layout/ScreenWrapper';
import ActionSelector from '../components/inputs/ActionSelector';
import ActionFacedInfo from '../components/inputs/ActionFacedInfo';
import PotSizeInput from '../components/inputs/PotSizeInput';
import CardPicker from '../components/cards/CardPicker';
import RecommendationModal from '../components/recommendation/RecommendationModal';
import { dollarsToBB, bbToDollars } from '../utils/currency';

export default function RiverScreen() {
  const {
    state,
    setBoardCard, setPotSize,
    setStreetAction, setRecommendation, endHand, goBack,
  } = useSession();

  const { holeCards, boardCards, position, villainPos, potSize, currentStack, bigBlind, numPlayers } = state;
  const [actionFaced, setActionFaced] = useState(null);
  const [showModal,   setShowModal]   = useState(false);

  const { recommend, result, loading, error, clear } = useRecommendation();

  const allCards  = [...holeCards, ...boardCards].filter(Boolean);
  const riverDone = !!boardCards[4];

  function buildGameState() {
    return {
      holeCards,
      boardCards:  boardCards.slice(0, 5),
      position:    position || 'BTN',
      villainPos,
      potSize,
      actionFaced,
      stackSize:   currentStack,
      bigBlind,
      numPlayers,
    };
  }

  async function handleEndHand() {
    setShowModal(true);
    await recommend(buildGameState());
  }

  function handleConfirm() {
    if (result) setRecommendation('river', result);
    if (actionFaced) setStreetAction('river', actionFaced, potSize);
    setShowModal(false);
    clear();
    endHand();
  }

  function handleStay() {
    setShowModal(false);
    clear();
  }

  async function handleRetry() {
    clear();
    await recommend(buildGameState());
  }

  return (
    <ScreenWrapper title="River">
      <button className="back-btn" onClick={goBack}>← Back</button>

      <div className="section-label">River Card</div>
      <CardPicker
        label="River"
        existingCard={boardCards[4]}
        usedCards={allCards}
        onCardSelected={(c) => setBoardCard(4, c)}
      />

      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
        <div className="section-label">Action Faced</div>
        <ActionFacedInfo />
      </div>
      <ActionSelector value={actionFaced} onChange={setActionFaced} />

      <PotSizeInput
        valueDollars={bbToDollars(potSize, bigBlind)}
        onChangeDollars={(dollars) => setPotSize(dollarsToBB(dollars, bigBlind))}
      />

      <div style={{ marginTop: 'auto' }}>
        <button
          className="btn-primary"
          onClick={handleEndHand}
          disabled={!riverDone}
        >
          End Hand
        </button>
      </div>

      {showModal && (
        <RecommendationModal
          result={result}
          error={error}
          loading={loading}
          onConfirm={handleConfirm}
          onStay={handleStay}
          onRetry={handleRetry}
          confirmLabel="Confirm & End Hand"
          stayLabel="Stay on River"
          bigBlind={bigBlind}
        />
      )}
    </ScreenWrapper>
  );
}
