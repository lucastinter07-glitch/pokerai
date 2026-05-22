import React from 'react';

export default function ScreenWrapper({ children, title, isLanding }) {
  return (
    <div
      className={`screen-wrapper${isLanding ? ' screen-wrapper--landing' : ''} screen-enter`}
    >
      {title && <div className="screen-label">{title}</div>}
      {children}
    </div>
  );
}
