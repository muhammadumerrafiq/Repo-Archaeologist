import React, { useState } from 'react';
import { Package, ExternalLink } from 'lucide-react';
import type { DependenciesReport, DependencyItem } from '../../types/contract';

interface DependenciesSectionProps {
  dependencies: DependenciesReport;
}

export const DependenciesSection: React.FC<DependenciesSectionProps> = ({ dependencies }) => {
  const [activeTab, setActiveTab] = useState<'runtime' | 'dev'>('runtime');
  const [filterQuery, setFilterQuery] = useState('');

  const ecosystems = dependencies.ecosystems || [];
  const totalRuntime = ecosystems.reduce((acc, eco) => acc + eco.runtime.length, 0);
  const totalDev = ecosystems.reduce((acc, eco) => acc + eco.dev.length, 0);

  const hasAnyDependencies = totalRuntime > 0 || totalDev > 0;

  return (
    <div className="bg-bg-1 border border-border rounded p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border pb-3">
        <div className="flex items-center gap-2">
          <Package className="w-4 h-4 text-cyan" />
          <h2 className="font-mono text-sm font-bold text-text-0 uppercase tracking-wider">
            Declared Dependencies (Manifest Audit)
          </h2>
        </div>

        <div className="flex items-center gap-2">
          <span className="font-mono text-xs text-text-2 bg-bg-2 px-2 py-0.5 rounded border border-border">
            Declared in manifest, not proven used
          </span>
        </div>
      </div>

      <p className="text-xs text-text-1 leading-relaxed">
        Extracted directly from repository dependency manifests. Every package listed below is declared in the project's
        configuration file.
      </p>

      {!hasAnyDependencies ? (
        <div className="p-6 text-center text-text-2 font-mono text-xs border border-dashed border-border rounded">
          No package manifest files (package.json, requirements.txt, pyproject.toml, go.mod, Cargo.toml) found in this repository.
        </div>
      ) : (
        <div className="space-y-4">
          {/* Controls: Tab selection + Filter */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
            <div className="flex items-center gap-1 bg-bg-2 p-1 rounded border border-border">
              <button
                type="button"
                onClick={() => setActiveTab('runtime')}
                className={`px-3 py-1 rounded text-xs font-mono transition-colors ${
                  activeTab === 'runtime'
                    ? 'bg-cyan text-bg-0 font-bold'
                    : 'text-text-1 hover:text-text-0'
                }`}
              >
                Runtime ({totalRuntime})
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('dev')}
                className={`px-3 py-1 rounded text-xs font-mono transition-colors ${
                  activeTab === 'dev'
                    ? 'bg-cyan text-bg-0 font-bold'
                    : 'text-text-1 hover:text-text-0'
                }`}
              >
                Development ({totalDev})
              </button>
            </div>

            <div className="relative">
              <input
                type="text"
                value={filterQuery}
                onChange={(e) => setFilterQuery(e.target.value)}
                placeholder="Filter dependencies..."
                className="bg-bg-2 border border-border rounded px-3 py-1 text-xs font-mono text-text-0 placeholder:text-text-2 focus:border-cyan focus:outline-none w-full sm:w-60"
              />
            </div>
          </div>

          {/* Ecosystem Manifest Blocks */}
          <div className="space-y-4">
            {ecosystems.map((eco) => {
              const list: DependencyItem[] =
                activeTab === 'runtime' ? eco.runtime : eco.dev;
              const filtered = list.filter((item) =>
                item.name.toLowerCase().includes(filterQuery.toLowerCase())
              );

              if (filtered.length === 0 && filterQuery) {
                return null;
              }

              return (
                <div
                  key={`${eco.ecosystem}-${eco.manifest_path}`}
                  className="rounded bg-bg-2 border border-border overflow-hidden"
                >
                  {/* Manifest Bar */}
                  <div className="p-3 bg-bg-0/60 border-b border-border flex items-center justify-between text-xs font-mono">
                    <div className="flex items-center gap-2">
                      <span className="px-1.5 py-0.5 rounded bg-cyan/10 border border-cyan/30 text-cyan text-[10px] font-bold uppercase">
                        {eco.ecosystem}
                      </span>
                      <span className="text-text-0 font-medium">{eco.manifest_path}</span>
                    </div>

                    <a
                      href={`https://github.com/search?q=${encodeURIComponent(
                        eco.manifest_path
                      )}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-text-2 hover:text-cyan flex items-center gap-1 transition-colors text-[11px]"
                    >
                      <span>Manifest source</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>

                  {/* Dependencies List */}
                  {filtered.length === 0 ? (
                    <div className="p-4 text-center text-text-2 text-xs font-mono">
                      No {activeTab} dependencies declared in this manifest.
                    </div>
                  ) : (
                    <div className="p-2 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                      {filtered.map((dep) => (
                        <div
                          key={dep.name}
                          className="p-2.5 rounded bg-bg-1 border border-border flex items-center justify-between text-xs font-mono hover:border-cyan/30 transition-colors"
                        >
                          <span className="font-medium text-text-0 truncate mr-2">
                            {dep.name}
                          </span>
                          <span className="text-text-2 text-[11px] shrink-0">
                            {dep.version_spec || 'latest'}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
