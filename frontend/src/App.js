import React, { useState } from "react";
import axios from "axios";
import API_BASE from "./config";
import CardPicker from "./components/CardPicker";
import GameContext from "./components/GameContext";
import Recommendation from "./components/Recommendation";
import "./App.css";

const SLOTS = ["hole_1", "hole_2", "flop_1", "flop_2", "flop_3", "turn", "river"];

function App() {
  const [cards, setCards]           = useState({});
  const [position, setPosition]     = useState("BTN");
  const [stack, setStack]           = useState(100);
  const [pot, setPot]               = useState(1.5);
  const [toCall, setToCall]         = useState(0);
  const [villainPos, setVillainPos] = useState("");
  const [result, setResult]         = useState(null);
  const [loading, setLoading]       = useState(false);
  const [error, setError]           = useState(null);

  function setCard(slot, card) {
    setCards(prev => ({ ...prev, [slot]: card }));
  }

  function clearCard(slot) {
    setCards(prev => { const n = {...prev}; delete n[slot]; return n; });
  }

  function resetAll() {
    setCards({});
    setResult(null);
    setError(null);
  }

  function getHoleCards() {
    return [cards["hole_1"], cards["hole_2"]].filter(Boolean);
  }

  function getBoardCards() {
    const out = [];
    for (const s of ["flop_1","flop_2","flop_3","turn","river"]) {
      if (!cards[s]) break;
      out.push(cards[s]);
    }
    return out;
  }

  async function getRecommendation() {
    const hole  = getHoleCards();
    const board = getBoardCards();

    if (hole.length !== 2) {
      setError("Select both hole cards first."); return;
    }
    if (![0,3,4,5].includes(board.length)) {
      setError(`Board needs 0, 3, 4, or 5 cards — got ${board.length}.`); return;
    }

    setError(null);
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/recommend`, {
        hole_cards:       hole,
        position:         position,
        stack:            parseFloat(stack),
        board:            board,
        pot:              parseFloat(pot),
        to_call:          parseFloat(toCall),
        villain_position: villainPos || null,
      });
      setResult(res.data);
    } catch (e) {
      setError("Could not reach the advisor. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Poker AI</h1>
        <p className="subtitle">Range-based advisor · No-Limit Hold'em</p>
      </header>

      <section className="section">
        <h2 className="section-label">Your Hand</h2>
        <div className="card-row">
          {["hole_1","hole_2"].map(slot => (
            <CardPicker
              key={slot}
              slot={slot}
              label={slot === "hole_1" ? "Card 1" : "Card 2"}
              selected={cards[slot] || null}
              usedCards={Object.values(cards).filter(Boolean)}
              onSelect={card => setCard(slot, card)}
              onClear={() => clearCard(slot)}
            />
          ))}
        </div>
      </section>

      <section className="section">
        <h2 className="section-label">Board</h2>
        <div className="card-row board-row">
          {[
            ["flop_1","Flop"],["flop_2","Flop"],["flop_3","Flop"],
            ["turn","Turn"],["river","River"]
          ].map(([slot, label]) => (
            <CardPicker
              key={slot}
              slot={slot}
              label={label}
              selected={cards[slot] || null}
              usedCards={Object.values(cards).filter(Boolean)}
              onSelect={card => setCard(slot, card)}
              onClear={() => clearCard(slot)}
            />
          ))}
        </div>
      </section>

      <GameContext
        position={position}     setPosition={setPosition}
        stack={stack}           setStack={setStack}
        pot={pot}               setPot={setPot}
        toCall={toCall}         setToCall={setToCall}
        villainPos={villainPos} setVillainPos={setVillainPos}
      />

      <div className="actions">
        <button className="btn-reset" onClick={resetAll}>↺ Reset</button>
        <button className="btn-primary" onClick={getRecommendation} disabled={loading}>
          {loading ? "Calculating..." : "Get Recommendation"}
        </button>
      </div>

      {error && <div className="error-box">{error}</div>}

      {result && <Recommendation result={result} toCall={parseFloat(toCall)} />}
    </div>
  );
}

export default App;