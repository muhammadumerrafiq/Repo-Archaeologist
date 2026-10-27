import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Compass,
  ArrowRight,
  ShieldCheck,
  Search,
  CheckCircle2,
  AlertCircle,
  FileCode,
  Layers,
  GitBranch,
  Terminal,
} from 'lucide-react';
import { validateRepoUrl } from '../lib/validateRepoUrl';
import { checkHealth } from '../api/analyze';
import { Button } from '../components/ui/Button';
import { ProvenanceStamp } from '../components/ui/ProvenanceStamp';

interface ExampleRepo {
  ownerRepo: string;
  label: string;
  category: string;
}

const EXAMPLE_REPOS: ExampleRepo[] = [
  { ownerRepo: 'bottlepy/bottle', label: 'bottlepy/bottle', category: 'Python Microframework' },
  { ownerRepo: 'chalk/chalk', label: 'chalk/chalk', category: 'TypeScript Terminal Styling' },
  { ownerRepo: 'facebook/react', label: 'facebook/react', category: 'Monorepo & Web Framework' },
  { ownerRepo: 'pallets/click', label: 'pallets/click', category: 'Python CLI Package' },
];

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [inputValue, setInputValue] = useState('');
  const [tokenConfigured, setTokenConfigured] = useState<boolean | null>(null);

  useEffect(() => {
    checkHealth()
      .then((res) => setTokenConfigured(res.github_token_configured))
      .catch(() => setTokenConfigured(false));
  }, []);

  const validation = validateRepoUrl(inputValue);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validation.valid && validation.owner && validation.repo) {
      navigate(`/analyze?repo=${validation.owner}/${validation.repo}`);
    }
  };

  const handleSelectExample = (ownerRepo: string) => {
    navigate(`/analyze?repo=${ownerRepo}`);
  };

  return (
    <div className="min-h-screen bg-bg-0 text-text-0 flex flex-col font-sans selection:bg-cyan/20 selection:text-cyan">
      {/* Top Header */}
      <header className="border-b border-border bg-bg-1/80 backdrop-blur sticky top-0 z-40 px-4 md:px-8 py-3">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded border border-cyan/40 bg-bg-2 flex items-center justify-center font-mono font-bold text-cyan text-sm shadow-sm">
              RA
            </div>
            <div>
              <span className="font-mono text-xs text-cyan tracking-wider uppercase block">
                Public Codebase Survey
              </span>
              <span className="font-mono font-bold text-sm tracking-tight text-text-0">
                Repo Archaeologist
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Rate limit status pill */}
            <div
              className="hidden sm:inline-flex items-center gap-2 px-2.5 py-1 rounded bg-bg-2 border border-border text-xs font-mono"
              title="GitHub API token status"
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  tokenConfigured ? 'bg-cyan' : 'bg-amber'
                }`}
              />
              <span className="text-text-1">
                {tokenConfigured === null
                  ? 'Connecting...'
                  : tokenConfigured
                  ? 'Token Active (5k/hr)'
                  : 'Public (60/hr)'}
              </span>
            </div>

            <Link
              to="/styleguide"
              className="text-xs font-mono text-text-1 hover:text-cyan transition-colors border-b border-dashed border-text-2 pb-0.5"
            >
              /styleguide
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 md:px-8 py-10 md:py-16 space-y-16">
        {/* Geological Strata Hero */}
        <section className="relative pt-6 pb-4">
          {/* Strata depth lines decoration */}
          <div className="absolute inset-0 pointer-events-none opacity-20 -z-10 flex flex-col justify-between overflow-hidden">
            <div className="border-b border-border w-full flex items-center justify-between text-[10px] font-mono text-text-2">
              <span>STRATUM 0 — SURFACE MANIFESTS</span>
              <span>DEPTH: 0m</span>
            </div>
            <div className="border-b border-border w-full flex items-center justify-between text-[10px] font-mono text-text-2">
              <span>STRATUM 1 — ENTRY CANDIDATES</span>
              <span>DEPTH: -50m</span>
            </div>
            <div className="border-b border-border w-full flex items-center justify-between text-[10px] font-mono text-text-2">
              <span>STRATUM 2 — IMPORT TOPOLOGY</span>
              <span>DEPTH: -100m</span>
            </div>
          </div>

          <div className="max-w-3xl space-y-4">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-bg-2 border border-border text-xs font-mono text-cyan">
              <Compass className="w-3.5 h-3.5 text-cyan" />
              <span>DETERMINISTIC CODEBASE SURVEYOR</span>
            </div>

            <h1 className="text-3xl md:text-5xl font-mono font-bold tracking-tight text-text-0 leading-tight">
              Excavate & Survey Any Public GitHub Repository
            </h1>

            <p className="text-base md:text-lg text-text-1 leading-relaxed">
              Repo Archaeologist performs deterministic text parsing on public repositories to unearth project structure,
              declared manifests, entry point candidates, and import relationships. Zero AI hallucination—every
              finding is backed by verifiable code evidence.
            </p>
          </div>
        </section>

        {/* The Survey Transit Input Module */}
        <section className="bg-bg-1 border border-border rounded p-6 md:p-8 space-y-6 relative shadow-lg">
          <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-cyan via-violet to-transparent" />

          <form onSubmit={handleSubmit} className="space-y-4">
            <label className="block text-xs font-mono font-medium text-text-1 uppercase tracking-wider">
              Target Repository Locator
            </label>

            <div className="flex flex-col sm:flex-row gap-3">
              <div className="flex-1 relative">
                <div className="flex items-center bg-bg-2 border border-border focus-within:border-cyan rounded transition-colors overflow-hidden">
                  <span className="px-3.5 py-3 text-xs md:text-sm font-mono text-text-2 bg-bg-0 border-r border-border select-none whitespace-nowrap">
                    github.com/
                  </span>
                  <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder="owner/repo (e.g. facebook/react)"
                    className="w-full bg-transparent px-3.5 py-3 text-sm font-mono text-text-0 placeholder:text-text-2 focus:outline-none"
                    autoFocus
                  />
                  {inputValue.trim() && (
                    <div className="pr-3">
                      {validation.valid ? (
                        <CheckCircle2 className="w-4 h-4 text-cyan" />
                      ) : (
                        <AlertCircle className="w-4 h-4 text-amber" />
                      )}
                    </div>
                  )}
                </div>
              </div>

              <Button
                type="submit"
                variant="primary"
                disabled={!validation.valid}
                className="whitespace-nowrap sm:w-auto w-full py-3 px-6 flex items-center justify-center gap-2"
              >
                <span>Analyze Repository</span>
                <ArrowRight className="w-4 h-4" />
              </Button>
            </div>

            {/* Live Inline Validation Feedback */}
            <div className="min-h-[20px] text-xs font-mono">
              {!inputValue.trim() ? (
                <span className="text-text-2">
                  Enter an owner/repo slug or paste a full GitHub repository URL.
                </span>
              ) : validation.valid ? (
                <span className="text-cyan flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan inline-block" />
                  Target verified: <strong className="font-bold">{validation.owner}/{validation.repo}</strong>
                </span>
              ) : (
                <span className="text-amber flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber inline-block" />
                  {validation.error || 'Invalid repository format'}
                </span>
              )}
            </div>
          </form>

          {/* Quick Start Excavation Chips */}
          <div className="pt-4 border-t border-border space-y-2">
            <span className="text-xs font-mono text-text-2 uppercase tracking-wider block">
              Or inspect a verified public repository:
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2.5">
              {EXAMPLE_REPOS.map((ex) => (
                <button
                  key={ex.ownerRepo}
                  type="button"
                  onClick={() => handleSelectExample(ex.ownerRepo)}
                  className="flex flex-col text-left p-3 rounded bg-bg-2 border border-border hover:border-cyan/50 hover:bg-bg-2/80 transition-all group"
                >
                  <span className="font-mono text-xs font-medium text-text-0 group-hover:text-cyan transition-colors truncate">
                    {ex.label}
                  </span>
                  <span className="text-[11px] font-sans text-text-2 mt-0.5 truncate">
                    {ex.category}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* Methodology & Integrity Architecture */}
        <section className="space-y-6">
          <div className="flex items-center justify-between border-b border-border pb-2">
            <h2 className="text-xs font-mono text-text-1 uppercase tracking-wider">
              Survey Methodology & Analysis Integrity
            </h2>
            <span className="text-xs font-mono text-text-2">Deterministic Rules Engine</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Card 1: Provenance Framework */}
            <div className="p-5 rounded bg-bg-1 border border-border space-y-4">
              <div className="flex items-center gap-2 text-cyan">
                <ShieldCheck className="w-5 h-5" />
                <h3 className="font-mono text-sm font-bold text-text-0">Evidence Provenance</h3>
              </div>
              <p className="text-xs text-text-1 leading-relaxed">
                Every finding carries an explicit confidence level and direct evidence link to the underlying GitHub file:
              </p>
              <div className="space-y-2.5 pt-1">
                <div className="p-2.5 rounded bg-bg-2 border border-border space-y-1">
                  <div className="flex items-center justify-between">
                    <ProvenanceStamp confidence="confirmed" />
                    <span className="text-[10px] font-mono text-cyan">Direct Fact</span>
                  </div>
                  <p className="text-[11px] text-text-2">
                    Directly observable fact (e.g. manifest exists, imports resolve to disk).
                  </p>
                </div>
                <div className="p-2.5 rounded bg-bg-2 border border-border space-y-1">
                  <div className="flex items-center justify-between">
                    <ProvenanceStamp confidence="heuristic" />
                    <span className="text-[10px] font-mono text-violet">Inferred Pattern</span>
                  </div>
                  <p className="text-[11px] text-text-2">
                    Inferred from standard conventions (e.g. candidate entry naming).
                  </p>
                </div>
              </div>
            </div>

            {/* Card 2: Archaeological Layers */}
            <div className="p-5 rounded bg-bg-1 border border-border space-y-4">
              <div className="flex items-center gap-2 text-cyan">
                <Layers className="w-5 h-5" />
                <h3 className="font-mono text-sm font-bold text-text-0">Excavation Strata</h3>
              </div>
              <p className="text-xs text-text-1 leading-relaxed">
                Analysis inspects four complementary structural layers without executing repository code:
              </p>
              <ul className="space-y-2 text-xs text-text-1 font-mono pt-1">
                <li className="flex items-start gap-2">
                  <FileCode className="w-4 h-4 text-cyan shrink-0 mt-0.5" />
                  <span>Entry candidates (main, app, cli)</span>
                </li>
                <li className="flex items-start gap-2">
                  <Terminal className="w-4 h-4 text-cyan shrink-0 mt-0.5" />
                  <span>Manifest dependencies (declared)</span>
                </li>
                <li className="flex items-start gap-2">
                  <GitBranch className="w-4 h-4 text-cyan shrink-0 mt-0.5" />
                  <span>Architecture import graph</span>
                </li>
                <li className="flex items-start gap-2">
                  <Search className="w-4 h-4 text-cyan shrink-0 mt-0.5" />
                  <span>Deterministic narrative synthesis</span>
                </li>
              </ul>
            </div>

            {/* Card 3: Strict Safety Boundary */}
            <div className="p-5 rounded bg-bg-1 border border-border space-y-4">
              <div className="flex items-center gap-2 text-cyan">
                <ShieldCheck className="w-5 h-5" />
                <h3 className="font-mono text-sm font-bold text-text-0">Isolation & Safety</h3>
              </div>
              <p className="text-xs text-text-1 leading-relaxed">
                Built for zero-trust security with strict architectural guardrails:
              </p>
              <ul className="space-y-2 text-xs text-text-2 pt-1 leading-relaxed">
                <li className="flex items-start gap-2">
                  <span className="text-cyan font-mono font-bold">•</span>
                  <span><strong>Zero code execution:</strong> Analyzed repositories are parsed strictly as read-only text.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-cyan font-mono font-bold">•</span>
                  <span><strong>Public repositories only:</strong> No OAuth tokens or private repository access required.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-cyan font-mono font-bold">•</span>
                  <span><strong>SSRF protected:</strong> Backend communicates strictly with GitHub REST APIs and raw blobs.</span>
                </li>
              </ul>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-bg-1 py-8 px-4 md:px-8 mt-auto">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono text-text-2">
          <div className="flex items-center gap-3">
            <span className="text-text-1 font-bold">Repo Archaeologist</span>
            <span>•</span>
            <span>Deterministic Analysis Engine</span>
          </div>
          <div>
            <span>Public code inspection instrument • Read-only text parsing</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
