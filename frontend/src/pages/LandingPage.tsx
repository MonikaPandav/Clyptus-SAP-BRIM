import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { PublicNav } from '../components/navbar/PublicNav';
import { Footer } from '../components/footer/Footer';
import { PageMeta } from '../components/ui/PageMeta';
import { HeroChatbotPreview } from '../components/landing/HeroChatbotPreview';
import { EnterprisePartnerTicker } from '../components/landing/EnterprisePartnerTicker';
import { InfinitePossibilitiesGrid } from '../components/landing/InfinitePossibilitiesGrid';
import { RagWorkflowSection } from '../components/landing/RagWorkflowSection';
import { BrimModuleExplorer } from '../components/landing/BrimModuleExplorer';
import { AiComparisonSection } from '../components/landing/AiComparisonSection';
import { QuestionPromptBank } from '../components/landing/QuestionPromptBank';
import { AboutClyptusSection } from '../components/landing/AboutClyptusSection';
import { FaqSection } from '../components/landing/FaqSection';
import { FinalCtaSection } from '../components/landing/FinalCtaSection';
import iconOnly from '../assets/clyptusap-icon.png';

export const LandingPage: React.FC = () => {
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
        <section className="hero-minimal-section">
          {/* Subtle Ambient Background Gradient Orbs */}
          <div className="hero-radial-glow" aria-hidden="true" />
          <div className="hero-ambient-orb orb-left" aria-hidden="true" />
          <div className="hero-ambient-orb orb-right" aria-hidden="true" />

          <div className="hero-content-container">
            {/* Kicker Pill */}
            <motion.div
              className="kicker-pill-subtle"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
            >
              <span className="kicker-icon-badge">
                <img src={iconOnly} alt="Clyptus.AI" className="h-3.5 w-3.5 object-contain" />
              </span>
              <span>Clyptus.AI</span>
              <span className="pill-sep">/</span>
              <span className="pill-strong">SAP + BRIM ENTERPRISE ASSISTANT</span>
            </motion.div>

            {/* Main Headline with Signature Italic Serif Highlight */}
            <motion.h1
              className="hero-main-title"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.08 }}
            >
              Never Second-Guess Your<br />
              <span className="hero-italic-serif">SAP &amp; BRIM Architecture Ever Again.</span>
            </motion.h1>

            {/* Subtitle Description */}
            <motion.p
              className="hero-description"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.14 }}
            >
              Ditch fragmented spreadsheets, guesswork, and rigid consulting notes. <strong>Clyptus.AI</strong> retrieves verified SAP configuration manuals, transaction codes, and SPRO customizing paths with <strong>mathematical grounding</strong> and <strong>zero hallucination</strong>.
            </motion.p>

            {/* CTA Buttons Row */}
            <motion.div
              className="hero-actions-row"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <Link to="/login" className="button-brand-pill">
                <span>Get Started</span>
                <ArrowRight size={16} />
              </Link>
              <a href="#features" className="button-outline-pill">
                <span>Explore Architecture</span>
                <ArrowRight size={15} />
              </a>
            </motion.div>

            {/* Prominent Trust Indicators */}
            <motion.div
              className="hero-trust-bar"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.26 }}
            >
              <div className="trust-item">
                <span className="trust-dot" />
                <strong>SAP-Focused</strong>
              </div>
              <span className="trust-sep">·</span>
              <div className="trust-item">
                <span className="trust-dot" />
                <strong>Hybrid Retrieval (BM25 + Vectors)</strong>
              </div>
              <span className="trust-sep">·</span>
              <div className="trust-item">
                <span className="trust-dot" />
                <strong>Grounded in Official Documentation</strong>
              </div>
            </motion.div>

            {/* Centerpiece Chatbot Preview Showcase Window */}
            <motion.div
              className="hero-showcase-container"
              initial={{ opacity: 0, y: 28 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.65, delay: 0.3 }}
            >
              <HeroChatbotPreview />
            </motion.div>
          </div>
        </section>

        {/* Enterprise Partner / Module Ticker Strip */}
        <EnterprisePartnerTicker />

        {/* One Knowledge Platform. Infinite SAP Possibilities. (Feature Cards & Orbital Arcs) */}
        <InfinitePossibilitiesGrid />

        {/* The 6-Stage RAG Pipeline Interactive Section */}
        <RagWorkflowSection />

        {/* BRIM Module Explorer (SOM, CC, CI, FI-CA, CM) */}
        <BrimModuleExplorer />

        {/* Generic AI vs Clyptus.AI Side-by-Side Comparison */}
        <AiComparisonSection />

        {/* Practical Consulting Prompt Bank */}
        <QuestionPromptBank />

        {/* About Clyptus Section */}
        <AboutClyptusSection />

        {/* FAQ Accordion Section */}
        <FaqSection />

        {/* Final Elevated Call to Action */}
        <FinalCtaSection />
      </main>

      <Footer />
    </div>
  );
};
