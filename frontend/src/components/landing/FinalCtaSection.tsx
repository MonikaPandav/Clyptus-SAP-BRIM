import React from 'react';
import { ArrowRight, ArrowUpRight, Lock, ShieldCheck, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';

export const FinalCtaSection: React.FC = () => {
  return (
    <section className="final-cta-section">
      <div className="section-container">
        <div className="final-cta-card">
          {/* Subtle Ambient Radial Aura */}
          <div className="final-cta-radial-glow" />

          <div className="final-cta-content">
            <div className="kicker-pill-subtle">
              <span className="pill-dot" />
              <span>READY TO EXPLORE SAP + BRIM?</span>
            </div>

            <h2 className="cta-headline">
              Never Guess An SAP Setting Again.<br />
              <span className="hero-italic-serif">Ask Clyptus.AI.</span>
            </h2>

            <p className="cta-description">
              Access grounded answers across Convergent Invoicing, Charging, FI-CA, and SOM. Backed by verified enterprise documentation and zero-hallucination guardrails.
            </p>

            <div className="cta-buttons-row">
              <Link to="/login" className="button-brand-pill">
                <span>Open Enterprise Workspace</span>
                <ArrowRight size={16} />
              </Link>
              <Link to="/how-it-works" className="button-outline-pill">
                <span>See How It Works</span>
                <ArrowUpRight size={15} />
              </Link>
            </div>

            <div className="cta-trust-indicators">
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
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
