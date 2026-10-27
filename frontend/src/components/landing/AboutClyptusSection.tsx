import React from 'react';

const pillars = [
  {
    num: '01',
    title: 'Authoritative Ingestion',
    desc: 'Curated indexing of official SAP configuration guides, customizing dictionaries, master data schemas, and implementation blueprints.',
  },
  {
    num: '02',
    title: 'Dual-Stage Reranking',
    desc: 'Cross-encoder neural models re-evaluate candidate chunks against the specific functional query before generation begins.',
  },
  {
    num: '03',
    title: 'Verifiable Citations',
    desc: 'Every response displays clickable citations with document names, section paths, exact page numbers, and similarity scores.',
  },
  {
    num: '04',
    title: 'Strict Tenant Isolation',
    desc: 'Enterprise-grade security with JWT token authorization, project workspace grouping, and absolute data confidentiality.',
  },
];

const stats = [
  { value: '100%', label: 'Grounded Citations', sub: 'Zero invented SAP settings' },
  { value: '5 Core', label: 'BRIM Modules Covered', sub: 'SOM, CC, CI, FI-CA, CM' },
  { value: '< 250ms', label: 'Neural Rerank Latency', sub: 'Cross-encoder scoring' },
  { value: 'Zero', label: 'Hallucination Tolerance', sub: 'Mathematical refusal gates' },
];

export const AboutClyptusSection: React.FC = () => {
  return (
    <section className="about-clyptus-section" id="about">
      <div className="section-container">
        {/* Section Header */}
        <div className="section-header-center">
          <div className="kicker-pill-subtle">
            <span className="pill-dot" />
            <span>ABOUT CLYPTUS &amp; CLYPTUS.AI</span>
          </div>

          <h2 className="section-title-large">
            Engineered For Enterprise Precision.<br />
            <span className="hero-italic-serif">Zero Guesswork in Mission-Critical SAP.</span>
          </h2>

          <p className="section-subtitle-muted">
            Clyptus Technologies builds domain-specialized artificial intelligence systems designed strictly for complex ERP environments. Clyptus.AI bridges the gap between massive, distributed SAP technical documentation and immediate, grounded decision-making for enterprise architects, billing consultants, and engineering teams.
          </p>
        </div>

        {/* 2 Story Cards */}
        <div className="about-story-grid">
          <div className="story-card">
            <span className="story-tag tag-challenge">THE ENTERPRISE CHALLENGE</span>
            <h3>Why Generic AI Fails in SAP</h3>
            <p>
              Standard large language models hallucinate non-existent transaction codes, invent fictitious SPRO customizing paths, and confuse SAP Convergent Charging rating logic with Convergent Invoicing billing plans. In high-throughput telecommunications, utilities, and subscription businesses, a single billing configuration error can delay millions in revenue recognition.
            </p>
          </div>

          <div className="story-card">
            <span className="story-tag tag-approach">THE CLYPTUS APPROACH</span>
            <h3>Grounding Before Generation</h3>
            <p>
              Clyptus.AI never relies on raw parametric memory for configuration paths or technical syntax. Every query triggers dense embedding retrieval combined with BM25 exact keyword matching, cross-encoder neural reranking, and mathematical grounding verification. If verified enterprise documentation doesn't back the answer, the system refuses rather than guessing.
            </p>
          </div>
        </div>

        {/* 4 Pillars Grid */}
        <div className="pillars-grid">
          {pillars.map((pillar) => (
            <div key={pillar.num} className="pillar-card">
              <span className="pillar-number">{pillar.num}</span>
              <h4 className="pillar-title">{pillar.title}</h4>
              <p className="pillar-desc">{pillar.desc}</p>
            </div>
          ))}
        </div>

        {/* 4 Stats Cards */}
        <div className="stats-cards-row">
          {stats.map((s) => (
            <div key={s.label} className="stat-card">
              <strong className="stat-value">{s.value}</strong>
              <span className="stat-label">{s.label}</span>
              <span className="stat-sub">{s.sub}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
