import React from 'react';
import { motion } from 'framer-motion';
import {
  Check,
  ShieldAlert,
  ShieldCheck,
  X,
} from 'lucide-react';
import {
  sectionHeaderVariant,
  staggerContainer,
  cardVariant,
  viewportOnce,
  viewportCard,
  transitions,
} from '../../utils/motionVariants';

interface ComparisonRow {
  dimension: string;
  genericAi: string;
  clyptusAi: string;
}

const comparisons: ComparisonRow[] = [
  {
    dimension: 'SPRO Navigation Breadcrumbs',
    genericAi: 'Guesses generic ERP paths, often combining ECC 6.0 with S/4HANA obsolete trees.',
    clyptusAi: 'Outputs exact, verified IMG navigation paths down to the leaf node customizing activity.',
  },
  {
    dimension: 'Transaction Codes (T-Codes)',
    genericAi: 'Frequently hallucinates deprecated transactions or non-existent prefix codes.',
    clyptusAi: 'Verified SAP BRIM transaction codes with explicit version compatibility flags.',
  },
  {
    dimension: 'Zero Hallucination Guarantee',
    genericAi: 'Speaks with false confidence when context is missing, fabricating configuration tables.',
    clyptusAi: 'Mathematically refuses to answer if enterprise documentation cannot corroborate the claim.',
  },
  {
    dimension: 'Clickable Documentation Citations',
    genericAi: 'No source attribution or generic references to public forums.',
    clyptusAi: 'Page-accurate citations linked to indexed SAP Solution Architecture & Config Guides.',
  },
  {
    dimension: 'Enterprise Data Isolation',
    genericAi: 'Public multi-tenant models that may absorb prompts into training corpora.',
    clyptusAi: 'Tenant-isolated PostgreSQL pgvector storage with role-based JWT access controls.',
  },
];

export const AiComparisonSection: React.FC = () => {
  return (
    <section className="ai-comparison-section">
      <div className="section-container">
        {/* Section Header with Scroll-Triggered Reveal */}
        <motion.div
          className="section-header-center"
          variants={sectionHeaderVariant}
          initial="hidden"
          whileInView="visible"
          viewport={viewportOnce}
        >
          <h2 className="section-title-large">
            Why Generic AI Fails in SAP.<br />
            <span className="hero-italic-serif">And Why Clyptus.AI Doesn't.</span>
          </h2>

          <p className="section-subtitle-muted">
            In mission-critical billing and revenue accounting, a single hallucinated customizing path can derail enterprise implementations. Grounding makes all the difference.
          </p>
        </motion.div>

        {/* Side-by-side Cards with Staggered Scroll-Triggered Reveal */}
        <motion.div
          className="comparison-cards-grid"
          variants={staggerContainer(0.14, 0.05)}
          initial="hidden"
          whileInView="visible"
          viewport={viewportCard}
        >
          {/* Column 1: Generic LLMs */}
          <motion.div
            className="comparison-col generic-col"
            variants={cardVariant}
            whileHover={{ y: -3, transition: transitions.micro }}
          >
            <div className="col-header">
              <div className="col-badge badge-danger">
                <ShieldAlert size={14} />
                <span>GENERIC AI / CHATGPT</span>
              </div>
              <h3>Parametric Guesswork</h3>
              <p>Relies on general training weights without verified SAP documentation context.</p>
            </div>

            <div className="col-points-list">
              {comparisons.map((row) => (
                <div key={row.dimension} className="point-item">
                  <div className="point-status-icon status-bad">
                    <X size={14} />
                  </div>
                  <div>
                    <strong>{row.dimension}</strong>
                    <p>{row.genericAi}</p>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Column 2: Clyptus.AI */}
          <motion.div
            className="comparison-col clyptus-col"
            variants={cardVariant}
            whileHover={{ y: -4, transition: transitions.micro }}
          >
            <div className="col-header">
              <div className="col-badge badge-brand">
                <ShieldCheck size={14} />
                <span>CLYPTUS.AI PLATFORM</span>
              </div>
              <h3>Developer-Managed RAG</h3>
              <p>Grounds every generation strictly in indexed enterprise SAP manuals.</p>
            </div>

            <div className="col-points-list">
              {comparisons.map((row) => (
                <div key={row.dimension} className="point-item">
                  <div className="point-status-icon status-good">
                    <Check size={14} />
                  </div>
                  <div>
                    <strong>{row.dimension}</strong>
                    <p>{row.clyptusAi}</p>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
};
