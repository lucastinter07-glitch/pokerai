import React from "react";
import "./GameContext.css";

const POSITIONS = ["UTG","MP","CO","BTN","SB","BB"];

export default function GameContext({
  position, setPosition,
  stack, setStack,
  pot, setPot,
  toCall, setToCall,
  villainPos, setVillainPos,
}) {
  return (
    <div className="game-context">
      <section className="section">
        <h2 className="section-label">Game Context</h2>
        <div className="ctx-grid">
          <label className="ctx-field">
            <span>Your Position</span>
            <select value={position} onChange={e => setPosition(e.target.value)}>
              {POSITIONS.map(p => <option key={p}>{p}</option>)}
            </select>
          </label>
          <label className="ctx-field">
            <span>Stack (BB)</span>
            <input type="number" value={stack} min={1} step={10}
              onChange={e => setStack(e.target.value)} />
          </label>
          <label className="ctx-field">
            <span>Pot (BB)</span>
            <input type="number" value={pot} min={0} step={0.5}
              onChange={e => setPot(e.target.value)} />
          </label>
          <label className="ctx-field">
            <span>To Call (BB)</span>
            <input type="number" value={toCall} min={0} step={0.5}
              onChange={e => setToCall(e.target.value)} />
          </label>
        </div>
      </section>

      <section className="section">
        <h2 className="section-label">Opponent</h2>
        <p className="ctx-caption">Villain's position — used to model their range</p>
        <select
          className="villain-select"
          value={villainPos}
          onChange={e => setVillainPos(e.target.value)}
        >
          <option value="">None — opening or no bet</option>
          {POSITIONS.map(p => <option key={p} value={p}>{p}</option>)}
        </select>
      </section>
    </div>
  );
}