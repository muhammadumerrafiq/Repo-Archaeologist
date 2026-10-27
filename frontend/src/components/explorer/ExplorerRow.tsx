import React from 'react';
import { File, Folder, ExternalLink, Code2, Wrench, FileText, Package, Database, ShieldCheck } from 'lucide-react';
import type { FileTreeNode, FileKind } from '../../types/contract';

interface ExplorerRowProps {
  node: FileTreeNode;
  depth?: number;
  searchQuery?: string;
}

const KIND_CONFIG: Record<FileKind, { label: string; color: string; icon: React.FC<{ className?: string }> }> = {
  source: { label: 'SRC', color: 'text-cyan border-cyan/40', icon: Code2 },
  test: { label: 'TEST', color: 'text-violet border-violet/40', icon: ShieldCheck },
  config: { label: 'CFG', color: 'text-amber border-amber/40', icon: Wrench },
  docs: { label: 'DOC', color: 'text-text-1 border-text-2', icon: FileText },
  lockfile: { label: 'LOCK', color: 'text-amber border-amber/30', icon: Package },
  asset: { label: 'ASSET', color: 'text-text-2 border-text-2/40', icon: File },
  data: { label: 'DATA', color: 'text-text-1 border-line-strong', icon: Database },
  build: { label: 'BUILD', color: 'text-text-2 border-line', icon: File },
  ci: { label: 'CI', color: 'text-cyan border-cyan/30', icon: Wrench },
  unknown: { label: 'FILE', color: 'text-text-2 border-line', icon: File },
};

export const ExplorerRow: React.FC<ExplorerRowProps> = ({
  node,
  depth = 0,
  searchQuery = '',
}) => {
  const isDir = node.type === 'dir';
  const filename = node.path.split('/').pop() || node.path;
  const kindInfo = KIND_CONFIG[node.file_kind] || KIND_CONFIG.unknown;
  const KindIcon = isDir ? Folder : kindInfo.icon;

  // Highlight search matches
  const highlightName = (name: string, query: string) => {
    if (!query) return name;
    const idx = name.toLowerCase().indexOf(query.toLowerCase());
    if (idx === -1) return name;
    return (
      <>
        {name.slice(0, idx)}
        <mark className="bg-cyan/30 text-cyan px-0.5 rounded-[1px]">{name.slice(idx, idx + query.length)}</mark>
        {name.slice(idx + query.length)}
      </>
    );
  };

  return (
    <div
      className="flex items-center justify-between py-1.5 px-3 hover:bg-bg-2 border-b border-line/60 font-mono text-xs group transition-colors"
      style={{ paddingLeft: `${Math.max(12, depth * 20)}px` }}
    >
      <div className="flex items-center gap-2 truncate">
        {/* Depth Rail visual marker */}
        {depth > 0 && (
          <span className="w-1.5 h-1.5 rounded-full bg-line-strong shrink-0" aria-hidden="true" />
        )}

        <KindIcon className={`w-3.5 h-3.5 shrink-0 ${isDir ? 'text-amber' : 'text-text-2'}`} />

        <span className="text-text-0 truncate font-medium">
          {highlightName(filename, searchQuery)}
        </span>

        {node.description && (
          <span className="text-text-2 truncate text-[11px] hidden md:inline">
            — {node.description}
          </span>
        )}
      </div>

      <div className="flex items-center gap-3 shrink-0">
        {!isDir && (
          <span
            className={`text-[10px] px-1.5 py-0.2 border rounded-[2px] uppercase ${kindInfo.color}`}
          >
            {kindInfo.label}
          </span>
        )}

        {node.size !== null && node.size !== undefined && (
          <span className="text-text-2 text-[11px] w-14 text-right">
            {(node.size / 1024).toFixed(1)} KB
          </span>
        )}

        {node.github_url && (
          <a
            href={node.github_url}
            target="_blank"
            rel="noopener noreferrer"
            aria-label={`View ${node.path} on GitHub`}
            className="text-text-2 hover:text-cyan opacity-0 group-hover:opacity-100 transition-opacity p-0.5"
          >
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        )}
      </div>
    </div>
  );
};
