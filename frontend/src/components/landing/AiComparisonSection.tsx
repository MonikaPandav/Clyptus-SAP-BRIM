import { Check, ShieldAlert, ShieldCheck, X } from 'lucide-react';

interface ComparisonRow {
  dimension: string;
  genericAi: string;
  genericStatus: 'bad' | 'warn';
  clyptusAi: string;
  clyptusStatus: 'good';
}

const comparisons: ComparisonRow[] = [
  {
    dimension: 'SPRO Customizing Paths',
    genericAi: 'Frequently hallucinates non-existent SPRO nodes, mixing ECC and S/4HANA paths.',
    genericStatus: 'bad',
    clyptusAi: 'Exact SPRO hierarchy retrieved directly from indexed SAP official customizing guides.',
    clyptusStatus: 'good',
  },
  {
    dimension: 'SAP Transaction Codes',
    genericAi: 'Invents outdated or fictitious T-Codes (e.g., mixing SD billing with FI-CA).',
    genericStatus: 'bad',
    clyptusAi: 'Verified, executable S/4HANA and BRIM T-Codes (e.g. FKKBIXCIT_CONF, FPY1).',
    clyptusStatus: 'good',
  },
  {
    dimension: 'Hallucination Safeguard',
    genericAi: 'Generates plausible-sounding but completely incorrect technical configurations.',
    genericStatus: 'bad',
    clyptusAi: 'Mathematical grounding verification. Refuses to answer if evidence is insufficient.',
    clyptusStatus: 'good',
  },
  {
    dimension: 'Citations & Audit Trail',
    genericAi: 'No source citations. Impossible to verify or defend in architectural reviews.',
    genericStatus: 'bad',
    clyptusAi: 'Page-level and document-level citations with similarity scores and verified notes.',
    clyptusStatus: 'good',
  },
  {
    dimension: 'BRIM Domain Specialization',
    genericAi: 'Generalist training with shallow, outdated web scrapes on billing concepts.',
    genericStatus: 'warn',
    clyptusAi: 'Strictly dedicated to SAP ERP, S/4HANA, BRIM (CI, CC, FI-CA, SOM, CM).',
    clyptusStatus: 'good',
  },
  {
    dimension: 'Enterprise Data Privacy',
    genericAi: 'Public multi-tenant endpoints with risk of confidential prompt leakage.',
    genericStatus: 'warn',
    clyptusAi: 'Tenant isolation, encrypted JWT authentication, admin-managed document boundaries.',
    clyptusStatus: 'good',
  },
];

export const AiComparisonSection: React.FC = () => {
  return (
    <section className="ai-comparison-section">
      <div className="section-container">
        {/* Section Header */}
        <div className="section-header-center">
          <div className="kicker-pill-subtle">
            <span className="pill-dot" />
            <span>ARCHITECTURAL INTEGRITY</span>
          </div>

          <h2 className="section-title-large">
            Why Generic AI Fails in SAP.<br />
            <span className="hero-italic-serif">And Why Clyptus.AI Doesn't.</span>
          </h2>

          <p className="section-subtitle-muted">
            In mission-critical billing and revenue accounting, a single hallucinated customizing path can derail enterprise implementations. Grounding makes all the difference.
          </p>
        </div>

        {/* Side-by-side Table / Cards */}
        <div className="comparison-cards-grid">
          {/* Column 1: Generic LLMs */}
          <div className="comparison-col generic-col">
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
          </div>

          {/* Column 2: Clyptus.AI */}
          <div className="comparison-col clyptus-col">
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
          </div>
        </div>
      </div>
    </section>
  );
};
