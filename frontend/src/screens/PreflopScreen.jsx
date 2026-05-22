import React, { useState } from 'react';
import { useSession } from '../context/SessionContext';
import { useRecommendation } from '../hooks/useRecommendation';
import ScreenWrapper from '../components/layout/ScreenWrapper';
import PositionSelector from '../components/inputs/PositionSelector';
import ActionSelector from '../components/inputs/ActionSelector';
import ActionFacedInfo from '../components/inputs/ActionFacedInfo';
import PotSizeInput from '../components/inputs/PotSizeInput';
import CardPicker from '../components/cards/CardPicker';
import RecommendationModal from '../components/recommendation/RecommendationModal';
import { dollarsToBB, bbToDollars } from '../utils/currency';

export default function PreflopScreen() {
  const {
    state,
    setHoleCard, setPosition, setPotSize,
    setStreetAction, setRecommendation, advanceStreet, goBack,
  } = useSession();

  const { holeCards, boardCards, position, potSize, currentStack, bigBlind, numPlayers } = state;
  const [actionFaced,  setActionFaced]  = useState(null);
  const [showModal,    setShowModal]    = useState(false);

  const { recommend, result, loading, error, clear } = useRecommendation();

  const allCards  = [...holeCards, ...boardCards].filter(Boolean);
  const bothCards = holeCards[0] && holeCards[1];

  function buildGameState() {
    return {
      holeCards,
      boardCards:   [],
      position:     position || 'BTN',
      villainPos:   null,
      potSize,
      actionFaced,
      stackSize:    currentStack,
      bigBlind,
      numPlayers,
    };
  }

  async function handleNextStreet() {
    setShowModal(true);
    await recommend(buildGameState());
  }

  function handleConfirm() {
    if (result) setRecommendation('preflop', result);
    if (actionFaced) setStreetAction('preflop', actionFaced, potSize);
    setShowModal(false);
    clear();
    advanceStreet();
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
    <ScreenWrapper title="Preflop">
      <button className="back-btn" onClick={goBack}>← Setup</button>

      <div className="section-label">Your Position</div>
      <PositionSelector value={position} onChange={setPosition} numPlayers={numPlayers} />

      <div className="section-label">Hole Cards</div>
      <div className="card-row">
        <CardPicker
          label="Card 1"
          existingCard={holeCards[0]}
          usedCards={allCards}
          onCardSelected={(c) => setHoleCard(0, c)}
        />
        <CardPicker
          label="Card 2"
          existingCard={holeCards[1]}
          usedCards={allCards}
          onCardSelected={(c) => setHoleCard(1, c)}
        />
      </div>

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
          onClick={handleNextStreet}
          disabled={!bothCards}
        >
          Next Street →
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
          confirmLabel="Confirm & Continue"
          stayLabel="Stay on Preflop"
          bigBlind={bigBlind}
        />
      )}
    </ScreenWrapper>
  );
}
