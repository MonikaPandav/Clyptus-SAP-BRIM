import React, { useRef } from 'react';
import { motion, useScroll, useTransform, useReducedMotion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { PublicNav } from '../components/navbar/PublicNav';
import { Footer } from '../components/footer/Footer';
import { PageMeta } from '../components/ui/PageMeta';
import { HeroChatbotPreview } from '../components/landing/HeroChatbotPreview';
import { EnterprisePartnerTicker } from '../components/landing/EnterprisePartnerTicker';
import { InfinitePossibilitiesGrid } from '../components/landing/InfinitePossibilitiesGrid';
import { BrimModuleExplorer } from '../components/landing/BrimModuleExplorer';
import { AiComparisonSection } from '../components/landing/AiComparisonSection';
import { AboutClyptusSection } from '../components/landing/AboutClyptusSection';
import { FaqSection } from '../components/landing/FaqSection';
import { FinalCtaSection } from '../components/landing/FinalCtaSection';
import iconOnly from '../assets/clyptusap-icon.png';

export const LandingPage: React.FC = () => {
  const heroRef = useRef<HTMLElement>(null);
  const shouldReduceMotion = useReducedMotion();

  // Gentle Parallax Scroll Setup for Hero Ambient Layers
  const { scrollYProgress } = useScroll({
    target: heroRef,
    offset: ['start start', 'end start'],
  });

  const orbLeftY = useTransform(
    scrollYProgress,
    [0, 1],
    shouldReduceMotion ? [0, 0] : [0, 80]
  );
  const orbRightY = useTransform(
    scrollYProgress,
    [0, 1],
    shouldReduceMotion ? [0, 0] : [0, -60]
  );
  const showcaseY = useTransform(
    scrollYProgress,
    [0, 1],
    shouldReduceMotion ? [0, 0] : [0, 32]
  );
  const glowScale = useTransform(
    scrollYProgress,
    [0, 1],
    shouldReduceMotion ? [1, 1] : [1, 1.1]
  );

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
          <motion.div
            className="hero-radial-glow"
            style={{ scale: glowScale }}
            aria-hidden="true"
          />
          <motion.div
            className="hero-ambient-orb orb-left"
            style={{ y: orbLeftY }}
            aria-hidden="true"
          />
          <motion.div
            className="hero-ambient-orb orb-right"
            style={{ y: orbRightY }}
            aria-hidden="true"
          />

          <div className="hero-content-container">
            {/* Kicker Pill */}
            <motion.div
              className="kicker-pill-subtle"
              initial={{ opacity: 0, y: -12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
            >
              <span className="kicker-icon-badge">
                <img src={iconOnly} alt="Clyptus.AI" className="h-3.5 w-3.5 object-contain" />
              </span>
              <span>Clyptus.AI</span>
              <span className="pill-sep">/</span>
              <span className="pill-strong">SAP + BRIM ENTERPRISE ASSISTANT</span>
            </motion.div>

            {/* Main Headline */}
            <motion.h1
              className="hero-main-title"
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.55, delay: 0.08, ease: [0.16, 1, 0.3, 1] }}
            >
              Never Second-Guess Your<br />
              <span className="hero-title-accent">SAP &amp; BRIM Architecture Ever Again.</span>
            </motion.h1>

            {/* Subtitle Description */}
            <motion.p
              className="hero-description text-center mx-auto"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.55, delay: 0.14, ease: [0.16, 1, 0.3, 1] }}
            >
              Ditch fragmented spreadsheets, guesswork, and rigid consulting notes. <strong>Clyptus.AI</strong> retrieves verified SAP configuration manuals, transaction codes, and SPRO customizing paths with <strong>mathematical grounding</strong> and <strong>zero hallucination</strong>.
            </motion.p>

            {/* CTA Buttons Row */}
            <motion.div
              className="hero-actions-row"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.55, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
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
              transition={{ duration: 0.65, delay: 0.26 }}
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

            {/* Centerpiece Chatbot Preview Showcase Window with Parallax Shift */}
            <motion.div
              className="hero-showcase-container"
              style={{ y: showcaseY }}
              initial={{ opacity: 0, y: 32 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
            >
              <HeroChatbotPreview />
            </motion.div>
          </div>
        </section>

        {/* Enterprise Partner / Module Ticker Strip */}
        <EnterprisePartnerTicker />

        {/* One Knowledge Platform. Infinite SAP Possibilities. (Feature Cards & Orbital Arcs) */}
        <InfinitePossibilitiesGrid />

        {/* BRIM Module Explorer (SOM, CC, CI, FI-CA, CM) */}
        <BrimModuleExplorer />

        {/* Generic AI vs Clyptus.AI Side-by-Side Comparison */}
        <AiComparisonSection />

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
