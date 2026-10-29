import React from 'react';
import iconOnly from '../../assets/clyptusap-icon-small.webp';
import './ChatThinkingIndicator.css';

interface ChatThinkingIndicatorProps {
  stage?: string | null;
  subtext?: string | null;
  compact?: boolean;
  className?: string;
}

export const ChatThinkingIndicator: React.FC<ChatThinkingIndicatorProps> = ({
  stage, subtext, compact = false, className = '',
}) => {
  const detail = stage && stage.trim() !== 'Thinking...' ? stage : subtext;

  return (
    <div
      className={`clyptus-thinking-indicator ${compact ? 'thinking-compact' : ''} ${className}`}
      role="status"
      aria-live="polite"
      aria-atomic="true"
    >
      <div className="thinking-centerpiece" aria-hidden="true">
        <span className="thinking-ambient-glow" />
        <span className="thinking-sweep-ring" />
        <span className="thinking-logo-badge">
          <img src={iconOnly} width={24} height={24} alt="" decoding="async" />
        </span>
      </div>
      <div className="thinking-details">
        <p className="thinking-title">Clyptus is thinking&hellip;</p>
        {detail && <p className="thinking-subtext">{detail}</p>}
      </div>
    </div>
  );
};
