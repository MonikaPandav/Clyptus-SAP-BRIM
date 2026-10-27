import React, { useState } from 'react';
import { ChevronDown, MessageSquare } from 'lucide-react';
import { Link } from 'react-router-dom';

interface FaqItem {
  id: string;
  category: string;
  question: string;
  answer: React.ReactNode;
}

const faqs: FaqItem[] = [
  {
    id: 'f1',
    category: 'Architecture & RAG',
    question: 'What is Clyptus.AI and how is it different from ChatGPT?',
    answer: (
      <>
        <strong>Clyptus.AI</strong> is an enterprise AI knowledge platform built specifically for <strong>SAP ERP, S/4HANA, and SAP BRIM</strong>. Unlike generalist models like ChatGPT that guess based on web scrapes, Clyptus.AI uses <strong>Developer-Managed Retrieval-Augmented Generation (RAG)</strong> to retrieve verified documentation first, generating answers strictly backed by cited manuals.
      </>
    ),
  },
  {
    id: 'f2',
    category: 'Architecture & RAG',
    question: 'What does “Developer-Managed RAG” mean in practice?',
    answer: (
      <>
        <strong>Developer-Managed RAG</strong> combines high-dimensional dense embeddings for semantic search with <strong>BM25 lexical search</strong> for exact SAP transaction codes, followed by <strong>cross-encoder neural reranking</strong>. This guarantees that only verified enterprise documentation enters the model prompt.
      </>
    ),
  },
  {
    id: 'f3',
    category: 'BRIM Coverage',
    question: 'Which SAP BRIM modules are natively supported?',
    answer: (
      <>
        Clyptus.AI covers all five core pillars: <strong>Convergent Invoicing (CI)</strong>, <strong>Convergent Charging (CC)</strong>, <strong>Contract Accounts Receivable & Payable (FI-CA)</strong>, <strong>Subscription Order Management (SOM)</strong>, and <strong>Convergent Mediation (CM)</strong>.
      </>
    ),
  },
  {
    id: 'f4',
    category: 'Security & Privacy',
    question: 'How are internal documents, schemas, and source manuals secured?',
    answer: (
      <>
        Source documents and indexing pipelines are <strong>strictly restricted to authorized enterprise administrators</strong> via the secure Admin Dashboard. All user sessions are authenticated using encrypted JWT tokens with role-based access control and tenant workspace isolation.
      </>
    ),
  },
  {
    id: 'f5',
    category: 'Accuracy & Refusal',
    question: 'What happens when retrieved knowledge cannot answer my SAP question?',
    answer: (
      <>
        Clyptus.AI includes an <strong>automated mathematical grounding verification gate</strong>. If the retrieved documentation does not substantiate a confident technical answer, the assistant <strong>alerts the user and refuses to hallucinate</strong> fictitious SPRO customizing paths or T-Codes.
      </>
    ),
  },
  {
    id: 'f6',
    category: 'Domain Boundary',
    question: 'Can Clyptus.AI be used for non-SAP general queries?',
    answer: (
      <>
        No. Clyptus.AI enforces a <strong>strict domain boundary</strong> during query ingestion. General knowledge or non-enterprise queries (e.g., weather, generic programming) are rejected at pre-flight to preserve enterprise security and operational focus.
      </>
    ),
  },
];

export const FaqSection: React.FC = () => {
  const [openId, setOpenId] = useState<string | null>(faqs[0].id);

  const toggleFaq = (id: string) => {
    setOpenId(openId === id ? null : id);
  };

  return (
    <section className="faq-section" id="faq">
      <div className="section-container">
        {/* Section Header */}
        <div className="section-header-center">
          <div className="kicker-pill-subtle">
            <span className="pill-dot" />
            <span>FREQUENTLY ASKED QUESTIONS</span>
          </div>

          <h2 className="section-title-large">
            Curious About Clyptus.AI?<br />
            <span className="hero-italic-serif">Clear Answers to Common Questions.</span>
          </h2>

          <p className="section-subtitle-muted">
            Everything you need to know about our enterprise SAP retrieval architecture, grounding verification, and security guardrails.
          </p>
        </div>

        {/* Accordion List */}
        <div className="faq-accordion-wrap">
          {faqs.map((faq) => {
            const isOpen = openId === faq.id;
            return (
              <div
                key={faq.id}
                className={`faq-accordion-item ${isOpen ? 'is-open' : ''}`}
              >
                <button
                  className="faq-question-btn"
                  onClick={() => toggleFaq(faq.id)}
                  aria-expanded={isOpen}
                >
                  <div className="faq-question-title-wrap">
                    <span className="faq-category-badge">{faq.category}</span>
                    <span className="faq-question-text">{faq.question}</span>
                  </div>
                  <span className={`faq-chevron-icon ${isOpen ? 'rotated' : ''}`}>
                    <ChevronDown size={18} />
                  </span>
                </button>

                {isOpen && (
                  <div className="faq-answer-content">
                    <p>{faq.answer}</p>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Bottom Support Callout */}
        <div className="faq-bottom-callout">
          <div className="callout-inner">
            <div className="callout-icon-box">
              <MessageSquare size={18} />
            </div>
            <div>
              <strong>Have a specific architectural or billing question?</strong>
              <p>Explore our interactive workspace or connect with an enterprise consultant.</p>
            </div>
          </div>
          <Link to="/login" className="callout-action-btn">
            Open Workspace →
          </Link>
        </div>
      </div>
    </section>
  );
};
