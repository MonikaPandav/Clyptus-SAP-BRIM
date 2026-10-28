import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, ArrowUpRight, Lock, ShieldCheck, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';
import {
  viewportOnce,
  transitions,
} from '../../utils/motionVariants';

export const FinalCtaSection: React.FC = () => {
  return (
    <section className="final-cta-section">
      <div className="section-container">
        <motion.div
          className="final-cta-card"
          initial={{ opacity: 0, scale: 0.97, y: 28 }}
          whileInView={{ opacity: 1, scale: 1, y: 0 }}
          viewport={viewportOnce}
          transition={transitions.gentle}
        >
          {/* Subtle Ambient Radial Aura with gentle breathing pulse */}
          <motion.div
            className="final-cta-radial-glow"
            animate={{ scale: [1, 1.1, 1], opacity: [0.65, 0.95, 0.65] }}
            transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
          />

          <div className="final-cta-content">
            <motion.div
              className="kicker-pill-subtle"
              initial={{ opacity: 0, y: -10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={viewportOnce}
              transition={{ delay: 0.1, duration: 0.4 }}
            >
              <span className="pill-dot" />
              <span>READY TO EXPLORE SAP + BRIM?</span>
            </motion.div>

            <motion.h2
              className="cta-headline"
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={viewportOnce}
              transition={{ delay: 0.15, duration: 0.5 }}
            >
              Never Guess An SAP Setting Again.<br />
              <span className="hero-italic-serif">Ask Clyptus.AI.</span>
            </motion.h2>

            <motion.p
              className="cta-description"
              initial={{ opacity: 0, y: 14 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={viewportOnce}
              transition={{ delay: 0.2, duration: 0.5 }}
            >
              Access grounded answers across Convergent Invoicing, Charging, FI-CA, and SOM. Backed by verified enterprise documentation and zero-hallucination guardrails.
            </motion.p>

            <motion.div
              className="cta-buttons-row"
              initial={{ opacity: 0, y: 14 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={viewportOnce}
              transition={{ delay: 0.25, duration: 0.5 }}
            >
              <Link to="/login" className="button-brand-pill">
                <span>Open Enterprise Workspace</span>
                <ArrowRight size={16} />
              </Link>
              <Link to="/how-it-works" className="button-outline-pill">
                <span>See How It Works</span>
                <ArrowUpRight size={15} />
              </Link>
            </motion.div>

            <motion.div
              className="cta-trust-indicators"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={viewportOnce}
              transition={{ delay: 0.35, duration: 0.6 }}
            >
              <div className="trust-indicator-item">
                <ShieldCheck size={14} className="text-orange" />
                <span>100% Grounded in Official Manuals</span>
              </div>
              <span className="trust-sep">·</span>
              <div className="trust-indicator-item">
                <Lock size={14} className="text-orange" />
                <span>Tenant-Isolated Workspaces</span>
              </div>
              <span className="trust-sep">·</span>
              <div className="trust-indicator-item">
                <Sparkles size={14} className="text-orange" />
                <span>Real-Time Streaming Generation</span>
              </div>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};
