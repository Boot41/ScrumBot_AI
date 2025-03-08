import React from 'react';
import './ChatIcons.css';

export const BotIcon: React.FC = () => (
  <div className="icon-container">
    {[0, -1].map((delay) => (
      <div
        key={delay}
        className="ring bot"
        style={{ animationDelay: `${delay}s` }}
      />
    ))}
    <div className="icon-core bot">
      <div className="icon-inner">
        <div className="icon-text bot">AI</div>
      </div>
    </div>
  </div>
);

export const UserIcon: React.FC = () => (
  <div className="icon-container">
    {[0, -1].map((delay) => (
      <div
        key={delay}
        className="ring user"
        style={{ animationDelay: `${delay}s` }}
      />
    ))}
    <div className="icon-core user">
      <div className="icon-inner">
        <div className="icon-text user">You</div>
      </div>
    </div>
  </div>
);
