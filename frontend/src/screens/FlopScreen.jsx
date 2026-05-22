import React, { useState } from 'react';
import { useSession } from '../context/SessionContext';
import { useRecommendation } from '../hooks/useRecommendation';
import ScreenWrapper from '../components/layout/ScreenWrapper';
import PositionSelector from '../components/inputs/PositionSelector';
import ActionSelector from '../components/inputs/ActionSelector';
import ActionFacedInfo from '../components/inputs/ActionFacedInfo';
import VillainPositionInfo from '../components/inputs/VillainPositionInfo';
import PotSizeInput from '../components/inputs/PotSizeInput';
import CardPicker from '../components/cards/CardPicker';
import RecommendationModal from '../components/recommendation/RecommendationModal';
import { dollarsToBB, bbToDollars } from '../utils/currency';

export default function FlopScreen() {
  const {
    state,
    setBoardCard, setVillainPos, setPotSize,
    setStreetAction, setRecommendation, advanceStreet, goBack,
  } = useSession();

  const { holeCards, boardCards, position, villainPos, potSize, currentStack, bigBlind, numPlayers } = state;
  const [actionFaced, setActionFaced] = useState(null);
  const [showModal,   setShowModal]   = useState(false);

  const { recommend, result, loading, error, clear } = useRecommendation();

  const allCards  = [...holeCards, ...boardCards].filter(Boolean);
  const flopDone  = boardCards[0] && boardCards[1] && boardCards[2];

  function buildGameState() {
    return {
      holeCards,
      boardCards:  boardCards.slice(0, 3),
      position:    position || 'BTN',
      villainPos,
      potSize,
      actionFaced,
      stackSize:   currentStack,
      bigBlind,
      numPlayers,
    };
  }

  async function handleNextStreet() {
    setShowModal(true);
    await recommend(buildGameState());
  }

  function handleConfirm() {
    if (result) setRecommendation('flop', result);
    if (actionFaced) setStreetAction('flop', actionFaced, potSize);
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
    <ScreenWrapper title="Flop">
      <button className="back-btn" onClick={goBack}>← Back</button>

      <div className="section-label">Flop Cards</div>
      <div className="card-row">
        {[0, 1, 2].map((i) => (
          <CardPicker
            key={i}
            label={`Flop ${i + 1}`}
            existingCard={boardCards[i]}
            usedCards={allCards}
            onCardSelected={(c) => setBoardCard(i, c)}
          />
        ))}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
        <div className="section-label">Villain Position</div>
        <VillainPositionInfo />
      </div>
      <PositionSelector value={villainPos} onChange={setVillainPos} numPlayers={numPlayers} />

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
          disabled={!flopDone}
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
          stayLabel="Stay on Flop"
          bigBlind={bigBlind}
        />
      )}
    </ScreenWrapper>
  );
}
