import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowUpRight,
  CheckCircle2,
  Copy,
  Sparkles,
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

interface SamplePrompt {
  id: string;
  category: string;
  question: string;
  sproOrTcode: string;
  summary: string;
}

const samplePrompts: SamplePrompt[] = [
  {
    id: 'p1',
    category: 'Billing & Invoicing',
    question: 'How do billable items get grouped into a single billing document in SAP CI?',
    sproOrTcode: 'SPRO: Convergent Invoicing > Basic Data > Billable Item Classes > Define Aggregation Criteria',
    summary: 'Aggregation is governed by billing process definitions and grouping variants. Header fields (VKONT, GPART, WAERS) are evaluated alongside customizable grouping characteristics to combine raw BITs into consolidated invoice line items.',
  },
  {
    id: 'p2',
    category: 'Charging & Rating',
    question: 'Where is the rating logic defined for recurring monthly fees vs tiered usage in SAP CC?',
    sproOrTcode: 'Core Tool: Price Plans > Reusable Charges > Tiered Rate Trees (Numeric Component)',
    summary: 'Recurring charges are triggered via recurring events with periodic chronologies. Usage charges evaluate consumption metrics through decision trees and comparator branches in the Core Tool charge plan.',
  },
  {
    id: 'p3',
    category: 'Architecture & Process',
    question: 'What is the end-to-end integration path from Subscription Order Management to SAP FI-CA?',
    sproOrTcode: 'Architecture: SAP CM -> SAP CC -> SAP CI -> SAP FI-CA',
    summary: 'Order capture in SOM distributes technical provider contracts to FI-CA and charge plans to CC. Usage passes through CM to CC for rating, into CI for aggregation/billing, and finally posts as open items in FI-CA.',
  },
  {
    id: 'p4',
    category: 'FI-CA Subledger',
    question: 'How do clearing variants resolve open invoices when a customer makes a partial payment in FI-CA?',
    sproOrTcode: 'SPRO: Contract Accounts > Basic Functions > Open Item Management > Define Clearing Variants',
    summary: 'Clearing control matches incoming cash against open items based on clearing categories, due date sorting, and payment amount tolerances specified in clearing variant configuration.',
  },
  {
    id: 'p5',
    category: 'Billing & Invoicing',
    question: 'What transaction code is used to generate DDIC structures for a billable item class?',
    sproOrTcode: 'T-Code: FKKBIXCIT_CONF',
    summary: 'Execute FKKBIXCIT_CONF after maintaining interface components. The transaction creates table structures (/1BIX/...), database indices, and generation statuses required for high-volume database storage.',
  },
  {
    id: 'p6',
    category: 'Subscription (SOM)',
    question: 'How do discount agreements propagate from SOM master agreements to CC charging trees?',
    sproOrTcode: 'SPRO: CRM > Master Data > Products > Define Subscription Settings for CC Cross-Catalog Mapping',
    summary: 'Master agreements store discount percentages as parameters in provider contract items. These parameters are transferred during RFC replication to override price table lookups within SAP CC charging logic.',
  },
];

const categories = ['All Scenarios', 'Billing & Invoicing', 'Charging & Rating', 'FI-CA Subledger', 'Architecture & Process', 'Subscription (SOM)'];

export const QuestionPromptBank: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('All Scenarios');
  const [selectedPrompt, setSelectedPrompt] = useState<SamplePrompt>(samplePrompts[0]);
  const [copied, setCopied] = useState<boolean>(false);

  const filteredPrompts = activeTab === 'All Scenarios'
    ? samplePrompts
    : samplePrompts.filter((p) => p.category === activeTab);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className="prompt-bank-section">
      <div className="section-container">
        {/* Section Header with Scroll-Triggered Reveal */}
        <motion.div
          className="section-header-center"
          variants={sectionHeaderVariant}
          initial="hidden"
          whileInView="visible"
          viewport={viewportOnce}
        >
          <div className="kicker-pill-subtle">
            <span className="pill-dot" />
            <span>PRACTICAL CONSULTING PROMPTS</span>
          </div>

          <h2 className="section-title-large">
            Ask The Exact Question<br />
            <span className="hero-italic-serif">Already On Your Desk.</span>
          </h2>

          <p className="section-subtitle-muted">
            Click any real-world SAP scenario below to preview how Clyptus.AI structures the grounded answer, transaction codes, and SPRO path.
          </p>
        </motion.div>

        {/* Category Filter Pills */}
        <motion.div
          className="prompt-filter-tabs"
          variants={staggerContainer(0.04, 0.02)}
          initial="hidden"
          whileInView="visible"
          viewport={viewportOnce}
        >
          {categories.map((cat) => (
            <motion.button
              key={cat}
              className={`filter-tab-btn ${activeTab === cat ? 'active' : ''}`}
              onClick={() => setActiveTab(cat)}
              whileHover={{ y: -1 }}
              whileTap={{ scale: 0.97 }}
            >
              <span>{cat}</span>
            </motion.button>
          ))}
        </motion.div>

        {/* 2-Column Layout: Prompt Chips Left, Grounded Inspector Right */}
        <div className="prompt-sandbox-grid">
          {/* Left Column: Chips with Staggered Scroll-Triggered Reveal */}
          <motion.div
            className="prompt-chips-list"
            variants={staggerContainer(0.07, 0.05)}
            initial="hidden"
            whileInView="visible"
            viewport={viewportCard}
          >
            {filteredPrompts.map((p, index) => {
              const isSelected = selectedPrompt.id === p.id;
              return (
                <motion.div
                  key={p.id}
                  className={`prompt-chip-card ${isSelected ? 'selected-chip' : ''}`}
                  onClick={() => setSelectedPrompt(p)}
                  variants={cardVariant}
                  whileHover={{ x: 4, transition: transitions.micro }}
                >
                  <div className="chip-meta-row">
                    <span className="chip-index">0{index + 1}</span>
                    <span className="chip-category">{p.category}</span>
                  </div>
                  <p className="chip-question">{p.question}</p>
                  <span className="chip-arrow"><ArrowUpRight size={14} /></span>
                </motion.div>
              );
            })}
          </motion.div>

          {/* Right Column: Live Inspector Card with AnimatePresence */}
          <motion.div
            className="prompt-inspector-card"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={viewportOnce}
            transition={transitions.smooth}
          >
            <div className="inspector-header">
              <div className="inspector-badge">
                <Sparkles size={13} />
                <span>GROUNDED PREVIEW</span>
              </div>
              <button
                className="inspector-copy-btn"
                onClick={() => handleCopy(selectedPrompt.question)}
              >
                <Copy size={12} />
                <span>{copied ? 'Copied' : 'Copy Question'}</span>
              </button>
            </div>

            <AnimatePresence mode="wait">
              <motion.div
                key={selectedPrompt.id}
                variants={tabPanelVariant}
                initial="hidden"
                animate="visible"
                exit="exit"
                className="inspector-body"
              >
                <span className="inspector-label">QUERY</span>
                <h4 className="inspector-question">{selectedPrompt.question}</h4>

                <div className="inspector-divider" />

                <span className="inspector-label">CLYPTUS.AI GROUNDED SYNTHESIS</span>
                <p className="inspector-summary">{selectedPrompt.summary}</p>

                <div className="inspector-spro-box">
                  <span className="spro-box-title">CONFIGURATION / T-CODE ANCHOR</span>
                  <code>{selectedPrompt.sproOrTcode}</code>
                </div>

                <div className="inspector-footer">
                  <CheckCircle2 size={13} className="text-orange" />
                  <span>Mathematically verified against official SAP implementation documentation</span>
                </div>
              </motion.div>
            </AnimatePresence>
          </motion.div>
        </div>
      </div>
    </section>
  );
};
