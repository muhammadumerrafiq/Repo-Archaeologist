import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import {
  ArrowLeft,
  RotateCcw,
  FolderTree,
  Terminal,
  Package,
  Layers,
  BookOpen,
  FileText,
} from 'lucide-react';
import { analyzeRepository } from '../api/analyze';
import { ApiError } from '../api/client';
import { validateRepoUrl } from '../lib/validateRepoUrl';
import type { AnalyzeResponse } from '../types/contract';

import { DashboardHeader } from '../components/dashboard/DashboardHeader';
import { TechStackSection } from '../components/dashboard/TechStackSection';
import { EntryPointsSection } from '../components/dashboard/EntryPointsSection';
import { DependenciesSection } from '../components/dashboard/DependenciesSection';
import { FileExplorer } from '../components/dashboard/FileExplorer';
import { GuideSectionView } from '../components/dashboard/GuideSectionView';
import { ReadmeSection } from '../components/dashboard/ReadmeSection';
import { LoadingSkeleton } from '../components/dashboard/LoadingSkeleton';
import { ErrorView } from '../components/dashboard/ErrorView';
import { Banner } from '../components/ui/Banner';
import { Button } from '../components/ui/Button';

export const ResultsDashboard: React.FC = () => {
  const [searchParams] = useSearchParams();
  const repoParam = searchParams.get('repo') || '';

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);
  const [data, setData] = useState<AnalyzeResponse | null>(null);
  const [activeTab, setActiveTab] = useState<
    'all' | 'guide' | 'stack' | 'entries' | 'dependencies' | 'files' | 'readme'
  >('all');

  const executeAnalysis = () => {
    if (!repoParam.trim()) {
      setError(
        new ApiError('INVALID_URL', 'No repository target was specified in the URL query.')
      );
      setLoading(false);
      return;
    }

    const validation = validateRepoUrl(repoParam);
    if (!validation.valid || !validation.owner || !validation.repo) {
      setError(
        new ApiError(
          'INVALID_URL',
          validation.error || 'Invalid repository format. Expected owner/repo.'
        )
      );
      setLoading(false);
      return;
    }

    const targetUrl = `https://github.com/${validation.owner}/${validation.repo}`;
    setLoading(true);
    setError(null);

    const controller = new AbortController();

    analyzeRepository(targetUrl, controller.signal)
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        if (err.name === 'AbortError') {
          // Request was cancelled, do not set state
          return;
        }
        if (err instanceof ApiError) {
          setError(err);
        } else {
          setError(
            new ApiError('UPSTREAM_ERROR', (err as Error).message || 'Survey request failed')
          );
        }
        setLoading(false);
      });

    return () => {
      controller.abort();
    };
  };

  useEffect(() => {
    const cleanup = executeAnalysis();
    return () => {
      if (cleanup) cleanup();
    };
  }, [repoParam]);

  return (
    <div className="min-h-screen bg-bg-0 text-text-0 flex flex-col font-sans selection:bg-cyan/20 selection:text-cyan">
      {/* Top Navigation Bar */}
      <header className="border-b border-border bg-bg-1/80 backdrop-blur sticky top-0 z-40 px-4 md:px-8 py-3">
        <div className="max-w-6xl mx-auto flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Link
              to="/"
              className="p-1 rounded text-text-2 hover:text-cyan hover:bg-bg-2 transition-colors"
              title="Return to Target Locator"
            >
              <ArrowLeft className="w-5 h-5" />
            </Link>

            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded border border-cyan/40 bg-bg-2 flex items-center justify-center font-mono font-bold text-cyan text-xs shadow-sm">
                RA
              </div>
              <div className="hidden sm:block">
                <span className="font-mono text-[10px] text-cyan tracking-wider uppercase block">
                  Excavation Results
                </span>
                <span className="font-mono font-bold text-xs tracking-tight text-text-0 truncate max-w-xs block">
                  {repoParam || 'Dashboard'}
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Button
              type="button"
              variant="secondary"
              onClick={executeAnalysis}
              disabled={loading}
              className="text-xs font-mono py-1.5 px-3 flex items-center gap-1.5"
            >
              <RotateCcw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span className="hidden sm:inline">Refresh Survey</span>
            </Button>

            <Link
              to="/styleguide"
              className="text-xs font-mono text-text-2 hover:text-cyan transition-colors"
            >
              /styleguide
            </Link>
          </div>
        </div>
      </header>

      {/* Main Dashboard Body */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 md:px-8 py-8 space-y-8">
        {loading && <LoadingSkeleton repoTarget={repoParam} />}

        {error && !loading && (
          <ErrorView
            code={error.code}
            message={error.message}
            retryAfter={error.retryAfter}
            onRetry={executeAnalysis}
          />
        )}

        {data && !loading && !error && (
          <div className="space-y-8 animate-fade-in">
            {/* Warning Banners (Honest reporting of partial results) */}
            {data.warnings.length > 0 && (
              <div className="space-y-2">
                {data.warnings.map((warn, i) => (
                  <Banner
                    key={i}
                    type="warning"
                    code={warn.code}
                    message={warn.message}
                  />
                ))}
              </div>
            )}

            {/* Dashboard Metadata Header */}
            <DashboardHeader repo={data.repo} stats={data.stats} />

            {/* View Selector Filter Tabs */}
            <div className="flex items-center gap-1.5 overflow-x-auto pb-1 border-b border-border text-xs font-mono">
              <button
                type="button"
                onClick={() => setActiveTab('all')}
                className={`px-3 py-1.5 rounded transition-colors whitespace-nowrap ${
                  activeTab === 'all'
                    ? 'bg-cyan text-bg-0 font-bold'
                    : 'text-text-1 hover:text-text-0 hover:bg-bg-2'
                }`}
              >
                All Sections
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('guide')}
                className={`px-3 py-1.5 rounded transition-colors flex items-center gap-1.5 whitespace-nowrap ${
                  activeTab === 'guide'
                    ? 'bg-cyan text-bg-0 font-bold'
                    : 'text-text-1 hover:text-text-0 hover:bg-bg-2'
                }`}
              >
                <BookOpen className="w-3.5 h-3.5" />
                <span>Architecture Guide</span>
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('stack')}
                className={`px-3 py-1.5 rounded transition-colors flex items-center gap-1.5 whitespace-nowrap ${
                  activeTab === 'stack'
                    ? 'bg-cyan text-bg-0 font-bold'
                    : 'text-text-1 hover:text-text-0 hover:bg-bg-2'
                }`}
              >
                <Layers className="w-3.5 h-3.5" />
                <span>Tech Stack</span>
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('entries')}
                className={`px-3 py-1.5 rounded transition-colors flex items-center gap-1.5 whitespace-nowrap ${
                  activeTab === 'entries'
                    ? 'bg-cyan text-bg-0 font-bold'
                    : 'text-text-1 hover:text-text-0 hover:bg-bg-2'
                }`}
              >
                <Terminal className="w-3.5 h-3.5" />
                <span>Entry Points ({data.entry_points.length})</span>
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('dependencies')}
                className={`px-3 py-1.5 rounded transition-colors flex items-center gap-1.5 whitespace-nowrap ${
                  activeTab === 'dependencies'
                    ? 'bg-cyan text-bg-0 font-bold'
                    : 'text-text-1 hover:text-text-0 hover:bg-bg-2'
                }`}
              >
                <Package className="w-3.5 h-3.5" />
                <span>Dependencies</span>
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('files')}
                className={`px-3 py-1.5 rounded transition-colors flex items-center gap-1.5 whitespace-nowrap ${
                  activeTab === 'files'
                    ? 'bg-cyan text-bg-0 font-bold'
                    : 'text-text-1 hover:text-text-0 hover:bg-bg-2'
                }`}
              >
                <FolderTree className="w-3.5 h-3.5" />
                <span>File Tree</span>
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('readme')}
                className={`px-3 py-1.5 rounded transition-colors flex items-center gap-1.5 whitespace-nowrap ${
                  activeTab === 'readme'
                    ? 'bg-cyan text-bg-0 font-bold'
                    : 'text-text-1 hover:text-text-0 hover:bg-bg-2'
                }`}
              >
                <FileText className="w-3.5 h-3.5" />
                <span>README</span>
              </button>
            </div>

            {/* Dashboard Sections Grid */}
            <div className="space-y-8">
              {(activeTab === 'all' || activeTab === 'guide') && (
                <GuideSectionView guide={data.guide} />
              )}

              {(activeTab === 'all' || activeTab === 'stack') && (
                <TechStackSection
                  techStack={data.tech_stack}
                  configFiles={data.config_files}
                  languages={data.languages}
                />
              )}

              {(activeTab === 'all' || activeTab === 'entries') && (
                <EntryPointsSection entryPoints={data.entry_points} />
              )}

              {(activeTab === 'all' || activeTab === 'dependencies') && (
                <DependenciesSection dependencies={data.dependencies} />
              )}

              {(activeTab === 'all' || activeTab === 'files') && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h2 className="font-mono text-sm font-bold text-text-0 uppercase tracking-wider flex items-center gap-2">
                      <FolderTree className="w-4 h-4 text-cyan" />
                      <span>Codebase File Explorer</span>
                    </h2>
                    <span className="text-xs font-mono text-text-2">
                      {data.file_tree.nodes.length} nodes indexed
                    </span>
                  </div>
                  <FileExplorer
                    nodes={data.file_tree.nodes}
                    truncated={data.file_tree.truncated}
                  />
                </div>
              )}

              {(activeTab === 'all' || activeTab === 'readme') && (
                <ReadmeSection readme={data.readme} />
              )}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-bg-1 py-8 px-4 md:px-8 mt-auto">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-mono text-text-2">
          <div className="flex items-center gap-3">
            <span className="text-text-1 font-bold">Repo Archaeologist</span>
            <span>•</span>
            <span>Public Codebase Survey Dashboard</span>
          </div>
          <div>
            <span>Deterministic Rules Engine • Zero Foreign Code Execution</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
