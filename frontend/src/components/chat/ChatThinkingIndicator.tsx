import React from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import iconOnly from '../../assets/clyptusap-icon.png';

interface ChatThinkingIndicatorProps {
  stage?: string | null;
  subtext?: string | null;
  compact?: boolean;
  className?: string;
}

export const ChatThinkingIndicator: React.FC<ChatThinkingIndicatorProps> = ({
  stage,
  subtext,
  compact = false,
  className = '',
}) => {
  const shouldReduceMotion = useReducedMotion();

  // Primary label text
  const primaryText = stage && stage.trim() !== 'Thinking...'
    ? stage
    : 'Analyzing your question...';

  // Subtext detailing RAG activity
  const secondaryText =
    subtext || 'Cross-referencing indexed SAP manuals and SPRO configuration dictionaries';

  return (
    <motion.div
      initial={{ opacity: 0, y: 6, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -6, scale: 0.98 }}
      transition={{ duration: 0.28, ease: [0.16, 1, 0.3, 1] }}
      className={`clyptus-thinking-indicator ${compact ? 'thinking-compact' : ''} ${className}`}
      role="status"
      aria-live="polite"
      aria-label="Clyptus.AI is analyzing your question"
    >
      {/* Centerpiece Emblem with Glow & Orbital Ring */}
      <div className="thinking-centerpiece">
        {/* Subtle Pulsing Ambient Radial Glow */}
        <motion.div
          className="thinking-ambient-glow"
          animate={
            shouldReduceMotion
              ? { opacity: 0.5, scale: 1 }
              : {
                  scale: [1, 1.25, 1],
                  opacity: [0.4, 0.75, 0.4],
                }
          }
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          aria-hidden="true"
        />

        {/* Smooth Gradient Sweep Orbit Ring */}
        <motion.div
          className="thinking-sweep-ring"
          animate={
            shouldReduceMotion
              ? { rotate: 0 }
              : { rotate: 360 }
          }
          transition={{
            duration: 3.6,
            repeat: Infinity,
            ease: 'linear',
          }}
          aria-hidden="true"
        />

        {/* Orbiting Micro-Particle 1 (Primary Brand Orange) */}
        {!shouldReduceMotion && (
          <motion.div
            className="thinking-orbit-track track-1"
            animate={{ rotate: 360 }}
            transition={{
              duration: 3.2,
              repeat: Infinity,
              ease: 'linear',
            }}
            aria-hidden="true"
          >
            <span className="thinking-particle particle-1" />
          </motion.div>
        )}

        {/* Orbiting Micro-Particle 2 (Soft Peach / Amber) */}
        {!shouldReduceMotion && (
          <motion.div
            className="thinking-orbit-track track-2"
            animate={{ rotate: -360 }}
            transition={{
              duration: 4.4,
              repeat: Infinity,
              ease: 'linear',
            }}
            aria-hidden="true"
          >
            <span className="thinking-particle particle-2" />
          </motion.div>
        )}

        {/* Center Logo Badge with Gentle Scale Transition */}
        <motion.div
          className="thinking-logo-badge"
          animate={
            shouldReduceMotion
              ? { scale: 1 }
              : { scale: [1, 1.04, 1] }
          }
          transition={{
            duration: 2.8,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        >
          <img
            src={iconOnly}
            alt="Clyptus.AI"
            className="thinking-logo-img"
          />
        </motion.div>
      </div>

      {/* Typography & Subtle Progress Section */}
      <div className="thinking-details">
        <div className="thinking-headline-row">
          <motion.span
            className="thinking-title"
            animate={
              shouldReduceMotion
                ? { opacity: 1 }
                : {
                    backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
                  }
            }
            transition={{
              duration: 3.5,
              repeat: Infinity,
              ease: 'linear',
            }}
          >
            {primaryText}
          </motion.span>
          <span className="thinking-status-dot" aria-hidden="true" />
        </div>

        <p className="thinking-subtext">
          {secondaryText}
        </p>

        {/* Elegant Subtle Progress Track */}
        <div className="thinking-progress-track" aria-hidden="true">
          <motion.div
            className="thinking-progress-bar"
            animate={
              shouldReduceMotion
                ? { x: '50%' }
                : {
                    x: ['-100%', '240%'],
                  }
            }
            transition={{
              duration: 1.8,
              repeat: Infinity,
              ease: [0.4, 0, 0.2, 1],
            }}
          />
        </div>
      </div>
    </motion.div>
  );
};
