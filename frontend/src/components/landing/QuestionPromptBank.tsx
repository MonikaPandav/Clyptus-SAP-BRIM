import React, { useState } from 'react';
import { ArrowUpRight, CheckCircle2, Copy, Sparkles } from 'lucide-react';

interface PromptItem {
  id: string;
  category: 'Configuration' | 'Troubleshooting' | 'Transactions' | 'Processes';
  question: string;
  summary: string;
  sproOrTcode: string;
}

const samplePrompts: PromptItem[] = [
  {
    id: 'p1',
    category: 'Configuration',
    question: 'What is transaction FKKBIXCIT_CONF used for in Convergent Invoicing?',
    summary: 'Used to configure and generate Billable Item Classes (/1BIX/ structures and DB tables) after defining field catalogs.',
    sproOrTcode: 'T-Code: FKKBIXCIT_CONF | SPRO: Convergent Invoicing > Basic Data > Billable Item Classes',
  },
  {
    id: 'p2',
    category: 'Configuration',
    question: 'Where are document types and posting areas configured in FI-CA?',
    summary: 'Document types define number ranges and clearing behavior, maintained in Posting Area 0100 under FI-CA Document settings.',
    sproOrTcode: 'SPRO: Contract Accounts A/R & A/P > Basic Functions > Postings and Documents > Document > Maintain Document Types',
  },
  {
    id: 'p3',
    category: 'Processes',
    question: 'Explain the complete BRIM rating, billing, and invoicing flow.',
    summary: 'Mediation CDRs are priced by CC, stored as BITs in CI, grouped into Billing Documents, and converted into FI-CA subledger Invoices.',
    sproOrTcode: 'Architecture: SAP CM -> SAP CC -> SAP CI -> SAP FI-CA',
  },
  {
    id: 'p4',
    category: 'Troubleshooting',
    question: 'Billing run completed successfully but no invoice document was generated. What should I check?',
    summary: 'Check invoicing locks in the billing document header, verify invoicing category assignment in contract account master, and check invoicing log.',
    sproOrTcode: 'T-Codes: FKKBIX_BILL_M, FKKBIX_INV_M | Table: DFKKBIXBIT_IT',
  },
  {
    id: 'p5',
    category: 'Transactions',
    question: 'What is the purpose of transaction FKKBIX_BIT_MON?',
    summary: 'Billable Item Monitor: Inspect, analyze status (raw, billable, billed), and simulate billing for billable items across all classes.',
    sproOrTcode: 'T-Code: FKKBIX_BIT_MON',
  },
  {
    id: 'p6',
    category: 'Troubleshooting',
    question: 'Why was an open invoice item excluded from the payment run (FPY1)?',
    summary: 'Exclusion is caused by item-level payment/clearing locks, missing bank details, or failure to meet minimum payment tolerances.',
    sproOrTcode: 'T-Codes: FPY1, FPE2 | SPRO: Clearing Control > Specifications for Clearing Types',
  },
];

export const QuestionPromptBank: React.FC = () => {
  const [selectedPrompt, setSelectedPrompt] = useState<PromptItem>(samplePrompts[0]);
  const [activeTab, setActiveTab] = useState<string>('All');
  const [copied, setCopied] = useState<boolean>(false);

  const categories = ['All', 'Configuration', 'Troubleshooting', 'Transactions', 'Processes'];

  const filteredPrompts = activeTab === 'All'
    ? samplePrompts
    : samplePrompts.filter((p) => p.category === activeTab);

  const handleCopy = (text: string) => {
    navigator.clipboard?.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className="prompt-bank-section">
      <div className="section-container">
        {/* Section Header */}
        <div className="section-header-center">
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
        </div>

        {/* Category Filter Pills */}
        <div className="prompt-filter-tabs">
          {categories.map((cat) => (
            <button
              key={cat}
              className={`filter-tab-btn ${activeTab === cat ? 'active' : ''}`}
              onClick={() => setActiveTab(cat)}
            >
              <span>{cat}</span>
            </button>
          ))}
        </div>

        {/* 2-Column Layout: Prompt Chips Left, Grounded Inspector Right */}
        <div className="prompt-sandbox-grid">
          {/* Left Column: Chips */}
          <div className="prompt-chips-list">
            {filteredPrompts.map((p, index) => {
              const isSelected = selectedPrompt.id === p.id;
              return (
                <div
                  key={p.id}
                  className={`prompt-chip-card ${isSelected ? 'selected-chip' : ''}`}
                  onClick={() => setSelectedPrompt(p)}
                >
                  <div className="chip-meta-row">
                    <span className="chip-index">0{index + 1}</span>
                    <span className="chip-category">{p.category}</span>
                  </div>
                  <p className="chip-question">{p.question}</p>
                  <span className="chip-arrow"><ArrowUpRight size={14} /></span>
                </div>
              );
            })}
          </div>

          {/* Right Column: Live Inspector Card */}
          <div className="prompt-inspector-card">
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

            <div className="inspector-body">
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
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
