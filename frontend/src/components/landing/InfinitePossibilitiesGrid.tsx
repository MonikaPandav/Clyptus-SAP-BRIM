import React from 'react';
import { motion } from 'framer-motion';
import {
  CheckCircle2,
  FileCode,
  FileText,
  GitBranch,
  Layers,
  Lock,
  Network,
  Search,
  Server,
  Shield,
  ShieldCheck,
  Sparkles,
  Workflow,
  Zap,
} from 'lucide-react';
import {
  sectionHeaderVariant,
  staggerContainer,
  cardVariant,
  viewportOnce,
  viewportCard,
  transitions,
} from '../../utils/motionVariants';

export const InfinitePossibilitiesGrid: React.FC = () => {
  return (
    <section className="infinite-possibilities-section" id="features">
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
            One Knowledge Platform.<br />
            <span className="hero-title-accent">Infinite SAP Possibilities.</span>
          </h2>

          <p className="section-subtitle-muted">
            Connect enterprise SAP documentation, configuration dictionaries, and consulting teams into one authoritative, hallucination-free AI workspace.
          </p>
        </motion.div>

        {/* Feature Cards Grid with Staggered Scroll-Triggered Reveal */}
        <motion.div
          className="possibilities-grid"
          variants={staggerContainer(0.12, 0.05)}
          initial="hidden"
          whileInView="visible"
          viewport={viewportCard}
        >
          {/* Card 1: Secure Multi-User SAP Access */}
          <motion.div
            className="possibility-card card-multi-user"
            variants={cardVariant}
            whileHover={{ y: -4, transition: transitions.micro }}
          >
            <div className="card-top-content">
              <span className="card-category-tag">ACCESS CONTROL</span>
              <h3 className="card-headline">Secure Multi-User SAP Access</h3>
              <p className="card-description">
                Connect multiple consultants, functional leads, and architects into one controlled AI workspace. Every request is processed through an encrypted system, ensuring privacy, traceability, and secure role-based permissions.
              </p>
            </div>

            <div className="card-multi-user-visual">
              <div className="user-workspace-preview">
                <div className="workspace-header">
                  <span className="ws-dot" />
                  <strong>Enterprise Billing Team (Tenant #824)</strong>
                  <span className="ws-badge">Active SLA</span>
                </div>
                <div className="user-role-row">
                  <div className="user-chip">
                    <div className="avatar-letter bg-orange-subtle">AC</div>
                    <div>
                      <strong>Senior Billing Architect</strong>
                      <span>Convergent Invoicing (CI) · Admin</span>
                    </div>
                  </div>
                  <span className="status-pill-green">Verified</span>
                </div>

                <div className="user-role-row">
                  <div className="user-chip">
                    <div className="avatar-letter bg-amber-subtle">MK</div>
                    <div>
                      <strong>FI-CA Lead Consultant</strong>
                      <span>Subledger Accounting · Analyst</span>
                    </div>
                  </div>
                  <span className="status-pill-green">Verified</span>
                </div>

                <div className="workspace-security-footer">
                  <Lock size={12} />
                  <span>End-to-End JWT Auth &amp; Audit Traceability</span>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Card 2: Connect with Your Favorite Tools (Orbital Arcs) */}
          <motion.div
            className="possibility-card card-orbital-tools"
            variants={cardVariant}
            whileHover={{ y: -4, transition: transitions.micro }}
          >
            <div className="card-top-content">
              <span className="card-category-tag">ECOSYSTEM INTEGRATION</span>
              <h3 className="card-headline">Connect with Your Enterprise Tools</h3>
              <p className="card-description">
                Integrate seamlessly with documentation repositories, ticket systems, and enterprise knowledge stores. Ground your AI in your actual implementation blueprints.
              </p>
            </div>

            {/* Concentric Dotted Orbital Arc Visualization */}
            <div className="card-orbital-visual">
              <div className="orbital-arcs-container">
                {/* Center Core Badge */}
                <motion.div
                  className="orbital-core-badge"
                  animate={{ scale: [1, 1.04, 1] }}
                  transition={{ duration: 3.5, repeat: Infinity, ease: 'easeInOut' }}
                >
                  <Sparkles size={18} />
                  <span>Clyptus</span>
                </motion.div>

                {/* Orbit 1 */}
                <div className="orbital-ring ring-1" />
                {/* Orbit 2 */}
                <div className="orbital-ring ring-2" />
                {/* Orbit 3 */}
                <div className="orbital-ring ring-3" />

                {/* Floating Tool Badges along the concentric arcs with subtle float animation */}
                <motion.div
                  className="orbital-tool-node node-sap"
                  title="SAP S/4HANA"
                  animate={{ y: [0, -4, 0] }}
                  transition={{ duration: 3.8, repeat: Infinity, ease: 'easeInOut' }}
                >
                  <Server size={14} />
                  <span>S/4HANA</span>
                </motion.div>

                <motion.div
                  className="orbital-tool-node node-confluence"
                  title="SAP Fiori / GUI"
                  animate={{ y: [0, 4, 0] }}
                  transition={{ duration: 4.2, repeat: Infinity, ease: 'easeInOut', delay: 0.5 }}
                >
                  <Layers size={14} />
                  <span>Fiori</span>
                </motion.div>

                <motion.div
                  className="orbital-tool-node node-jira"
                  title="Jira Implementation Issues"
                  animate={{ y: [0, -3, 0] }}
                  transition={{ duration: 3.5, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
                >
                  <FileText size={14} />
                  <span>Jira</span>
                </motion.div>

                <motion.div
                  className="orbital-tool-node node-github"
                  title="Confluence Runbooks"
                  animate={{ y: [0, 3, 0] }}
                  transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut', delay: 1.5 }}
                >
                  <GitBranch size={14} />
                  <span>Git/Docs</span>
                </motion.div>

                <motion.div
                  className="orbital-tool-node node-slack"
                  title="Enterprise Messaging"
                  animate={{ y: [0, -4, 0] }}
                  transition={{ duration: 4.5, repeat: Infinity, ease: 'easeInOut', delay: 0.8 }}
                >
                  <Network size={14} />
                  <span>ServiceNow</span>
                </motion.div>
              </div>
            </div>
          </motion.div>

          {/* Card 3: Encrypted Workflow Infrastructure (Wide Timeline Card) */}
          <motion.div
            className="possibility-card card-infrastructure-timeline"
            variants={cardVariant}
            whileHover={{ y: -3, transition: transitions.micro }}
          >
            <div className="card-top-content">
              <span className="card-category-tag">DATA CONFIDENCE</span>
              <h3 className="card-headline">Encrypted Workflow Infrastructure</h3>
              <p className="card-description">
                Every workflow runs through protected AI pipelines with encrypted processing layers. Designed for enterprise organizations that require absolute reliability, deterministic SPRO retrieval, and mathematical grounding.
              </p>
            </div>

            {/* Timeline Pipeline Visualization */}
            <div className="card-timeline-visual">
              <div className="timeline-pipeline-track">
                <div className="timeline-step-node">
                  <div className="node-icon-box"><FileCode size={14} /></div>
                  <span className="node-label">01 Ingestion</span>
                  <span className="node-sub">Curated SAP Guides</span>
                </div>

                <div className="timeline-connector-line" />

                <div className="timeline-step-node">
                  <div className="node-icon-box"><Search size={14} /></div>
                  <span className="node-label">02 Hybrid Search</span>
                  <span className="node-sub">Dense + BM25 Lexical</span>
                </div>

                <div className="timeline-connector-line" />

                <div className="timeline-step-node">
                  <div className="node-icon-box active-pulse"><Zap size={14} /></div>
                  <span className="node-label">03 Neural Rerank</span>
                  <span className="node-sub">Cross-Encoder &lt;250ms</span>
                </div>

                <div className="timeline-connector-line" />

                <div className="timeline-step-node">
                  <div className="node-icon-box"><ShieldCheck size={14} /></div>
                  <span className="node-label">04 Grounding</span>
                  <span className="node-sub">Strict Hallucination Gate</span>
                </div>

                <div className="timeline-connector-line" />

                <div className="timeline-step-node">
                  <div className="node-icon-box"><CheckCircle2 size={14} /></div>
                  <span className="node-label">05 Verified Answer</span>
                  <span className="node-sub">Clickable Citations</span>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Card 4: Smart Workflows */}
          <motion.div
            className="possibility-card card-compact"
            variants={cardVariant}
            whileHover={{ y: -4, transition: transitions.micro }}
          >
            <div className="compact-icon-box bg-orange">
              <Workflow size={20} className="text-white" />
            </div>
            <h4 className="compact-title">Smart Workflows</h4>
            <p className="compact-desc">
              Accelerate blueprinting and troubleshooting across Convergent Invoicing, Charging, and FI-CA contract accounts without digging through hundreds of PDF manuals.
            </p>
            <div className="compact-feature-list">
              <span><CheckCircle2 size={13} /> SPRO navigation breadcrumbs</span>
              <span><CheckCircle2 size={13} /> S/4HANA Transaction codes</span>
            </div>
          </motion.div>

          {/* Card 5: Secure AI */}
          <motion.div
            className="possibility-card card-compact"
            variants={cardVariant}
            whileHover={{ y: -4, transition: transitions.micro }}
          >
            <div className="compact-icon-box bg-amber">
              <Shield size={20} className="text-white" />
            </div>
            <h4 className="compact-title">Secure AI &amp; Zero Hallucination</h4>
            <p className="compact-desc">
              When retrieved documentation does not substantiate an answer, Clyptus.AI alerts you and refuses to hallucinate fictitious SAP configuration steps.
            </p>
            <div className="compact-feature-list">
              <span><CheckCircle2 size={13} /> Mathematical refusal trigger</span>
              <span><CheckCircle2 size={13} /> Admin-controlled knowledge base</span>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
};
