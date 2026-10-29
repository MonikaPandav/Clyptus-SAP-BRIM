import React, { useRef } from 'react';
import { motion, useInView, useReducedMotion, type Variants } from 'framer-motion';
import { ArrowDown, ArrowUpRight, Boxes, MessageCircle, Search, ShieldCheck, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Footer } from '../components/footer/Footer';
import { PublicNav } from '../components/navbar/PublicNav';
import { PageMeta } from '../components/ui/PageMeta';
import { cardVariant, transitions, viewportOnce } from '../utils/motionVariants';
import './productInfo.css';

const steps = [
  [MessageCircle, 'Ask', 'Ask your SAP or BRIM question naturally, whether regarding a transaction code, configuration path, process flow, or customizing table.', 'No special syntax required.'],
  [Search, 'Retrieve', 'Dense vector similarity (MiniLM-L6) and BM25 lexical search run in parallel over pre-indexed document chunks.', 'Hybrid dense & lexical retrieval.'],
  [Boxes, 'Context & Rerank', 'A cross-encoder model scores candidate chunks, elevating the most contextually relevant technical excerpts.', 'Precision reranking.'],
  [Sparkles, 'Generate & Stream', 'The LLM streams tokens via SSE with ChatGPT-style thinking and bouncing animation indicators.', 'Real-time interactive streaming.'],
  [ShieldCheck, 'Ground & Verify', 'The response is checked for hallucination against enterprise domain boundaries with automated quality validation.', 'Enterprise verification.'],
] as const;

const workflowCardVariant: Variants = {
  hidden: cardVariant.hidden,
  visible: (index: number) => ({
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { ...transitions.smooth, delay: (index % 3) * 0.06 },
  }),
};

function WorkflowStep({ step, index, last }: { step: typeof steps[number]; index: number; last: boolean }) {
  const [Icon, title, text, note] = step;
  const ref = useRef<HTMLLIElement>(null);
  const inView = useInView(ref, { once: true, amount: 0.35 });
  const reduceMotion = useReducedMotion();
  const revealed = inView || !!reduceMotion;

  return (
    <li className="info-process-step" ref={ref} data-revealed={revealed}>
      <span className="info-step-indicator">0{index + 1}</span>
      {!last && <span className="info-step-connector" aria-hidden="true"><motion.span initial={reduceMotion ? false : { scaleY: 0 }} animate={{ scaleY: revealed ? 1 : 0 }} transition={{ ...transitions.smooth, delay: reduceMotion ? 0 : 0.12, duration: reduceMotion ? 0 : 0.65 }} /></span>}
      <motion.article className="story-card info-workflow-card" custom={index} variants={reduceMotion ? undefined : workflowCardVariant} initial={reduceMotion ? false : 'hidden'} animate={revealed ? 'visible' : 'hidden'} whileHover={reduceMotion ? undefined : { y: -3 }} transition={transitions.micro}>
        <div className="info-card-icon"><Icon size={20} /></div>
        <div className="info-step-copy">
          <h2>{title}</h2>
          <p>{text}</p>
          <span className="story-tag tag-approach info-step-note">{note}</span>
        </div>
      </motion.article>
    </li>
  );
}

export const HowItWorksPage: React.FC = () => {
  const reduceMotion = useReducedMotion();
  return (
    <div className="clyptus-landing-wrap product-info-page">
      <PageMeta
        title="How It Works"
        description="Learn how Clyptusap.ai retrieves SAP knowledge to generate grounded answers."
      />
      <PublicNav />
      <main>
        <section className="inner-hero info-hero section-container">
          <div className="section-header-center info-hero-copy">
          <span className="kicker-pill-subtle">RETRIEVAL-AUGMENTED GENERATION</span>
          <h1 className="section-title-large">
            From question<br />
            to <span className="hero-italic-serif">grounded answer.</span>
          </h1>
          <p className="section-subtitle-muted">
            Clyptusap.ai searches its indexed SAP knowledge base for relevant technical documentation and uses that context to generate grounded enterprise answers under strict administrative control.
          </p>
          <a className="button-outline-pill info-hero-action" href="#process">
            FOLLOW THE ARCHITECTURE <ArrowDown size={14} />
          </a>
          </div>
          <motion.div className="story-card info-hero-visual" initial={reduceMotion ? false : { opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={viewportOnce} transition={transitions.smooth}>
          <div className="info-hero-flow">
            <span><MessageCircle size={17} /> Question</span>
            <ArrowUpRight size={16} />
            <span><Search size={17} /> Hybrid Retrieval</span>
            <ArrowUpRight size={16} />
            <span><Sparkles size={17} /> Verified Answer</span>
          </div>
          </motion.div>
        </section>


        <section className="section-container info-content-section info-process" id="process" aria-label="Workflow">
          <div className="info-section-label"><span className="story-tag tag-approach">FROM QUESTION TO RESPONSE</span></div>
          <ol className="info-process-list">
            {steps.map((step, i) => (
              <WorkflowStep key={step[1]} step={step} index={i} last={i === steps.length - 1} />
            ))}
          </ol>
        </section>

        <motion.section className="section-container info-bottom-cta" initial={reduceMotion ? false : { opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={viewportOnce} transition={transitions.smooth}>
          <span className="story-tag tag-approach">READY TO TEST?</span>
          <h2>Experience the SAP Knowledge Assistant</h2>
          <Link className="button-brand-pill" to="/login">
            Ask Clyptusap.ai <ArrowUpRight size={16} />
          </Link>
        </motion.section>
      </main>
      <Footer />
    </div>
  );
};
