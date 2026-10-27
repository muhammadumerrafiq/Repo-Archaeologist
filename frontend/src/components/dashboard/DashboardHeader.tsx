import React from 'react';
import {
  ExternalLink,
  Star,
  GitFork,
  Scale,
  Calendar,
  HardDrive,
  GitBranch,
  Clock,
} from 'lucide-react';
import type { RepoMeta, AnalysisStats } from '../../types/contract';

interface DashboardHeaderProps {
  repo: RepoMeta;
  stats: AnalysisStats;
  onRefresh?: () => void;
}

export const DashboardHeader: React.FC<DashboardHeaderProps> = ({ repo, stats }) => {
  const formattedDate = repo.pushed_at
    ? new Date(repo.pushed_at).toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    : 'Unknown';

  return (
    <div className="bg-bg-1 border border-border rounded p-6 space-y-4">
      {/* Title & Actions Row */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-mono text-xs text-cyan uppercase tracking-wider">
              SURVEY TARGET
            </span>
            {repo.archived && (
              <span className="px-1.5 py-0.5 rounded bg-amber/10 border border-amber/30 text-amber text-[10px] font-mono">
                ARCHIVED
              </span>
            )}
            {repo.primary_language && (
              <span className="px-2 py-0.5 rounded bg-bg-2 border border-border text-text-0 text-[11px] font-mono">
                {repo.primary_language}
              </span>
            )}
          </div>

          <div className="flex items-center gap-3">
            <h1 className="text-2xl md:text-3xl font-mono font-bold text-text-0 tracking-tight">
              {repo.owner}/<span className="text-cyan">{repo.name}</span>
            </h1>
            <a
              href={repo.html_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-text-2 hover:text-cyan transition-colors p-1"
              title="Open repository on GitHub"
            >
              <ExternalLink className="w-5 h-5" />
            </a>
          </div>
        </div>

        {/* Survey Timing & Stats Pill */}
        <div className="flex items-center gap-2 self-start md:self-auto">
          <div className="px-3 py-1.5 rounded bg-bg-2 border border-border text-xs font-mono text-text-1 flex items-center gap-3">
            <span className="flex items-center gap-1.5 text-cyan">
              <Clock className="w-3.5 h-3.5" />
              <span>{stats.analysis_ms}ms</span>
            </span>
            <span className="text-text-2">•</span>
            <span>{stats.files_fetched} files fetched</span>
            <span className="text-text-2">•</span>
            <span>{stats.api_calls_made} API calls</span>
          </div>
        </div>
      </div>

      {/* Description */}
      {repo.description ? (
        <p className="text-sm text-text-1 leading-relaxed max-w-4xl font-sans">
          {repo.description}
        </p>
      ) : (
        <p className="text-xs text-text-2 italic font-mono">No description provided.</p>
      )}

      {/* Topics */}
      {repo.topics && repo.topics.length > 0 && (
        <div className="flex flex-wrap gap-1.5 pt-1">
          {repo.topics.map((topic) => (
            <span
              key={topic}
              className="px-2 py-0.5 rounded bg-bg-2 border border-border text-[11px] font-mono text-text-1"
            >
              #{topic}
            </span>
          ))}
        </div>
      )}

      {/* Metadata Badges Strip */}
      <div className="pt-3 border-t border-border flex flex-wrap items-center gap-4 text-xs font-mono text-text-2">
        <div className="flex items-center gap-1.5" title="Stars">
          <Star className="w-3.5 h-3.5 text-amber" />
          <span className="text-text-0 font-medium">{repo.stars.toLocaleString()}</span>
          <span>stars</span>
        </div>

        <div className="flex items-center gap-1.5" title="Forks">
          <GitFork className="w-3.5 h-3.5 text-text-1" />
          <span className="text-text-0 font-medium">{repo.forks.toLocaleString()}</span>
          <span>forks</span>
        </div>

        <div className="flex items-center gap-1.5" title="Default branch">
          <GitBranch className="w-3.5 h-3.5 text-cyan" />
          <span className="text-text-0">{repo.default_branch}</span>
        </div>

        {repo.license && (
          <div className="flex items-center gap-1.5" title="License">
            <Scale className="w-3.5 h-3.5 text-text-1" />
            <span className="text-text-0">{repo.license}</span>
          </div>
        )}

        <div className="flex items-center gap-1.5" title="Repository size">
          <HardDrive className="w-3.5 h-3.5 text-text-1" />
          <span className="text-text-0">{(repo.size_kb / 1024).toFixed(1)} MB</span>
        </div>

        <div className="flex items-center gap-1.5" title="Last commit date">
          <Calendar className="w-3.5 h-3.5 text-text-1" />
          <span>Last pushed:</span>
          <span className="text-text-0">{formattedDate}</span>
        </div>
      </div>
    </div>
  );
};
