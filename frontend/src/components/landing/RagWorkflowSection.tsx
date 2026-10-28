import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowRight,
  BrainCircuit,
  CheckCircle,
  Database,
  Filter,
  Layers,
  Search,
  ShieldCheck,
} from 'lucide-react';
import {
  sectionHeaderVariant,
  staggerContainer,
  cardVariant,
  tabPanelVariant,
  viewportOnce,
  viewportCard,
  transitions,
} from '../../utils/motionVariants';

interface Stage {
  num: string;
  title: string;
  subtitle: string;
  description: string;
  metric: string;
  icon: React.ElementType;
  techSpec: string;
}

const stages: Stage[] = [
  {
    num: '01',
    title: 'Query Ingestion',
    subtitle: 'SAP Domain Intent Parser',
    description: 'Deconstructs user input into T-Codes, SPRO customizing paths, billing concepts, and architectural sub-modules (SOM, CC, CI, FI-CA).',
    metric: '< 45ms Intent Classification',
    icon: BrainCircuit,
    techSpec: 'Multi-head intent classification with specialized SAP vocabulary dictionary and entity extraction.',
  },
  {
    num: '02',
    title: 'Hybrid Retrieval',
    subtitle: 'BM25 + Dense Vectors (pgvector)',
    description: 'Executes parallel searches: pgvector HNSW cosine index for conceptual semantics, plus BM25 for precise SAP transaction codes.',
    metric: 'Top-25 Balanced Candidates',
    icon: Database,
    techSpec: 'Dual-engine retrieval balancing semantic embedding similarity with exact technical keyword matching.',
  },
  {
    num: '03',
    title: 'Reciprocal Rank Fusion',
    subtitle: 'RRF Merging & De-duplication',
    description: 'Merges lexical and semantic rank lists mathematically, promoting chunks that satisfy both exact T-code and contextual needs.',
    metric: 'RRF Normalized Scoring',
    icon: Layers,
    techSpec: 'Reciprocal Rank Fusion k=60 parameter tuning to merge disparate search result spaces seamlessly.',
  },
  {
    num: '04',
    title: 'Neural Cross-Encoder',
    subtitle: 'Re-ranking & Context Trimming',
    description: 'Scores (query, passage) pairs through a neural re-ranker, discarding irrelevant guides and selecting top 3-5 high-relevance chunks.',
    metric: '0.94 Precision @ 5',
    icon: Filter,
    techSpec: 'Cross-attention deep transformer scoring full sequence interaction between user question and SAP manual.',
  },
  {
    num: '05',
    title: 'Zero-Hallucination Gate',
    subtitle: 'Grounding Verification Gate',
    description: 'Validates that retrieved SAP documentation provides sufficient evidence. If insufficient, triggers honest refusal instead of guessing.',
    metric: 'Strict Hallucination Gate',
    icon: ShieldCheck,
    techSpec: 'Deterministic grounding threshold check; queries lacking manual corroboration are gracefully declined.',
  },
  {
    num: '06',
    title: 'Grounded Generation',
    subtitle: 'Cited Streaming Response',
    description: 'Streams the verified answer with exact SPRO navigation breadcrumbs, required transaction codes, and clickable documentation references.',
    metric: '100% Traceable Citations',
    icon: Search,
    techSpec: 'Constraint-guided generation appending exact page, section, and document metadata citations to every response.',
  },
];

export const RagWorkflowSection: React.FC = () => {
  const [activeStage, setActiveStage] = useState<number>(0);

  return (
    <section className="rag-workflow-section" id="how-it-works">
      <div className="section-container">
        {/* Section Heading with Scroll-Triggered Reveal */}
        <motion.div
          className="section-header-center"
          variants={sectionHeaderVariant}
          initial="hidden"
          whileInView="visible"
          viewport={viewportOnce}
        >
          <div className="kicker-pill-subtle">
            <span className="pill-dot" />
            <span>THE RAG ARCHITECTURE</span>
          </div>

          <h2 className="section-title-large">
            Retrieve First.<br />
            <span className="hero-italic-serif">Answer Second.</span>
          </h2>

          <p className="section-subtitle-muted">
            Dense vector embeddings, BM25 lexical keyword search, and neural cross-encoder reranking eliminate guesswork and prevent hallucinations in complex SAP systems.
          </p>
        </motion.div>

        {/* 6-Stage Timeline Track with Staggered Entrance */}
        <motion.div
          className="workflow-stages-grid"
          variants={staggerContainer(0.09, 0.05)}
          initial="hidden"
          whileInView="visible"
          viewport={viewportCard}
        >
          {stages.map((stage, idx) => {
            const Icon = stage.icon;
            const isSelected = activeStage === idx;
            return (
              <motion.div
                key={stage.num}
                className={`workflow-stage-card ${isSelected ? 'active-card' : ''}`}
                onClick={() => setActiveStage(idx)}
                variants={cardVariant}
                whileHover={{ y: -4, transition: transitions.micro }}
              >
                <div className="stage-card-top">
                  <span className="stage-num-badge">{stage.num}</span>
                  <div className="stage-icon-circle">
                    <Icon size={16} />
                  </div>
                </div>

                <h3 className="stage-title">{stage.title}</h3>
                <span className="stage-subtitle">{stage.subtitle}</span>

                <p className="stage-desc">{stage.description}</p>

                <div className="stage-card-footer">
                  <span className="stage-metric">{stage.metric}</span>
                  {idx < stages.length - 1 && (
                    <span className="stage-next-arrow"><ArrowRight size={13} /></span>
                  )}
                </div>
              </motion.div>
            );
          })}
        </motion.div>

        {/* Detailed Stage Deep-Dive Bar with Smooth AnimatePresence Transition */}
        <motion.div
          className="stage-deep-dive-card"
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={viewportOnce}
          transition={transitions.smooth}
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={activeStage}
              variants={tabPanelVariant}
              initial="hidden"
              animate="visible"
              exit="exit"
              className="w-full flex flex-col md:flex-row md:items-center md:justify-between gap-6"
            >
              <div className="deep-dive-left">
                <span className="deep-dive-badge">STAGE {stages[activeStage].num} ARCHITECTURAL SPEC</span>
                <h4>{stages[activeStage].title} — {stages[activeStage].subtitle}</h4>
                <p>{stages[activeStage].techSpec}</p>
              </div>
              <div className="deep-dive-right">
                <div className="spec-metric-pill">
                  <span>Performance SLA:</span>
                  <strong>{stages[activeStage].metric}</strong>
                </div>
                <div className="spec-status-pill">
                  <CheckCircle size={14} className="text-orange" />
                  <span>Enterprise Guardrail Active</span>
                </div>
              </div>
            </motion.div>
          </AnimatePresence>
        </motion.div>
      </div>
    </section>
  );
};
