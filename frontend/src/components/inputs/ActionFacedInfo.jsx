import React, { useState } from 'react';

const ITEMS = [
  { action: 'Fold',   desc: 'They folded — you win the pot automatically.' },
  { action: 'Check',  desc: 'No bet made. You can check back or bet.' },
  { action: 'Call',   desc: 'They matched a previous bet. Enter that amount as pot size.' },
  { action: 'Raise',  desc: 'They raised. Enter the raise amount as pot size.' },
  { action: 'All-In', desc: 'They moved all their chips in.' },
];

export default function ActionFacedInfo() {
  const [show, setShow] = useState(false);

  return (
    <>
      <button className="info-icon-btn" onClick={() => setShow(true)} aria-label="What is Action Faced?">
        ⓘ
      </button>

      {show && (
        <div className="info-modal-overlay" onClick={() => setShow(false)}>
          <div className="info-modal" onClick={(e) => e.stopPropagation()}>
            <div className="info-modal__header">
              <span className="info-modal__title">Action Faced</span>
              <button className="info-modal__close" onClick={() => setShow(false)}>✕</button>
            </div>
            <p className="info-modal__body">
              What your opponent did before it's your turn. Select what they did so the AI can recommend your best response.
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
