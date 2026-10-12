import React, { useState } from 'react';
import {
  X,
  FileText,
  Award,
  Hash,
  BookOpen,
  Globe,
  Copy,
  Check,
  ExternalLink,
  ShieldCheck,
  Search,
} from 'lucide-react';
import type { Citation, WebSource } from '../../types';

interface CitationModalProps {
  citations?: Citation[];
  webSources?: WebSource[];
  isOpen: boolean;
  onClose: () => void;
}

export const CitationModal: React.FC<CitationModalProps> = ({
  citations = [],
  webSources = [],
  isOpen,
  onClose,
}) => {
  const [activeTab, setActiveTab] = useState<'all' | 'kb' | 'web'>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [copiedIndex, setCopiedIndex] = useState<string | null>(null);

  if (!isOpen) return null;

  const totalSources = citations.length + webSources.length;
  const hasCitations = citations.length > 0;
  const hasWebSources = webSources.length > 0;

  const handleCopyText = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(id);
    setTimeout(() => {
      setCopiedIndex((prev) => (prev === id ? null : prev));
    }, 2000);
  };

  const filteredCitations = citations.filter((c) => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      c.document.toLowerCase().includes(term) ||
      (c.section && c.section.toLowerCase().includes(term)) ||
      c.snippet.toLowerCase().includes(term)
    );
  });

  const filteredWebSources = webSources.filter((w) => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      w.title.toLowerCase().includes(term) ||
      w.domain.toLowerCase().includes(term) ||
      w.snippet.toLowerCase().includes(term)
    );
  });

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-5 bg-black/65 dark:bg-black/80 backdrop-blur-sm animate-in fade-in duration-200"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-3xl bg-white dark:bg-[#0c0c14] border border-slate-200 dark:border-[#222234] rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[88vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 sm:px-6 py-4 border-b border-slate-200 dark:border-[#1a1a28] bg-slate-50/90 dark:bg-[#08080f] shrink-0">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-orange-500/10 dark:bg-orange-500/20 text-orange-600 dark:text-orange-400 border border-orange-500/25 dark:border-orange-500/35">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                  Verified Evidence Sources
                </h3>
                <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full bg-orange-500/10 dark:bg-orange-500/15 text-orange-700 dark:text-orange-300 border border-orange-500/20">
                  <ShieldCheck className="w-3 h-3 text-orange-500" />
                  {totalSources} {totalSources === 1 ? 'Source' : 'Sources'}
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                Exact documents, manuals, and official SAP portals where this response was retrieved
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-white hover:bg-slate-200/60 dark:hover:bg-slate-800 transition cursor-pointer"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Filter bar & Tabs */}
        <div className="px-5 sm:px-6 py-3 border-b border-slate-200 dark:border-[#1a1a28] bg-slate-100/50 dark:bg-[#07070b] flex flex-wrap items-center justify-between gap-3 shrink-0">
          {/* Tabs */}
          <div className="inline-flex items-center p-1 rounded-xl bg-slate-200/70 dark:bg-[#12121e] text-xs font-medium">
            <button
              onClick={() => setActiveTab('all')}
              className={`px-3 py-1.5 rounded-lg transition cursor-pointer ${
                activeTab === 'all'
                  ? 'bg-white dark:bg-[#1e1e30] text-slate-900 dark:text-white shadow-xs font-semibold'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              All Sources ({totalSources})
            </button>
            {hasCitations && (
              <button
                onClick={() => setActiveTab('kb')}
                className={`px-3 py-1.5 rounded-lg transition cursor-pointer flex items-center gap-1.5 ${
                  activeTab === 'kb'
                    ? 'bg-white dark:bg-[#1e1e30] text-orange-600 dark:text-orange-400 shadow-xs font-semibold'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <BookOpen className="w-3.5 h-3.5 text-orange-500" />
                <span>Internal KB ({citations.length})</span>
              </button>
            )}
            {hasWebSources && (
              <button
                onClick={() => setActiveTab('web')}
                className={`px-3 py-1.5 rounded-lg transition cursor-pointer flex items-center gap-1.5 ${
                  activeTab === 'web'
                    ? 'bg-white dark:bg-[#1e1e30] text-cyan-600 dark:text-cyan-400 shadow-xs font-semibold'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <Globe className="w-3.5 h-3.5 text-cyan-500" />
                <span>SAP Web ({webSources.length})</span>
              </button>
            )}
          </div>

          {/* Search filter within sources */}
          {totalSources > 2 && (
            <div className="relative min-w-[200px] flex-1 sm:flex-initial">
              <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Filter by keyword..."
                className="w-full pl-8 pr-3 py-1 text-xs rounded-lg border border-slate-300 dark:border-slate-800 bg-white dark:bg-[#10101a] text-slate-800 dark:text-slate-200 placeholder-slate-400 focus:outline-none focus:border-orange-500"
              />
            </div>
          )}
        </div>

        {/* Scrollable Content Body */}
        <div className="p-5 sm:p-6 overflow-y-auto space-y-4 flex-1">
          {/* Knowledge Base Citations */}
          {(activeTab === 'all' || activeTab === 'kb') && filteredCitations.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center justify-between text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                <span className="flex items-center gap-1.5">
                  <BookOpen className="w-3.5 h-3.5 text-orange-500" />
                  SAP Enterprise Internal Documentation
                </span>
                <span className="text-[11px] font-medium text-slate-400">
                  {filteredCitations.length} {filteredCitations.length === 1 ? 'file match' : 'file matches'}
                </span>
              </div>

              {filteredCitations.map((c, idx) => {
                const matchPct = Math.round(c.score * 100);
                const copyKey = `kb-${idx}`;
                const isCopied = copiedIndex === copyKey;

                return (
                  <div
                    key={idx}
                    className="p-4 sm:p-5 rounded-2xl bg-slate-50/80 dark:bg-[#0e0e18] border border-slate-200 dark:border-[#1e1e2c] hover:border-orange-500/40 dark:hover:border-orange-500/40 transition-all space-y-3.5 shadow-xs"
                  >
                    {/* Header meta */}
                    <div className="flex flex-wrap items-center justify-between gap-2.5 pb-2.5 border-b border-slate-200/80 dark:border-[#181826]">
                      <div className="flex items-center gap-2.5 min-w-0">
                        <span className="w-6 h-6 rounded-lg bg-orange-500/15 dark:bg-orange-500/20 border border-orange-500/30 text-orange-600 dark:text-orange-300 text-xs font-bold flex items-center justify-center shrink-0">
                          {idx + 1}
                        </span>
                        <div className="min-w-0">
                          <div className="flex items-center gap-1.5">
                            <span className="text-xs font-bold text-slate-900 dark:text-slate-100 break-all sm:break-normal">
                              {c.document}
                            </span>
                            <span className="px-1.5 py-0.2 rounded text-[10px] font-semibold bg-orange-100 dark:bg-orange-950/60 text-orange-700 dark:text-orange-300 border border-orange-300 dark:border-orange-500/30 shrink-0">
                              Official Manual
                            </span>
                          </div>
                          {c.section && (
                            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5 truncate">
                              Section: <strong className="text-slate-700 dark:text-slate-300 font-semibold">{c.section}</strong>
                            </p>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-2 shrink-0">
                        <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 dark:text-emerald-400 bg-emerald-100/80 dark:bg-emerald-950/40 px-2 py-0.5 rounded-md border border-emerald-300 dark:border-emerald-800/40">
                          <Hash className="w-3 h-3" />
                          Page {c.page}
                        </span>

                        {c.score > 0 && (
                          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-orange-700 dark:text-orange-300 bg-orange-100/80 dark:bg-orange-950/50 px-2 py-0.5 rounded-md border border-orange-300 dark:border-orange-500/30">
                            <Award className="w-3 h-3 text-orange-500" />
                            {matchPct}% Match
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Verbatim Excerpt */}
                    <div>
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
                          Real Retrieved Passage (Verbatim Grounding Chunk)
                        </span>
                        <button
                          type="button"
                          onClick={() => handleCopyText(c.snippet, copyKey)}
                          className="inline-flex items-center gap-1 text-[11px] font-medium text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 transition cursor-pointer"
                          title="Copy snippet text"
                        >
                          {isCopied ? (
                            <>
                              <Check className="w-3 h-3 text-emerald-500" />
                              <span className="text-emerald-600 dark:text-emerald-400">Copied</span>
                            </>
                          ) : (
                            <>
                              <Copy className="w-3 h-3" />
                              <span>Copy Excerpt</span>
                            </>
                          )}
                        </button>
                      </div>
                      <div className="p-3.5 bg-white dark:bg-[#07070d] border border-slate-200 dark:border-[#1a1a28] rounded-xl text-xs leading-relaxed text-slate-700 dark:text-slate-300 font-mono whitespace-pre-wrap select-text max-h-48 overflow-y-auto">
                        "{c.snippet}"
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Web Sources Fallback */}
          {(activeTab === 'all' || activeTab === 'web') && filteredWebSources.length > 0 && (
            <div className="space-y-4 pt-2">
              <div className="flex items-center justify-between text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                <span className="flex items-center gap-1.5">
                  <Globe className="w-3.5 h-3.5 text-cyan-500" />
                  Official SAP Web Portal Sources (help.sap.com)
                </span>
                <span className="text-[11px] font-medium text-slate-400">
                  {filteredWebSources.length} {filteredWebSources.length === 1 ? 'web reference' : 'web references'}
                </span>
              </div>

              {filteredWebSources.map((w, idx) => {
                const copyKey = `web-${idx}`;
                const isCopied = copiedIndex === copyKey;

                return (
                  <div
                    key={idx}
                    className="p-4 sm:p-5 rounded-2xl bg-slate-50/80 dark:bg-[#0e0e18] border border-slate-200 dark:border-[#1e1e2c] hover:border-cyan-500/40 dark:hover:border-cyan-500/40 transition-all space-y-3.5 shadow-xs"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2.5 pb-2.5 border-b border-slate-200/80 dark:border-[#181826]">
                      <div className="flex items-center gap-2 min-w-0">
                        <Globe className="w-4 h-4 text-cyan-600 dark:text-cyan-400 shrink-0" />
                        <span className="text-xs font-bold text-slate-900 dark:text-slate-100">
                          {w.title}
                        </span>
                      </div>

                      <div className="flex items-center gap-2">
                        <span className="text-[10px] font-semibold text-cyan-800 dark:text-cyan-300 bg-cyan-100 dark:bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-300 dark:border-cyan-800/40">
                          {w.domain}
                        </span>
                        {w.url && (
                          <a
                            href={w.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-[11px] font-semibold text-cyan-600 dark:text-cyan-400 hover:text-cyan-700 dark:hover:text-cyan-300 hover:underline px-2 py-0.5 rounded bg-cyan-50 dark:bg-cyan-950/30 border border-cyan-200 dark:border-cyan-800/30 transition cursor-pointer"
                          >
                            <span>Open in help.sap.com</span>
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                      </div>
                    </div>

                    {/* Excerpt */}
                    <div>
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">
                          Real Web Documentation Snippet
                        </span>
                        <button
                          type="button"
                          onClick={() => handleCopyText(w.snippet, copyKey)}
                          className="inline-flex items-center gap-1 text-[11px] font-medium text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 transition cursor-pointer"
                          title="Copy snippet text"
                        >
                          {isCopied ? (
                            <>
                              <Check className="w-3 h-3 text-emerald-500" />
                              <span className="text-emerald-600 dark:text-emerald-400">Copied</span>
                            </>
                          ) : (
                            <>
                              <Copy className="w-3 h-3" />
                              <span>Copy Excerpt</span>
                            </>
                          )}
                        </button>
                      </div>
                      <div className="p-3.5 bg-white dark:bg-[#07070d] border border-slate-200 dark:border-[#1a1a28] rounded-xl text-xs leading-relaxed text-slate-700 dark:text-slate-300 font-mono whitespace-pre-wrap select-text max-h-48 overflow-y-auto">
                        "{w.snippet}"
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Empty fallback */}
          {filteredCitations.length === 0 && filteredWebSources.length === 0 && (
            <div className="text-center py-12 text-slate-400 text-xs space-y-2">
              <BookOpen className="w-9 h-9 text-slate-400 dark:text-slate-600 mx-auto opacity-70" />
              <p className="font-semibold text-slate-600 dark:text-slate-300">
                {searchTerm ? 'No sources match your filter keyword.' : 'No verified source citations found for this answer.'}
              </p>
              {searchTerm && (
                <button
                  type="button"
                  onClick={() => setSearchTerm('')}
                  className="text-orange-500 hover:underline text-xs"
                >
                  Clear filter
                </button>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-5 sm:px-6 py-3 border-t border-slate-200 dark:border-[#1a1a28] bg-slate-50/90 dark:bg-[#08080f] flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 shrink-0">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>Hybrid Dense + Lexical + Rerank Provenance</span>
          </span>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-1.5 rounded-xl bg-slate-200 dark:bg-[#1a1a26] hover:bg-slate-300 dark:hover:bg-[#252538] text-slate-800 dark:text-slate-200 font-semibold transition cursor-pointer"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
