import React, { createContext, useContext, useReducer } from 'react';

const STREET_ORDER = ['landing','preflop','flop','turn','river','hand_complete'];

const blankStreetActions = () => ({
  preflop: { action: null, amount: null },
  flop:    { action: null, amount: null },
  turn:    { action: null, amount: null },
  river:   { action: null, amount: null },
});

const blankRecommendations = () => ({
  preflop: null, flop: null, turn: null, river: null,
});

// bigBlind and smallBlind are stored in dollars (e.g. 0.50)
// startingStack, currentStack, estimatedStack are stored in BB
// potSize is stored in BB
// sessionPnL is stored in dollars
const initialState = {
  currentScreen:   'landing',
  bigBlind:        0.50,
  smallBlind:      0.25,
  numPlayers:      6,
  startingStack:   100,
  currentStack:    100,
  estimatedStack:  100,   // rough post-hand stack estimate (BB)
  sessionPnL:      0,     // cumulative P&L this session (dollars)
  holeCards:       [null, null],
  boardCards:      [null, null, null, null, null],
  position:        null,
  villainPos:      null,
  potSize:         0,
  streetActions:   blankStreetActions(),
  recommendations: blankRecommendations(),
  handSummary:     [],
  handHistory:     [],    // array of { handNum, summary }
  handCount:       0,
};

function reducer(state, action) {
  switch (action.type) {

    case 'START_SESSION':
      return {
        ...state,
        bigBlind:       action.bigBlind,
        smallBlind:     action.smallBlind,
        numPlayers:     action.numPlayers,
        startingStack:  action.startingStack,
        currentStack:   action.startingStack,
        estimatedStack: action.startingStack,
        sessionPnL:     0,
        handHistory:    [],
        handCount:      0,
        currentScreen:  'preflop',
      };

    case 'SET_HOLE_CARD': {
      const holeCards = [...state.holeCards];
      holeCards[action.index] = action.card;
      return { ...state, holeCards };
    }

    case 'SET_BOARD_CARD': {
      const boardCards = [...state.boardCards];
      boardCards[action.index] = action.card;
      return { ...state, boardCards };
    }

    case 'SET_POSITION':
      return { ...state, position: action.position };

    case 'SET_VILLAIN_POS':
      return { ...state, villainPos: action.villainPos };

    case 'SET_POT_SIZE':
      return { ...state, potSize: action.potSize };

    case 'SET_STREET_ACTION':
      return {
        ...state,
        streetActions: {
          ...state.streetActions,
          [action.street]: { action: action.streetAction, amount: action.amount },
        },
      };

    case 'SET_RECOMMENDATION':
      return {
        ...state,
        recommendations: {
          ...state.recommendations,
          [action.street]: action.result,
        },
      };

    case 'ADVANCE_STREET': {
      const idx  = STREET_ORDER.indexOf(state.currentScreen);
      const next = idx < STREET_ORDER.length - 1 ? STREET_ORDER[idx + 1] : state.currentScreen;
      return { ...state, currentScreen: next };
    }

    case 'GO_BACK': {
      const idx = STREET_ORDER.indexOf(state.currentScreen);
      if (idx <= 0) return state;
      const prev = STREET_ORDER[idx - 1];
      const streets = ['preflop','flop','turn','river'];
      const newRecs = streets.includes(state.currentScreen)
        ? { ...state.recommendations, [state.currentScreen]: null }
        : state.recommendations;
      return { ...state, currentScreen: prev, recommendations: newRecs };
    }

    case 'GO_TO_LANDING':
      return { ...state, currentScreen: 'landing' };

    case 'END_HAND': {
      const streets = ['preflop','flop','turn','river'];
      const handSummary = streets
        .filter(s => state.streetActions[s].action)
        .map(s => ({
          street:         s,
          action:         state.streetActions[s].action,
          amount:         state.streetActions[s].amount,
          recommendation: state.recommendations[s],
        }));

      // Rough estimate: deduct ~50% of pot for call/raise (pot ≠ to_call, so 50% is a heuristic)
      let estimatedStack = state.currentStack;
      for (const s of streets) {
        const sa = state.streetActions[s];
        if (!sa.action) continue;
        if (sa.action === 'call' || sa.action === 'raise') {
          estimatedStack = Math.max(0, estimatedStack - (sa.amount || 0) * 0.5);
        } else if (sa.action === 'all-in') {
          estimatedStack = 0;
        }
      }

      return { ...state, handSummary, estimatedStack, currentScreen: 'hand_complete' };
    }

    case 'START_NEXT_HAND': {
      const pnlDelta  = (action.confirmedStack - state.currentStack) * state.bigBlind;
      const sessionPnL = state.sessionPnL + pnlDelta;
      const previousHand = { handNum: state.handCount + 1, summary: state.handSummary };
      return {
        ...initialState,
        bigBlind:       state.bigBlind,
        smallBlind:     state.smallBlind,
        numPlayers:     state.numPlayers,
        startingStack:  action.confirmedStack,
        currentStack:   action.confirmedStack,
        estimatedStack: action.confirmedStack,
        sessionPnL,
        handHistory:    [...state.handHistory, previousHand],
        handCount:      state.handCount + 1,
        currentScreen:  'preflop',
      };
    }

    case 'UPDATE_STACK':
      return { ...state, currentStack: action.stack };

    case 'RESET_HAND':
      return {
        ...initialState,
        bigBlind:       state.bigBlind,
        smallBlind:     state.smallBlind,
        numPlayers:     state.numPlayers,
        startingStack:  state.startingStack,
        currentStack:   state.currentStack,
        estimatedStack: state.currentStack,
        sessionPnL:     state.sessionPnL,
        handHistory:    state.handHistory,
        handCount:      state.handCount,
        currentScreen:  'preflop',
      };

    default:
      return state;
  }
}

const SessionContext = createContext(null);

export function SessionProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  const api = {
    startSession:     (cfg)              => dispatch({ type: 'START_SESSION',    ...cfg }),
    setHoleCard:      (index, card)      => dispatch({ type: 'SET_HOLE_CARD',    index, card }),
    setBoardCard:     (index, card)      => dispatch({ type: 'SET_BOARD_CARD',   index, card }),
    setPosition:      (position)        => dispatch({ type: 'SET_POSITION',     position }),
    setVillainPos:    (villainPos)      => dispatch({ type: 'SET_VILLAIN_POS',  villainPos }),
    setPotSize:       (potSize)         => dispatch({ type: 'SET_POT_SIZE',     potSize }),
    setStreetAction:  (street, sa, amt) => dispatch({ type: 'SET_STREET_ACTION',street, streetAction: sa, amount: amt }),
    setRecommendation:(street, result)  => dispatch({ type: 'SET_RECOMMENDATION',street, result }),
    advanceStreet:    ()                => dispatch({ type: 'ADVANCE_STREET' }),
    goBack:           ()                => dispatch({ type: 'GO_BACK' }),
    goToLanding:      ()                => dispatch({ type: 'GO_TO_LANDING' }),
    endHand:          ()                => dispatch({ type: 'END_HAND' }),
    startNextHand:    (confirmedStack)  => dispatch({ type: 'START_NEXT_HAND',  confirmedStack }),
    updateStack:      (stack)           => dispatch({ type: 'UPDATE_STACK',     stack }),
    resetHand:        ()                => dispatch({ type: 'RESET_HAND' }),
  };

  return (
    <SessionContext.Provider value={{ state, ...api }}>
      {children}
    </SessionContext.Provider>
  );
}

export function useSession() {
  const ctx = useContext(SessionContext);
  if (!ctx) throw new Error('useSession must be inside SessionProvider');
  return ctx;
}
