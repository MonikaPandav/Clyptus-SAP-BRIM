import React from 'react';
import { motion } from 'framer-motion';
import {
  ArrowDown,
  ArrowRight,
  ArrowUpRight,
  BookOpen,
  Boxes,
  Compass,
  FileText,
  Gauge,
  MessageCircle,
  Search,
  ShieldCheck,
  Sparkles,
  Workflow,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { FaqSection } from '../components/landing/FaqSection';
import { VideoShowcase } from '../components/landing/VideoShowcase';
import { Footer } from '../components/footer/Footer';
import { PublicNav } from '../components/navbar/PublicNav';
import { PageMeta } from '../components/ui/PageMeta';

const brimAreas = [
  { abbreviation: 'CM', title: 'Convergent Mediation', icon: Workflow },
  { abbreviation: 'CC', title: 'Convergent Charging', icon: Gauge },
  { abbreviation: 'CI', title: 'Convergent Invoicing', icon: FileText },
  { abbreviation: 'FI-CA', title: 'Contract Accounts Receivable & Payable', icon: BookOpen },
  { abbreviation: 'SOM', title: 'Subscription Order Management', icon: Boxes },
  { abbreviation: 'SAP + BRIM', title: 'Connected knowledge across the entire SAP landscape.', icon: Compass },
];

const retrievalSteps: Array<[string, string, React.ReactNode, React.ComponentType<{ size?: number }>]> = [
  ['01', 'Question', <>Start with your SAP question in <strong>everyday technical or functional terms</strong>.</>, MessageCircle],
  ['02', 'Retrieve', <><strong>Dense embeddings & BM25 search</strong> across indexed enterprise manuals.</>, Search],
  ['03', 'Rank', <><strong>Cross-encoder reranking</strong> prioritizes highest-relevance context.</>, Gauge],
  ['04', 'Generate', <><strong>Real-time streaming generation</strong> informed strictly by verified knowledge.</>, Sparkles],
  ['05', 'Ground', <><strong>Automated grounding checks</strong> verify factual alignment and prevent hallucination.</>, ShieldCheck],
  ['06', 'Respond', <><strong>Interactive answers</strong> with verified citations and grounding confidence.</>, ArrowRight],
];

const useCases: Array<[string, React.ReactNode]> = [
  ['Configuration', <>Where is this specific SAP setting configured in <strong>SPRO</strong>?</>],
  ['Transaction codes', <>Which <strong>transaction code</strong> manages billable items or billing runs?</>],
  ['Concepts', <>What is the <strong>lifecycle of a billable item</strong> in Convergent Invoicing?</>],
  ['Processes', <>Walk me step-by-step through the <strong>SAP BRIM rating and charging flow</strong>.</>],
  ['Troubleshooting', <>Billing completed but <strong>no invoice document created</strong>. What should I check?</>],
  ['Documentation', <>Synthesize complex <strong>FI-CA clearing rules</strong> from official SAP documentation.</>],
];

const exampleQuestions = [
  'What is FKKBIXCIT_CONF?',
  'Where are document types configured in FI-CA?',
  'How does Convergent Charging handle charge plans?',
  'Explain the complete BRIM billing flow.',
  'Why was my billing document not generated?',
  'What is the purpose of transaction FKKBIX_BIT_MON?',
];

function ResponsePreview({ specific = false }: { specific?: boolean }) {
  return (
    <article className="response-preview">
      <div className="response-preview-top">
        <span><span className="live-dot" /> LIVE PLATFORM ARCHITECTURE</span>
        <span>Developer-Managed RAG</span>
      </div>
      <div className="response-preview-question">
        <span>QUESTION</span>
        <p>{specific ? 'Where is this SAP configuration maintained in SPRO?' : 'What is transaction FKKBIXCIT_CONF?'}</p>
      </div>
      <div className="response-preview-answer">
        <span>ANSWER</span>
        <p>Relevant SAP details are retrieved from indexed enterprise manuals with verified citations and cross-encoder validation.</p>
      </div>
      {specific && (
        <div className="response-preview-row">
          <strong>Configuration path</strong>
          <span>IMG &gt; Financial Accounting &gt; Contract Accounts Receivable & Payable &gt; Convergent Invoicing</span>
        </div>
      )}
      <div className="response-preview-meta">
        <div><strong>Grounding Score</strong><span>0.94 · Highly Grounded</span></div>
        <div><strong>Source Type</strong><span>Knowledge Base</span></div>
        <div><strong>Citations</strong><span>3 Verified Doc Chunks</span></div>
      </div>
    </article>
  );
}

export const LandingPage: React.FC = () => {
  return (
    <>
      <PageMeta
        title="SAP + BRIM AI Knowledge Assistant"
        description="Clyptusap.ai is an enterprise AI knowledge assistant dedicated to SAP and SAP BRIM."
      />
      <PublicNav />
      <main>
        {/* Hero Section */}
        <section className="hero section-wrap">
          <motion.div
            className="hero-copy"
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55 }}
          >
            <div className="hero-kicker">
              <span className="kicker-mark">C</span> <strong>SAP + BRIM</strong> ENTERPRISE ASSISTANT
            </div>
            <h1>
              Your SAP questions.<br />
              <span>Answered with</span><br />
              exact context.
            </h1>
            <p className="hero-description">
              <strong>Clyptus.AI</strong> is an enterprise AI knowledge platform built to help consultants and architects navigate <strong>SAP &amp; BRIM</strong> with <strong>grounded, verified citations</strong>.
            </p>
            <div className="hero-actions">
              <Link className="button button-brand" to="/login">
                Ask Clyptus.AI <ArrowUpRight size={17} />
              </Link>
              <Link className="text-link" to="/how-it-works">
                See how it works <ArrowRight size={16} />
              </Link>
            </div>
            <div className="hero-trust">
              <span className="trust-line" />
              <strong>SAP-Focused</strong> · <strong>Hybrid Retrieval</strong> · <strong>Grounded in Verified Documentation</strong>
            </div>
          </motion.div>

          <motion.div
            className="hero-visual"
            initial={{ opacity: 0, y: 22 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.14 }}
          >
            <VideoShowcase />
            <div className="video-supporting-copy">
              <strong>See Clyptus.AI in action</strong>
              <p>
                Ask a question. <strong>Clyptus.AI</strong> retrieves relevant SAP knowledge, generates answers with <strong>real-time streaming</strong>, and surfaces <strong>verified citations</strong>.
              </p>
            </div>
          </motion.div>
          <a className="scroll-hint" href="#why">
            <span>SCROLL TO EXPLORE</span>
            <ArrowDown size={14} />
          </a>
        </section>

        {/* Statement Band */}
        <section className="statement-band" id="why">
          <div className="statement-inner">
            <span className="eyebrow">ENTERPRISE SAP KNOWLEDGE, IN CONTEXT</span>
            <p>
              From complex SAP configuration doubts<br />
              <span>to <strong>verified answers</strong> and <strong>authoritative documentation</strong>.</span>
            </p>
          </div>
        </section>

        {/* Intro Section */}
        <section className="section section-wrap intro-section">
          <div className="intro-label">
            <span className="section-index">01</span>
            <span className="eyebrow">WHAT IS CLYPTUS.AI</span>
          </div>
          <div className="intro-content">
            <h2>An AI assistant<br />built specifically for <span>SAP knowledge.</span></h2>
            <p>
              SAP is vast and intricate. Answers depend on <strong>precise module interactions</strong>, <strong>transaction codes</strong>, <strong>SPRO customizing settings</strong>, and <strong>system architectures</strong>.
            </p>
            <p>
              <strong>Clyptus.AI</strong> uses <strong>Developer-Managed RAG</strong> to retrieve the exact documentation before answering, <strong>eliminating hallucinations</strong> and delivering <strong>enterprise grounding</strong>.
            </p>
            <Link className="text-link" to="/how-it-works">
              See how answers are grounded <ArrowRight size={16} />
            </Link>
          </div>
        </section>

        {/* Workflow Section */}
        <section className="workflow-section">
          <div className="section section-wrap">
            <div className="workflow-heading">
              <div>
                <span className="eyebrow">THE RAG WORKFLOW</span>
                <h2>Retrieve first.<br /><span>Answer second.</span></h2>
              </div>
              <p>
                <strong>Dense embeddings</strong>, <strong>BM25 lexical search</strong>, <strong>cross-encoder reranking</strong>, and <strong>citation tracking</strong> ensure rock-solid answers.
              </p>
            </div>
            <div className="workflow-track workflow-track-six">
              {retrievalSteps.map(([number, title, text, Icon], index) => (
                <motion.div
                  className="workflow-step"
                  key={number}
                  initial={{ opacity: 0, y: 14 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, amount: 0.35 }}
                  transition={{ delay: index * 0.06 }}
                >
                  <div className="workflow-node"><Icon size={18} /></div>
                  <span className="step-number">{number}</span>
                  <h3>{title}</h3>
                  <p>{text}</p>
                  {index < retrievalSteps.length - 1 && <span className="workflow-connector" aria-hidden="true" />}
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* BRIM Section */}
        <section className="section section-wrap brim-section">
          <div className="features-heading">
            <div>
              <span className="eyebrow">SAP + BRIM</span>
              <h2>Built for SAP.<br /><span>Deeply focused on BRIM.</span></h2>
            </div>
            <p>
              Full coverage across <strong>billing, rating, charging, subscription order management (SOM)</strong>, and <strong>contract accounts (FI-CA)</strong>.
            </p>
          </div>
          <div className="feature-grid">
            {brimAreas.map(({ abbreviation, title, icon: Icon }, index) => (
              <motion.article
                className="feature-card brim-card"
                key={abbreviation}
                initial={{ opacity: 0, y: 14 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, amount: 0.25 }}
                transition={{ delay: index * 0.05 }}
              >
                <span className="feature-icon"><Icon size={19} strokeWidth={1.7} /></span>
                <span className="brim-abbreviation">{abbreviation}</span>
                <h3>{title}</h3>
                <span className="feature-card-line" />
              </motion.article>
            ))}
          </div>
        </section>

        {/* Response Preview */}
        <section className="response-section section section-wrap">
          <div className="response-copy">
            <span className="eyebrow">SOURCES + CONFIDENCE</span>
            <h2>Don't just get an answer.<br /><span>See what supports it.</span></h2>
            <p>
              <strong>Clyptus.AI</strong> provides <strong>clickable sources</strong>, <strong>grounding score badges</strong>, and <strong>exact page citations</strong> alongside each response.
            </p>
          </div>
          <ResponsePreview />
        </section>

        {/* Boundary Section */}
        <section className="boundary-section">
          <div className="section section-wrap boundary-grid">
            <article className="boundary-card">
              <span className="eyebrow">WHEN KNOWLEDGE IS INSUFFICIENT</span>
              <h2>When the knowledge isn't there,<br /><span>Clyptus.AI says so.</span></h2>
              <p>
                When retrieved documentation does not sufficiently support an answer, the assistant <strong>refuses to hallucinate</strong> invented settings or transaction codes.
              </p>
              <div className="boundary-example">
                <strong>User</strong>
                <p>“What is posting area 9999 used for in FI-CA?”</p>
                <strong>Assistant</strong>
                <p>“I couldn't find sufficient information in verified SAP documentation to answer this reliably.”</p>
              </div>
              <div className="boundary-tags">
                <span>Grounding Verification</span>
                <span>Verified Citations</span>
                <span>Zero Hallucination</span>
              </div>
            </article>

            <article className="boundary-card domain-card">
              <span className="eyebrow">DOMAIN BOUNDARY</span>
              <h2>Focused<br /><span>by design.</span></h2>
              <p>
                <strong>Clyptus.AI</strong> is strictly specialized in <strong>SAP ERP, S/4HANA, Fiori, ABAP, Basis, and BRIM</strong>. General non-enterprise queries are <strong>rejected at pre-flight</strong>.
              </p>
              <div className="boundary-example">
                <strong>User</strong>
                <p>“What is the weather in Paris?”</p>
                <strong>Assistant</strong>
                <p>“I am strictly specialized in SAP and SAP BRIM enterprise systems. Please ask an SAP-related question.”</p>
              </div>
            </article>
          </div>
        </section>

        {/* Question Section */}
        <section className="section section-wrap question-section">
          <div className="question-heading">
            <span className="eyebrow">START WITH WHAT YOU'RE WORKING ON</span>
            <h2>Ask the SAP question<br /><span>already in front of you.</span></h2>
            <p>
              Ask about <strong>transaction codes</strong>, <strong>error messages</strong>, <strong>SPRO customizing paths</strong>, <strong>process integration</strong>, or <strong>configuration guidelines</strong>.
            </p>
          </div>
          <div className="question-list">
            {exampleQuestions.map((question, index) => (
              <div className="question-chip" key={question}>
                <span>0{index + 1}</span>
                <p>{question}</p>
                <ArrowUpRight size={15} />
              </div>
            ))}
          </div>
        </section>

        {/* About Clyptus Section */}
        <section id="about" className="about-clyptus-section section-wrap">
          <div className="about-clyptus-inner">
            <div className="about-header">
              <span className="eyebrow">ABOUT CLYPTUS &amp; CLYPTUS.AI</span>
              <h2>
                Engineered for enterprise precision.<br />
                <span>Zero guesswork in mission-critical SAP.</span>
              </h2>
              <p className="about-lead">
                <strong>Clyptus Technologies</strong> builds domain-specialized artificial intelligence systems designed strictly for complex ERP environments. <strong>Clyptus.AI</strong> bridges the gap between massive, distributed SAP technical documentation and <strong>immediate, grounded decision-making</strong> for enterprise architects, billing consultants, and engineering teams.
              </p>
            </div>

            <div className="about-story-grid">
              <div className="about-story-card">
                <span className="story-badge">THE CHALLENGE</span>
                <h3>Why Generic AI Fails in SAP</h3>
                <p>
                  Standard large language models <strong>hallucinate non-existent transaction codes</strong>, invent <strong>fictitious SPRO customizing paths</strong>, and confuse SAP Convergent Charging rating logic with Convergent Invoicing billing plans. In high-throughput telecommunications, utilities, and subscription businesses, <strong>a single billing configuration error can delay millions in revenue recognition</strong>.
                </p>
              </div>

              <div className="about-story-card highlight-card">
                <span className="story-badge">THE CLYPTUS APPROACH</span>
                <h3>Grounding Before Generation</h3>
                <p>
                  <strong>Clyptus.AI never relies on raw parametric memory</strong> for configuration paths or technical syntax. Every query triggers <strong>dense embedding retrieval</strong> combined with <strong>BM25 exact keyword matching</strong>, <strong>cross-encoder neural reranking</strong>, and <strong>mathematical grounding verification</strong>. If verified enterprise documentation doesn't back the answer, <strong>the system refuses rather than guessing</strong>.
                </p>
              </div>
            </div>

            <div className="about-pillars-grid">
              <div className="pillar-item">
                <div className="pillar-num">01</div>
                <h4>Authoritative Ingestion</h4>
                <p>Curated indexing of <strong>official SAP configuration guides</strong>, customizing dictionaries, <strong>master data schemas</strong>, and implementation blueprints.</p>
              </div>

              <div className="pillar-item">
                <div className="pillar-num">02</div>
                <h4>Dual-Stage Reranking</h4>
                <p><strong>Cross-encoder neural models</strong> re-evaluate candidate chunks against the specific functional query <strong>before generation begins</strong>.</p>
              </div>

              <div className="pillar-item">
                <div className="pillar-num">03</div>
                <h4>Verifiable Citations</h4>
                <p>Every response displays <strong>clickable citations</strong> with <strong>document names, section paths, exact page numbers</strong>, and similarity scores.</p>
              </div>

              <div className="pillar-item">
                <div className="pillar-num">04</div>
                <h4>Strict Tenant Isolation</h4>
                <p>Enterprise-grade security with <strong>JWT token authorization</strong>, <strong>project workspace grouping</strong>, and <strong>absolute data confidentiality</strong>.</p>
              </div>
            </div>

            <div className="about-stats-band">
              <div className="stat-box">
                <strong>100%</strong>
                <span>Grounded Citations</span>
              </div>
              <div className="stat-box">
                <strong>5 Core</strong>
                <span>BRIM Modules Covered</span>
              </div>
              <div className="stat-box">
                <strong>&lt; 250ms</strong>
                <span>Neural Rerank Latency</span>
              </div>
              <div className="stat-box">
                <strong>Zero</strong>
                <span>Invented Configurations</span>
              </div>
            </div>
          </div>
        </section>

        {/* Use Cases */}
        <section className="usecase-section">
          <div className="section section-wrap">
            <div className="usecase-heading">
              <span className="eyebrow">SAP-SPECIFIC USE CASES</span>
              <h2>From questions<br /><span>to actionable technical clarity.</span></h2>
            </div>
            <div className="usecase-grid">
              {useCases.map(([title, text], i) => (
                <article key={title} className="usecase-card">
                  <span>0{i + 1}</span>
                  <h3>{title}</h3>
                  <p>{text}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        {/* FAQ Section */}
        <FaqSection />

        {/* Final CTA */}
        <section className="final-cta section-wrap">
          <div className="final-cta-inner">
            <span className="eyebrow">READY TO EXPLORE SAP?</span>
            <h2>Have an SAP question?<br /><span>Ask Clyptus.AI.</span></h2>
            <p>
              Get <strong>grounded answers</strong> across <strong>SAP and BRIM</strong>, backed by <strong>retrieved knowledge, authoritative sources</strong>, and <strong>verified confidence</strong>.
            </p>
            <Link className="button button-brand" to="/login">
              Open Workspace <ArrowUpRight size={17} />
            </Link>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
};
