import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowRight,
  CheckCircle2,
} from 'lucide-react';
import {
  sectionHeaderVariant,
  staggerContainer,
  tabPanelVariant,
  viewportOnce,
  viewportCard,
  transitions,
} from '../../utils/motionVariants';

interface BrimModule {
  id: string;
  name: string;
  abbreviation: string;
  tagline: string;
  overview: string;
  keyTcodes: string[];
  sproFocus: string;
  commonQuestions: string[];
}

const modules: BrimModule[] = [
  {
    id: 'som',
    name: 'Subscription Order Management',
    abbreviation: 'SAP SOM',
    tagline: 'Order Capture, Solution Bundles & Master Agreements',
    overview: 'Centralizes the commercial definition of subscription products, cross-catalog bundles, and contract life-cycle events. Translates CRM orders into technical provider contracts in FI-CA and rating contracts in CC.',
    keyTcodes: ['CRMD_ORDER', 'SOM_CONTRACT_MON', 'COMM_HIERARCHY'],
    sproFocus: 'Customer Relationship Management > Master Data > Products > Define Subscription Settings',
    commonQuestions: [
      'How to map partner functions on Provider Orders to FI-CA contract accounts?',
      'Configuring distribution chains for complex subscription products and hardware combos.',
    ],
  },
  {
    id: 'cc',
    name: 'Convergent Charging',
    abbreviation: 'SAP CC',
    tagline: 'High-Throughput Real-Time Rating & Charging Engine',
    overview: 'High-throughput rating and charging engine processing billions of usage consumption events per second. Evaluates charged items, executes pricing logic trees, and manages prepaid/postpaid subscriber balances.',
    keyTcodes: ['Core Tool (GUI)', 'Admin+ CLI', 'BART Server Monitor'],
    sproFocus: 'Integration via RFC / Web Services with SAP CI; Charged Item (CIT) classes mapping.',
    commonQuestions: [
      'How to design tiered volume charging plans with recurring reset periods in Core Tool?',
      'Resolving CIT storage buffer overflow errors between CC and CI ingestion queues.',
    ],
  },
  {
    id: 'ci',
    name: 'Convergent Invoicing',
    abbreviation: 'SAP CI',
    tagline: 'Billable Item Processing, Aggregation & Invoicing',
    overview: 'Aggregates billable items (BITs) from multiple upstream mediation sources, applies billing rules, generates customer-facing invoices, and creates open posting items directly into FI-CA contract subledgers.',
    keyTcodes: ['FKKBIXCIT_CONF', 'FKKBIX_BIT_MON', 'FKKBIX_BILLDOC_DISP', 'FKKINV_S'],
    sproFocus: 'Financial Accounting > Contract Accounts > Convergent Invoicing > Basic Data > Billable Item Classes',
    commonQuestions: [
      'Step-by-step SPRO guide to activate new custom fields on /1BIX/ generated DDIC tables.',
      'How to trigger selective invoicing reversing individual billing documents without cancelling BITs.',
    ],
  },
  {
    id: 'fica',
    name: 'Contract Accounts Receivable and Payable',
    abbreviation: 'SAP FI-CA',
    tagline: 'High-Volume Enterprise Subledger Accounting',
    overview: 'Subledger designed specifically for millions of B2C/B2B consumer accounts. Manages automatic payment runs, multi-stage dunning procedures, revenue recognition, dispute workflows, and mass clearing.',
    keyTcodes: ['FP03D', 'FPY1', 'FPVA / FPVB', 'FPP3', 'FKK_SEC_MON'],
    sproFocus: 'Financial Accounting > Contract Accounts Receivable and Payable > Basic Functions > Open Item Management',
    commonQuestions: [
      'How do clearing categories and clearing variants resolve installment plan priority?',
      'Configuring multi-currency dunning procedures with automated collection agency handoff.',
    ],
  },
  {
    id: 'cm',
    name: 'Convergent Mediation',
    abbreviation: 'SAP CM (DigitalRoute)',
    tagline: 'Carrier-Grade Mediation & Usage Normalization',
    overview: 'Collects raw usage logs, CDRs, and telemetry data from network switches, cloud APIs, and IoT devices. Normalizes, enriches, deduplicates, and formats clean transactions for downstream SAP CC rating.',
    keyTcodes: ['Desktop Client', 'Execution Plans', 'Node Monitor'],
    sproFocus: 'Integration endpoints to SAP CC Service Controller; APL scripting configuration.',
    commonQuestions: [
      'Configuring duplicate detection algorithms on massive streaming CDR telemetry batches.',
      'How to route abnormal usage records into exception quarantine workflows for manual review.',
    ],
  },
];

export const BrimModuleExplorer: React.FC = () => {
  const [selectedModule, setSelectedModule] = useState<BrimModule>(modules[0]);

  return (
    <section className="brim-explorer-section">
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
            Built For SAP.<br />
            <span className="hero-italic-serif">Deeply Focused on BRIM.</span>
          </h2>

          <p className="section-subtitle-muted">
            End-to-end expertise across all 5 core pillars of the SAP Billing and Revenue Innovation Management ecosystem.
          </p>
        </motion.div>

        {/* Tab Buttons for Modules with Staggered Reveal */}
        <motion.div
          className="module-tabs-row"
          variants={staggerContainer(0.06, 0.04)}
          initial="hidden"
          whileInView="visible"
          viewport={viewportCard}
        >
          {modules.map((mod) => (
            <motion.button
              key={mod.id}
              className={`module-tab-btn ${selectedModule.id === mod.id ? 'active' : ''}`}
              onClick={() => setSelectedModule(mod)}
              whileHover={{ y: -2, transition: transitions.micro }}
              whileTap={{ scale: 0.98 }}
            >
              <span className="mod-tab-abbr">{mod.abbreviation}</span>
              <span className="mod-tab-name">{mod.name}</span>
            </motion.button>
          ))}
        </motion.div>

        {/* Active Module Card with Smooth Cross-Fade Transition */}
        <motion.div
          className="module-display-card"
          initial={{ opacity: 0, y: 22 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={viewportOnce}
          transition={transitions.smooth}
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={selectedModule.id}
              variants={tabPanelVariant}
              initial="hidden"
              animate="visible"
              exit="exit"
            >
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
            </motion.div>
          </AnimatePresence>
        </motion.div>
      </div>
    </section>
  );
};
