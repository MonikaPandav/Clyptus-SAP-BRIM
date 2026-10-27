import React, { useState } from 'react';
import {
  ArrowRight,
  CheckCircle,
  Cpu,
  FileCheck2,
  MessageCircle,
  Search,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';

interface Stage {
  num: string;
  title: string;
  subtitle: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  description: string;
  techSpec: string;
  metric: string;
}

const stages: Stage[] = [
  {
    num: '01',
    title: 'Question Ingestion',
    subtitle: 'Technical SAP Context',
    icon: MessageCircle,
    description: 'Consultants submit questions using standard SAP business or technical terms, transaction codes, error codes, or SPRO paths.',
    techSpec: 'Pre-flight query normalization and prompt boundary analysis ensuring only enterprise SAP queries enter the pipeline.',
    metric: '< 15ms latency',
  },
  {
    num: '02',
    title: 'Hybrid Retrieval',
    subtitle: 'Dense Vectors + BM25',
    icon: Search,
    description: 'Simultaneous search using high-dimensional dense embeddings for semantic intent combined with BM25 lexical search for exact SAP transaction codes.',
    techSpec: 'Dual-index search across admin-curated official SAP implementation guides, customizing dictionaries, and master data schemas.',
    metric: 'Top-50 candidate recall',
  },
  {
    num: '03',
    title: 'Cross-Encoder Rerank',
    subtitle: 'Neural Relevance Scoring',
    icon: Cpu,
    description: 'Neural cross-encoder evaluates the exact semantic fit of every retrieved chunk against the query, filtering out out-of-date or irrelevant SAP release notes.',
    techSpec: 'Re-scores text chunks jointly with query tokens to maximize contextual precision before model prompting.',
    metric: '250ms reranking latency',
  },
  {
    num: '04',
    title: 'Streaming Generation',
    subtitle: 'Strict Contextual Guardrails',
    icon: Sparkles,
    description: 'LLM generates clear, step-by-step technical guidance with SPRO customizing paths, transaction codes, and prerequisite settings streamed in real-time.',
    techSpec: 'System prompt enforces strict grounding within retrieved context, preventing extrapolations or fabricated SAP codes.',
    metric: 'Token-by-token streaming',
  },
  {
    num: '05',
    title: 'Grounding Verification',
    subtitle: 'Automated Hallucination Check',
    icon: ShieldCheck,
    description: 'Post-generation mathematical checks ensure that every statement, table name, and configuration step is explicitly supported by retrieved manuals.',
    techSpec: 'Zero-hallucination safeguard: if confidence falls below threshold, the assistant alerts the user rather than guessing.',
    metric: '100% verified grounding',
  },
  {
    num: '06',
    title: 'Authoritative Response',
    subtitle: 'Clickable Document Citations',
    icon: FileCheck2,
    description: 'The response is delivered alongside clickable citations displaying the exact document title, section heading, page number, and similarity score.',
    techSpec: 'Traceable citations allow consultants to cross-reference official SAP guides immediately.',
    metric: 'Full audit traceability',
  },
];

export const RagWorkflowSection: React.FC = () => {
  const [activeStage, setActiveStage] = useState<number>(0);

  return (
    <section className="rag-workflow-section" id="how-it-works">
      <div className="section-container">
        {/* Section Heading */}
        <div className="section-header-center">
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
        </div>

        {/* 6-Stage Timeline Track */}
        <div className="workflow-stages-grid">
          {stages.map((stage, idx) => {
            const Icon = stage.icon;
            const isSelected = activeStage === idx;
            return (
              <div
                key={stage.num}
                className={`workflow-stage-card ${isSelected ? 'active-card' : ''}`}
                onClick={() => setActiveStage(idx)}
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
              </div>
            );
          })}
        </div>

        {/* Detailed Stage Deep-Dive Bar */}
        <div className="stage-deep-dive-card">
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
        </div>
      </div>
    </section>
  );
};
