import React from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { ArrowRight, BookOpen, Boxes, MessageCircle, Search, ShieldCheck, Sparkles, Workflow } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Footer } from '../components/footer/Footer';
import { PublicNav } from '../components/navbar/PublicNav';
import { PageMeta } from '../components/ui/PageMeta';
import { cardVariant, staggerContainer, transitions, viewportCard, viewportOnce } from '../utils/motionVariants';
import './productInfo.css';

const items = [
  [Sparkles, 'SAP answers with context', 'Ask in everyday technical language and get responses shaped strictly by indexed enterprise SAP knowledge.'],
  [Search, 'Hybrid dense + lexical retrieval', 'Combines sentence-transformers vector embeddings with BM25 keyword matching for optimal recall.'],
  [Boxes, 'Deep BRIM domain specialization', 'Exhaustive coverage of Convergent Mediation, Convergent Charging, Convergent Invoicing, FI-CA, and SOM.'],
  [MessageCircle, 'Conversations that retain thread context', 'Multi-turn query rewriting preserves conversational intent across follow-up technical questions.'],
  [BookOpen, 'Verified page-level citations', 'Every answer links to specific document chunks, pages, and confidence scores.'],
  [ShieldCheck, 'Grounding & guardrails', 'Real-time hallucination prevention guardrails reject unsupported assertions and non-SAP queries.'],
] as const;

export const FeaturesPage: React.FC = () => {
  const reduceMotion = useReducedMotion();
  return (
    <div className="clyptus-landing-wrap product-info-page">
      <PageMeta
        title="Features"
        description="Explore SAP-focused answers, retrieval and BRIM knowledge with Clyptusap.ai."
      />
      <PublicNav />
      <main>
        <section className="inner-hero info-hero section-container">
          <div className="section-header-center info-hero-copy">
          <span className="kicker-pill-subtle">SAP + BRIM AI KNOWLEDGE ASSISTANT</span>
          <h1 className="section-title-large">
            Good questions<br />
            <span className="hero-italic-serif">deserve verified SAP context.</span>
          </h1>
          <p className="section-subtitle-muted">
            Clyptusap.ai retrieves relevant information from indexed SAP knowledge before generating an answer, backed by streaming citations and cross-encoder reranking.
          </p>
          <Link className="button-outline-pill info-hero-action" to="/how-it-works">
            See how it works <ArrowRight size={16} />
          </Link>
          </div>
          <motion.div className="story-card info-hero-visual" initial={reduceMotion ? false : { opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={viewportOnce} transition={transitions.smooth}>
            <div className="info-art-stack">
              <span><Workflow size={17} /> SAP Technical Question</span>
              <span><Search size={17} /> Hybrid Retrieved Context</span>
              <span><Sparkles size={17} /> Grounded Streaming Answer</span>
            </div>
          </motion.div>
        </section>

        <section className="section-container info-content-section" aria-label="Features">
          <div className="info-section-label"><span className="story-tag tag-approach">BUILT FOR SAP · DEEPLY FOCUSED ON BRIM</span></div>
          <motion.div className="info-feature-grid" variants={reduceMotion ? undefined : staggerContainer(0.08, 0.04)} initial={reduceMotion ? false : 'hidden'} whileInView="visible" viewport={viewportCard}>
            {items.map(([Icon, title, text], index) => (
              <motion.article className="story-card info-feature-card" key={title} variants={reduceMotion ? undefined : cardVariant} whileHover={reduceMotion ? undefined : { y: -4 }} transition={transitions.micro}>
                <div className="info-feature-meta">
                <span className="info-card-icon"><Icon size={19} /></span>
                <span className="pillar-number">0{index + 1}</span>
                </div>
                <h2>{title}</h2>
                <p>{text}</p>
              </motion.article>
            ))}
          </motion.div>
        </section>

        <motion.section className="section-container info-bottom-cta" initial={reduceMotion ? false : { opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={viewportOnce} transition={transitions.smooth}>
          <span className="story-tag tag-approach">SAP KNOWLEDGE, IN CONTEXT</span>
          <h2>Have an SAP question?</h2>
          <Link className="button-brand-pill" to="/login">
            Ask Clyptusap.ai <ArrowRight size={16} />
          </Link>
        </motion.section>
      </main>
      <Footer />
    </div>
  );
};
