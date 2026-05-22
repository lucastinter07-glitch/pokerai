import React from 'react';
import { SessionProvider, useSession } from './context/SessionContext';
import TopBar from './components/layout/TopBar';
import CardTray from './components/layout/CardTray';
import LandingScreen from './screens/LandingScreen';
import PreflopScreen from './screens/PreflopScreen';
import FlopScreen from './screens/FlopScreen';
import TurnScreen from './screens/TurnScreen';
import RiverScreen from './screens/RiverScreen';
import HandCompleteScreen from './screens/HandCompleteScreen';

function AppScreens() {
  const { state } = useSession();
  const { currentScreen } = state;

  const screens = {
    landing:       <LandingScreen />,
    preflop:       <PreflopScreen />,
    flop:          <FlopScreen />,
    turn:          <TurnScreen />,
    river:         <RiverScreen />,
    hand_complete: <HandCompleteScreen />,
  };

  return (
    <div className="app-shell">
      <TopBar />
      <div className="app-screens">
        {screens[currentScreen] || <LandingScreen />}
      </div>
      <CardTray />
    </div>
  );
}

export default function App() {
  return (
    <SessionProvider>
      <AppScreens />
    </SessionProvider>
  );
}
