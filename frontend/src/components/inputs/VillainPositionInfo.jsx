import React, { useState } from 'react';

const ITEMS = [
  { action: 'BTN',  desc: 'Button — last to act postflop, widest range, biggest positional advantage.' },
  { action: 'CO',   desc: 'Cutoff — second last preflop, wide range, strong position.' },
  { action: 'HJ',   desc: 'Hijack — mid-late position, solid opening range.' },
  { action: 'MP',   desc: 'Middle position — tighter range than late positions.' },
  { action: 'UTG',  desc: 'Under the gun — first to act, tightest and strongest range.' },
  { action: 'SB',   desc: 'Small blind — acts first postflop, often polar 3-bet or fold range.' },
  { action: 'BB',   desc: 'Big blind — defended wide preflop, many hands in their range.' },
];

export default function VillainPositionInfo() {
  const [show, setShow] = useState(false);

  return (
    <>
      <button className="info-icon-btn" onClick={() => setShow(true)} aria-label="What is Villain Position?">
        ⓘ
      </button>

      {show && (
        <div className="info-modal-overlay" onClick={() => setShow(false)}>
          <div className="info-modal" onClick={(e) => e.stopPropagation()}>
            <div className="info-modal__header">
              <span className="info-modal__title">Villain Position</span>
              <button className="info-modal__close" onClick={() => setShow(false)}>✕</button>
            </div>
            <p className="info-modal__body">
              Where the main betting opponent is seated. Their position shapes their range — later positions play more hands, earlier positions play fewer.
            </p>
            <div className="info-modal__items">
              {ITEMS.map((item) => (
                <div key={item.action} className="info-modal__item">
                  <span className="info-modal__action">{item.action}</span>
                  <span className="info-modal__desc">{item.desc}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
