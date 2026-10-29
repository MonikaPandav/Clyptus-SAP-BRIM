import { useState } from 'react';
import { Copy, Database, FileText, MessageSquare, Search, Workflow } from 'lucide-react';
import type { Scenario } from './HeroChatbotPreview';

interface Props {
  activePanel: 'chat' | 'documents' | 'workflows' | 'database';
  scenarios: Scenario[];
  activeScenario: Scenario;
  onSelectScenario: (scenario: Scenario) => void;
  onOpenChat: () => void;
  onCopyPath: () => void;
  copied: boolean;
}

export function PreviewResourcePanels({
  activePanel, scenarios, activeScenario, onSelectScenario, onOpenChat, onCopyPath, copied,
}: Props) {
  const [documentSearch, setDocumentSearch] = useState('');
  const filteredDocuments = scenarios.filter((scenario) =>
    `${scenario.citationDoc} ${scenario.category}`.toLowerCase().includes(documentSearch.trim().toLowerCase()),
  );

  return (
    <>
      <section className="showcase-resource-panel" aria-label="Documents preview" hidden={activePanel !== 'documents'}>
        <div className="showcase-welcome-header">
          <div className="welcome-icon-wrap"><FileText size={22} /></div>
          <h3>Documents</h3>
          <p>Browse the reference excerpts used by the four preview scenarios.</p>
        </div>
        <label className="showcase-search-box resource-search">
          <Search size={16} aria-hidden="true" />
          <input
            aria-label="Search preview documents"
            placeholder="Search manuals or BRIM domains"
            value={documentSearch}
            onChange={(event) => setDocumentSearch(event.target.value)}
          />
        </label>
        <div className="resource-document-list">
          {filteredDocuments.map((scenario) => (
            <button
              key={scenario.id}
              type="button"
              className={`resource-document ${activeScenario.id === scenario.id ? 'active' : ''}`}
              aria-pressed={activeScenario.id === scenario.id}
              onClick={() => onSelectScenario(scenario)}
            >
              <FileText size={16} aria-hidden="true" />
              <span><strong>{scenario.citationDoc}</strong><small>{scenario.category} · pp. {scenario.page}</small></span>
            </button>
          ))}
          {filteredDocuments.length === 0 && <p className="resolution-summary" role="status">No preview documents match your search.</p>}
        </div>
        <div className="floating-resolution-card">
          <div className="resolution-top-bar"><span className="resolution-badge">SELECTED REFERENCE EXCERPT</span></div>
          <div className="resolution-content">
            <p className="resolution-summary"><strong>{activeScenario.citationDoc}</strong> · pp. {activeScenario.page}</p>
            <p className="resolution-summary">{activeScenario.summary}</p>
            <button className="scenario-btn" type="button" onClick={onOpenChat}><MessageSquare size={13} /> Open in Chat</button>
          </div>
        </div>
      </section>

      <section className="showcase-resource-panel" aria-label="Workflows preview" hidden={activePanel !== 'workflows'}>
        <div className="showcase-welcome-header">
          <div className="welcome-icon-wrap"><Workflow size={22} /></div>
          <h3>Workflows</h3>
          <p>Explore the selected scenario's customizing path and implementation steps.</p>
        </div>
        <div className="floating-resolution-card">
          <div className="resolution-top-bar"><span className="resolution-badge">{activeScenario.tabLabel}</span></div>
          <div className="resolution-content">
            <div className="resolution-spro-box">
              <div className="spro-box-header">
                <strong>SPRO CUSTOMIZING PATH</strong>
                <button className="copy-path-btn" type="button" onClick={onCopyPath} title="Copy workflow SPRO path">
                  <Copy size={12} /><span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
              </div>
              <ol className="resource-path">
                {activeScenario.sproPath.split(/\s*(?:->|>)\s*/).map((step, index) => <li key={`${index}-${step}`}>{step}</li>)}
              </ol>
            </div>
            <ol className="resource-workflow-steps">
              {activeScenario.keyPoints.map((point) => <li key={point}>{point}</li>)}
            </ol>
            <p className="tcode-pill">T-CODE: <strong>{activeScenario.tcode}</strong></p>
            <button className="scenario-btn" type="button" onClick={onOpenChat}><MessageSquare size={13} /> Open in Chat</button>
          </div>
        </div>
      </section>

      <section className="showcase-resource-panel" aria-label="Database preview" hidden={activePanel !== 'database'}>
        <div className="showcase-welcome-header">
          <div className="welcome-icon-wrap"><Database size={22} /></div>
          <h3>Database</h3>
          <p>Inspect the {scenarios.length} sample knowledge records powering this preview.</p>
        </div>
        <div className="resource-table-scroll">
          <table className="resource-table">
            <caption>Preview knowledge records</caption>
            <thead><tr><th scope="col">Scenario</th><th scope="col">Transactions</th><th scope="col">Source pages</th></tr></thead>
            <tbody>
              {scenarios.map((scenario) => (
                <tr key={scenario.id} className={activeScenario.id === scenario.id ? 'active' : ''}>
                  <td><button type="button" aria-pressed={activeScenario.id === scenario.id} onClick={() => onSelectScenario(scenario)}>{scenario.tabLabel}</button></td>
                  <td>{scenario.tcode}</td><td>{scenario.page}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="floating-resolution-card">
          <div className="resolution-top-bar"><span className="resolution-badge">SELECTED RECORD · {activeScenario.id}</span></div>
          <div className="resolution-content">
            <dl className="resource-record">
              <dt>Domain</dt><dd>{activeScenario.category}</dd>
              <dt>Source</dt><dd>{activeScenario.citationDoc}</dd>
              <dt>SPRO path</dt><dd>{activeScenario.sproPath}</dd>
              <dt>Preview confidence</dt><dd>{activeScenario.similarity}</dd>
            </dl>
            <button className="scenario-btn" type="button" onClick={onOpenChat}><MessageSquare size={13} /> Open in Chat</button>
          </div>
        </div>
      </section>
    </>
  );
}
