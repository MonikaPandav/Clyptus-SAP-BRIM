import React from 'react';
import { useHeroParallax } from '../hooks/useHeroParallax';
import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { PublicNav } from '../components/navbar/PublicNav';
import { Footer } from '../components/footer/Footer';
import { PageMeta } from '../components/ui/PageMeta';
import { HeroChatbotPreview } from '../components/landing/HeroChatbotPreview';
import { DeferredLandingSections } from '../components/landing/DeferredLandingSections';
import iconOnly from '../assets/clyptusap-icon-small.webp';

export const LandingPage: React.FC = () => {
  const heroRef = useHeroParallax();

  return (
    <div className="clyptus-landing-wrap">
      <PageMeta
        title="SAP + BRIM AI Knowledge Platform"
        description="Clyptus.AI is an enterprise AI knowledge assistant dedicated to SAP and SAP BRIM with grounded citations and zero hallucination."
      />
      <PublicNav />

      <main className="landing-main-content">
        {/* =========================================================================
            Hero Section: Center-aligned, Warm Ivory Background with Peach Radial Aura
           ========================================================================= */}
        <section ref={heroRef} className="hero-minimal-section">
          {/* Subtle Ambient Background Gradient Orbs with Scroll Parallax */}
          <div
            className="hero-radial-glow"
            aria-hidden="true"
          />
          <div
            className="hero-ambient-orb orb-left"
            aria-hidden="true"
          />
          <div
            className="hero-ambient-orb orb-right"
            aria-hidden="true"
          />

          <div className="hero-content-container">
            {/* Kicker Pill */}
            <div
              className="kicker-pill-subtle"
            >
              <span className="kicker-icon-badge">
                <img src={iconOnly} alt="Clyptus.AI" className="h-3.5 w-3.5 object-contain" />
              </span>
              <span>Clyptus.AI</span>
              <span className="pill-sep">/</span>
              <span className="pill-strong">SAP + BRIM ENTERPRISE ASSISTANT</span>
            </div>

            {/* Main Headline */}
            <h1
              className="hero-main-title"
            >
              Every SAP Challenge.<br />
              <span className="hero-title-accent">A Clearer Path Forward.</span>
            </h1>

            {/* Subtitle Description */}
            <p
              className="hero-description text-center mx-auto"
            >
              Navigate complex SAP BRIM workflows, troubleshoot technical issues, and find reliable, documentation-grounded answers with Clyptus.AI.
            </p>

            {/* CTA Buttons Row */}
            <div
              className="hero-actions-row"
            >
              <Link to="/login" className="button-brand-pill">
                <span>Get Started</span>
                <ArrowRight size={16} />
              </Link>
              <a href="#features" className="button-outline-pill">
                <span>Explore Architecture</span>
                <ArrowRight size={15} />
              </a>
            </div>

            {/* Prominent Trust Indicators */}
            <div
              className="hero-trust-bar"
            >
              <div className="trust-item">
                <span className="trust-dot" />
                <strong>SAP-Focused</strong>
              </div>
              <span className="trust-sep">·</span>
              <div className="trust-item">
                <span className="trust-dot" />
                <strong>Grounded in Official Documentation</strong>
              </div>
            </div>

            {/* Centerpiece Chatbot Preview Showcase Window with Parallax Shift */}
            <div
              className="hero-showcase-container"
            >
              <HeroChatbotPreview />
            </div>
          </div>
        </section>

        <DeferredLandingSections />
      </main>

      <Footer />
    </div>
  );
};
