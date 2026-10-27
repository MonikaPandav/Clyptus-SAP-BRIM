import React, { useState } from 'react';
import { ArrowRight, CheckCircle2 } from 'lucide-react';


interface BrimModule {
  id: string;
  abbreviation: string;
  name: string;
  tagline: string;
  overview: string;
  keyTcodes: string[];
  sproFocus: string;
  commonQuestions: string[];
}

const modules: BrimModule[] = [
  {
    id: 'ci',
    abbreviation: 'CI',
    name: 'Convergent Invoicing',
    tagline: 'High-Volume Aggregation, Rating Ingestion & Billing',
    overview: 'Ingests billable items (BITs) from Convergent Charging or mediation, applies aggregation and billing rules, and creates billing and invoicing documents for FI-CA subledger posting.',
    keyTcodes: ['FKKBIXCIT_CONF', 'FKKBIX_BIT_MON', 'FKKBIX_BILL_M', 'FKKBIX_INV_M'],
    sproFocus: 'Financial Accounting > Contract Accounts A/R & A/P > Convergent Invoicing > Basic Data > Billable Item Classes & Billing Processes',
    commonQuestions: [
      'How to resolve BIT class generation errors in FKKBIXCIT_CONF?',
      'How to configure billable item aggregation rules per contract account?',
      'How does invoice document grouping prevent duplicate line item creation?',
    ],
  },
  {
    id: 'cc',
    abbreviation: 'CC',
    name: 'Convergent Charging',
    tagline: 'Real-Time Dynamic Rating, Pricing & Subscriber Balances',
    overview: 'Performs millisecond-speed rating and pricing for telecommunications, digital services, and utility events using price plans, charge plans, allowance logic, and refill mechanisms.',
    keyTcodes: ['Core Tool', 'Admin+ / Setup+', 'BART+', 'CAT Tool'],
    sproFocus: 'Integration via Web Services (JCo) with S/4HANA Convergent Invoicing and SOM Provider Agreements',
    commonQuestions: [
      'How does allowance logic interact with recurring monthly charges?',
      'How are charged items mapped and transmitted to S/4HANA billable item interfaces?',
      'Best practices for configuring tier-based pricing in CC Core Tool?',
    ],
  },
  {
    id: 'fica',
    abbreviation: 'FI-CA',
    name: 'Contract Accounts A/R & A/P',
    tagline: 'Subledger for Millions of Customers & High-Volume Payments',
    overview: 'High-performance subledger designed for mass data processing. Handles customer open item management, automatic clearing runs, dunning, dispute handling, and tax calculation.',
    keyTcodes: ['FPY1', 'FPE2', 'FPL9', 'FPMA', 'FPDOC'],
    sproFocus: 'Financial Accounting > Contract Accounts A/R & A/P > Basic Functions > Open Item Management & Clearing Control',
    commonQuestions: [
      'Why is an open item not cleared automatically during the FPY1 payment run?',
      'How are clearing variants configured for installment plans?',
      'How to configure posting area 0100 and document type assignments in SPRO?',
    ],
  },
  {
    id: 'som',
    abbreviation: 'SOM',
    name: 'Subscription Order Management',
    tagline: 'Order Capture, Master Agreements & Lifecycle Management',
    overview: 'Captures and manages recurring product bundles, subscription contracts, master agreements, and cross-catalog mapping, replicating contracts into S/4HANA and CC.',
    keyTcodes: ['CRMD_ORDER', 'FKKORD1', 'ODI Monitor', 'CVI Cockpit'],
    sproFocus: 'Customer Relationship Management > Master Data > Products & Order Distribution Infrastructure (ODI)',
    commonQuestions: [
      'How to trace contract replication failures in the ODI monitor?',
      'How are change processes (upgrades, downgrades, cancellations) mapped to CC?',
      'How to maintain technical resource IDs and sharing contracts in SOM?',
    ],
  },
  {
    id: 'cm',
    abbreviation: 'CM',
    name: 'Convergent Mediation',
    tagline: 'Raw CDR Ingestion, Duplicate Filtering & Normalization',
    overview: 'Collects unstructured usage records and event streams from network nodes, IoT devices, or cloud platforms, formats them, and dispatches them to Convergent Charging.',
    keyTcodes: ['Mediation Zone Desktop', 'Workflow Engine', 'Node Config'],
    sproFocus: 'Integration adapters: Diameter, RADIUS, REST, Kafka, and SAP CC Rating Engine',
    commonQuestions: [
      'How to configure deduplication filters for high-speed streaming events?',
      'How are aggregated record structures mapped into CC chargeable item formats?',
      'How to set up offline storage buffering during charging engine maintenance?',
    ],
  },
];

export const BrimModuleExplorer: React.FC = () => {
  const [selectedModule, setSelectedModule] = useState<BrimModule>(modules[0]);

  return (
    <section className="brim-explorer-section">
      <div className="section-container">
        {/* Section Header */}
        <div className="section-header-center">
          <div className="kicker-pill-subtle">
            <span className="pill-dot" />
            <span>FULL ARCHITECTURAL COVERAGE</span>
          </div>

          <h2 className="section-title-large">
            Built For SAP.<br />
            <span className="hero-italic-serif">Deeply Focused on BRIM.</span>
          </h2>

          <p className="section-subtitle-muted">
            End-to-end expertise across all 5 core pillars of the SAP Billing and Revenue Innovation Management ecosystem.
          </p>
        </div>

        {/* Tab Buttons for Modules */}
        <div className="module-tabs-row">
          {modules.map((mod) => (
            <button
              key={mod.id}
              className={`module-tab-btn ${selectedModule.id === mod.id ? 'active' : ''}`}
              onClick={() => setSelectedModule(mod)}
            >
              <span className="mod-tab-abbr">{mod.abbreviation}</span>
              <span className="mod-tab-name">{mod.name}</span>
            </button>
          ))}
        </div>

        {/* Active Module Card */}
        <div className="module-display-card">
          <div className="module-display-header">
            <div>
              <span className="display-abbr-badge">{selectedModule.abbreviation}</span>
              <h3 className="display-title">{selectedModule.name}</h3>
              <p className="display-tagline">{selectedModule.tagline}</p>
            </div>
            <div className="display-status-chip">
              <CheckCircle2 size={14} className="text-orange" />
              <span>100% Curated Manuals Indexed</span>
            </div>
          </div>

          <p className="module-overview-text">{selectedModule.overview}</p>

          <div className="module-details-grid">
            {/* T-Codes Box */}
            <div className="detail-box">
              <span className="box-label">KEY SAP TRANSACTION CODES</span>
              <div className="tcode-chips-wrap">
                {selectedModule.keyTcodes.map((tc) => (
                  <span key={tc} className="tcode-badge">
                    <code>{tc}</code>
                  </span>
                ))}
              </div>
            </div>

            {/* SPRO Customizing Path */}
            <div className="detail-box">
              <span className="box-label">SPRO CUSTOMIZING ANCHOR</span>
              <div className="spro-anchor-box">
                <code>{selectedModule.sproFocus}</code>
              </div>
            </div>
          </div>

          {/* Common Consulting Doubts Solved */}
          <div className="module-questions-box">
            <span className="box-label">COMMON CONSULTING DOUBTS ANSWERED BY CLYPTUS.AI</span>
            <ul className="questions-list">
              {selectedModule.commonQuestions.map((q, i) => (
                <li key={i}>
                  <ArrowRight size={13} className="text-orange flex-none" />
                  <span>{q}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
};
