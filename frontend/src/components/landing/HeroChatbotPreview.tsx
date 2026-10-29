import React, { lazy, Suspense, useEffect, useRef, useState } from 'react';
import {
  CheckCircle2,
  ChevronRight,
  Copy,
  Database,
  FileCheck,
  FileText,
  Layers,
  Lock,
  MessageSquare,
  Search,
  Send,
  ShieldCheck,
  Sparkles,
  Workflow,
} from 'lucide-react';
import iconOnly from '../../assets/clyptusap-icon-small.webp';
const PreviewResourcePanels = lazy(() => import('./PreviewResourcePanels').then(m => ({ default: m.PreviewResourcePanels })));

export interface Scenario {
  id: string;
  tabLabel: string;
  category: string;
  query: string;
  sproPath: string;
  tcode: string;
  citationDoc: string;
  page: string;
  similarity: string;
  summary: string;
  keyPoints: string[];
}

const scenarios: Scenario[] = [
  {
    id: 'ci-bit',
    tabLabel: '1. CI Billable Items',
    category: 'Convergent Invoicing (CI)',
    query: 'Where is billable item class configuration maintained in SPRO and how do we generate it?',
    sproPath: 'IMG > Financial Accounting > Contract Accounts Receivable and Payable > Convergent Invoicing > Basic Data > Billable Item Classes',
    tcode: 'FKKBIXCIT_CONF',
    citationDoc: 'SAP S/4HANA BRIM Convergent Invoicing Configuration Guide',
    page: '142-145',
    similarity: '98.7%',
    summary: 'Billable Item Classes define the technical and business attributes of raw billing data ingested from SAP Convergent Charging or mediation systems.',
    keyPoints: [
      'Maintain interfaces and assign field catalogs in SPRO under Basic Data.',
      'Execute transaction FKKBIXCIT_CONF to generate DDIC structures (/1BIX/...) and DB storage tables.',
      'Activate both active and simulated test configurations prior to productive consumption.',
    ],
  },
  {
    id: 'brim-flow',
    tabLabel: '2. BRIM End-to-End Flow',
    category: 'Architecture & Process',
    query: 'Explain the complete end-to-end data lifecycle from Mediation to FI-CA billing & invoicing.',
    sproPath: 'Architecture Integration: SAP CM -> SAP CC (Charge Plan) -> SAP CI (Billing Doc) -> SAP FI-CA',
    tcode: 'FKKBIX_BIT_MON / FPY1',
    citationDoc: 'SAP BRIM Solution Architecture Reference Manual',
    page: '58-64',
    similarity: '99.1%',
    summary: 'The standard SAP BRIM flow processes high-volume consumption events through rating, invoicing, and contract accounting.',
    keyPoints: [
      'Convergent Mediation (CM) normalizes raw CDR records and filters duplicates.',
      'Convergent Charging (CC) evaluates charge plans, subscriber accounts, and generates Billable Items (BITs).',
      'Convergent Invoicing (CI) aggregates BITs into Billing Documents, then triggers FI-CA Invoicing Documents.',
    ],
  },
  {
    id: 'som-sync',
    tabLabel: '3. SOM Contract Sync',
    category: 'Subscription Order Management',
    query: 'How are Subscription Orders synchronized into Provider Contracts and CC Provider Agreements?',
    sproPath: 'Cross-Application Components > Master Data Synchronization > Customer/Vendor Integration (CVI)',
    tcode: 'CRMD_ORDER / FKKORD1',
    citationDoc: 'SAP S/4HANA Subscription Order Management Implementation Handbook',
    page: '210-216',
    similarity: '97.9%',
    summary: 'Subscription Orders captured in CRM/SOM are replicated to S/4HANA Provider Contracts and CC Provider Agreements using ODI (Order Distribution Infrastructure).',
    keyPoints: [
      'Order capture triggers contract creation via ODI step triggers.',
      'Provider Contract ID is distributed to SAP Convergent Charging via Web Services.',
      'FI-CA contract accounts are automatically linked for subledger accounting.',
    ],
  },
  {
    id: 'fica-clearing',
    tabLabel: '4. FI-CA Clearing Lock',
    category: 'Contract Accounts (FI-CA)',
    query: 'Why was an open invoice item excluded from the payment run (FPY1) clearing proposal?',
    sproPath: 'IMG > Financial Accounting > Contract Accounts Receivable and Payable > Basic Functions > Open Item Management > Clearing Control',
    tcode: 'FPY1 / FPE2',
    citationDoc: 'SAP FI-CA Subledger Clearing & Payment Configuration Guide',
    page: '88-92',
    similarity: '98.3%',
    summary: 'Items are excluded from automatic clearing if a clearing lock or payment lock exists in the line item or business partner contract account master record.',
    keyPoints: [
      'Check clearing lock reason in document line item via transaction FPE2.',
      'Verify clearing variants in SPRO under Clearing Control > Define Specifications for Clearing Types.',
      'Ensure execution parameters in FPY1 match the tolerance groups assigned to the contract account.',
    ],
  },
];

const previewPanels = [
  { id: 'chat', label: 'Chat', Icon: MessageSquare },
  { id: 'documents', label: 'Documents', Icon: FileText },
  { id: 'workflows', label: 'Workflows', Icon: Workflow },
  { id: 'database', label: 'Database', Icon: Database },
] as const;

export const HeroChatbotPreview: React.FC = () => {
  const [activePanel, setActivePanel] = useState<typeof previewPanels[number]['id']>('chat');
  const [panelsLoaded, setPanelsLoaded] = useState(false);
  const [activeScenario, setActiveScenario] = useState<Scenario>(scenarios[0]);
  const [copied, setCopied] = useState(false);
  const responseRef = useRef<HTMLDivElement>(null);
  const responseAnimation = useRef<Animation | null>(null);
  useEffect(() => () => responseAnimation.current?.cancel(), []);

  const handleCopyPath = () => {
    navigator.clipboard?.writeText(activeScenario.sproPath);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSwitchScenario = (sc: Scenario) => {
    if (sc.id === activeScenario.id) return;
    setActiveScenario(sc);
    setCopied(false);
    handleRunQuery();
  };

  const handleRunQuery = () => {
    // Preview answers are already available; keep the panel visible and mounted.
    responseAnimation.current?.cancel();
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    responseAnimation.current = responseRef.current?.animate(
      [{ opacity: 0.85 }, { opacity: 1 }],
      { duration: 200, easing: 'ease-out' },
    ) ?? null;
  };

  return (
    <div className="hero-product-showcase">
      {/* Outer App Browser Frame */}
      <div className="showcase-window">
        {/* Top Window Bar */}
        <div className="showcase-window-header">
          <div className="showcase-window-dots">
            <span className="dot dot-close" />
            <span className="dot dot-minimize" />
            <span className="dot dot-expand" />
          </div>

          <div className="showcase-window-brand">
            <img src={iconOnly} alt="Clyptus.AI" className="h-4 w-4 object-contain" />
            <span>Clyptus.AI Copilot</span>
          </div>

          <div className="showcase-window-tabs">
            <span className="active-tab">Enterprise RAG</span>
          </div>

          <div className="showcase-window-status">
            <span className="live-pulse-dot" />
            <span>Connected to SAP S/4HANA &amp; BRIM</span>
          </div>
        </div>

        {/* Window Body Layout */}
        <div className="showcase-window-body">
          {/* Left Mini Sidebar */}
          <aside className="showcase-sidebar">
            <div className="sidebar-dock-icons">
              {previewPanels.map(({ id, label, Icon }) => (
                <button
                  key={id}
                  type="button"
                  className={`dock-btn ${activePanel === id ? 'active' : ''}`}
                  title={label}
                  aria-label={label}
                  aria-pressed={activePanel === id}
                  onClick={() => {
                    setActivePanel(id);
                    if (id !== 'chat') setPanelsLoaded(true);
                  }}
                >
                  <Icon size={16} aria-hidden="true" />
                </button>
              ))}
            </div>

            <div className="sidebar-module-list">
              <span className="sidebar-module-title">CLICK SCENARIO TO PREVIEW</span>
              {scenarios.map((sc, index) => {
                const Icon = [Layers, Workflow, ShieldCheck, FileCheck][index];
                return (
                  <button
                    key={sc.id}
                    className={`scenario-btn ${activeScenario.id === sc.id ? 'active' : ''}`}
                    type="button"
                    aria-pressed={activeScenario.id === sc.id}
                    onClick={() => {
                      handleSwitchScenario(sc);
                      setActivePanel('chat');
                    }}
                  >
                    <Icon size={13} aria-hidden="true" />
                    <span>{sc.tabLabel}</span>
                  </button>
                );
              })}
            </div>

            <div className="sidebar-security-badge">
              <Lock size={12} />
              <span>Tenant Isolated</span>
            </div>
          </aside>

          {/* Center / Right Main Canvas */}
          <div className="showcase-main-workspace">
            <div className="showcase-chat-panel" role="region" aria-label="Chat preview" hidden={activePanel !== 'chat'}>
            {/* Welcome Center Pill */}
            <div className="showcase-welcome-header">
              <div className="welcome-icon-wrap">
                <img src={iconOnly} alt="Clyptus" className="h-7 w-7 object-contain" />
              </div>
              <h3>Welcome to Clyptus.AI Your SAP + BRIM Copilot</h3>
              <p>Ask complex billing flows, transaction codes, or SPRO customizing paths.</p>
            </div>

            {/* Interactive Search Query Bar */}
            <div className="showcase-search-box">
              <div className="search-input-mock">
                <Search size={16} className="search-icon" />
                <span className="search-text-value">{activeScenario.query}</span>
              </div>
              <button className="search-send-btn" aria-label="Send Query" onClick={handleRunQuery}>
                <Send size={14} />
              </button>
            </div>

            <div className="showcase-search-actions">
              <span className="action-tag"><Sparkles size={12} /> Hybrid Retrieval</span>
              <span className="action-tag"><FileCheck size={12} /> Dense Embeddings + BM25</span>
              <span className="action-tag"><ShieldCheck size={12} /> Dual Rerank Guardrails</span>
            </div>

            {/* Floating Overlaid Resolution Card (Interactive Response with Smooth Transition) */}
            <div className="floating-resolution-card">
                  <div
                    ref={responseRef}
                    aria-live="polite"
                  >
                    <div className="resolution-top-bar">
                      <div className="resolution-badge">
                        <CheckCircle2 size={13} />
                        <span>GROUNDED SAP RESOLUTION</span>
                      </div>
                      <div className="resolution-score">
                        <span>Confidence:</span>
                        <strong>{activeScenario.similarity}</strong>
                      </div>
                    </div>

                    <div className="resolution-content">
                      <p className="resolution-summary">{activeScenario.summary}</p>

                      {/* SPRO Customizing Path Pill */}
                      <div className="resolution-spro-box">
                        <div className="spro-box-header">
                          <strong>SPRO CUSTOMIZING PATH</strong>
                          <button className="copy-path-btn" onClick={handleCopyPath} title="Copy SPRO path">
                            <Copy size={12} />
                            <span>{copied ? 'Copied' : 'Copy'}</span>
                          </button>
                        </div>
                        <code>{activeScenario.sproPath}</code>
                      </div>

                      {/* Key Technical Points */}
                      <ul className="resolution-key-points">
                        {activeScenario.keyPoints.map((point, idx) => (
                          <li key={idx}>
                            <ChevronRight size={13} className="bullet-arrow" />
                            <span>{point}</span>
                          </li>
                        ))}
                      </ul>

                      {/* Citation Footer Pill */}
                      <div className="resolution-citation-row">
                        <div className="citation-pill">
                          <FileText size={12} />
                          <span>{activeScenario.citationDoc} · p. {activeScenario.page}</span>
                        </div>
                        <div className="tcode-pill">
                          <span>T-CODE:</span>
                          <strong>{activeScenario.tcode}</strong>
                        </div>
                      </div>
                    </div>
                  </div>
            </div>
            </div>
            {panelsLoaded && <Suspense fallback={<div className="resource-panel-loading" role="status">Loading panel...</div>}>
            <PreviewResourcePanels
              activePanel={activePanel}
              scenarios={scenarios}
              activeScenario={activeScenario}
              onSelectScenario={handleSwitchScenario}
              onOpenChat={() => setActivePanel('chat')}
              onCopyPath={handleCopyPath}
              copied={copied}
            />
            </Suspense>}
          </div>
        </div>

      </div>
    </div>
  );
};
