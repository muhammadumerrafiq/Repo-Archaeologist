import React, { useState, useMemo } from 'react';
import {
  Folder,
  FolderOpen,
  FileCode,
  FileText,
  Settings,
  ChevronRight,
  ChevronDown,
  ExternalLink,
  Search,
} from 'lucide-react';
import type { FileTreeNode, FileKind } from '../../types/contract';

interface FileExplorerProps {
  nodes: FileTreeNode[];
  truncated?: boolean;
}

interface TreeItem {
  name: string;
  path: string;
  type: 'file' | 'dir';
  size: number | null;
  file_kind?: FileKind;
  description?: string | null;
  github_url?: string;
  children: TreeItem[];
}

function buildTree(nodes: FileTreeNode[]): TreeItem[] {
  const root: { [key: string]: any } = {};

  for (const node of nodes) {
    const parts = node.path.split('/');
    let current = root;

    for (let i = 0; i < parts.length; i++) {
      const part = parts[i];
      const isLast = i === parts.length - 1;

      if (!current[part]) {
        current[part] = {
          name: part,
          path: parts.slice(0, i + 1).join('/'),
          type: isLast ? node.type : 'dir',
          size: isLast ? node.size : null,
          file_kind: isLast ? node.file_kind : undefined,
          description: isLast ? node.description : null,
          github_url: isLast ? node.github_url : undefined,
          _children: {},
        };
      }
      current = current[part]._children;
    }
  }

  function toArray(obj: { [key: string]: any }): TreeItem[] {
    const items: TreeItem[] = Object.values(obj).map((val) => ({
      name: val.name,
      path: val.path,
      type: val.type,
      size: val.size,
      file_kind: val.file_kind,
      description: val.description,
      github_url: val.github_url,
      children: toArray(val._children),
    }));

    // Sort: directories first, then alphabetical
    return items.sort((a, b) => {
      if (a.type !== b.type) {
        return a.type === 'dir' ? -1 : 1;
      }
      return a.name.localeCompare(b.name);
    });
  }

  return toArray(root);
}

function getKindBadge(kind?: FileKind): { label: string; colorClass: string } | null {
  switch (kind) {
    case 'config':
      return { label: 'CFG', colorClass: 'text-amber border-amber/30 bg-amber/5' };
    case 'source':
      return { label: 'SRC', colorClass: 'text-cyan border-cyan/30 bg-cyan/5' };
    case 'test':
      return { label: 'TEST', colorClass: 'text-violet border-violet/30 bg-violet/5' };
    case 'docs':
      return { label: 'DOC', colorClass: 'text-text-1 border-text-2/40 bg-bg-2' };
    case 'build':
    case 'ci':
      return { label: 'CI', colorClass: 'text-rust border-rust/30 bg-rust/5' };
    case 'lockfile':
      return { label: 'LOCK', colorClass: 'text-text-2 border-text-2/30 bg-bg-2' };
    default:
      return null;
  }
}

function highlightMatch(text: string, query: string) {
  if (!query) return text;
  const index = text.toLowerCase().indexOf(query.toLowerCase());
  if (index === -1) return text;

  const before = text.substring(0, index);
  const match = text.substring(index, index + query.length);
  const after = text.substring(index + query.length);

  return (
    <>
      {before}
      <mark className="bg-amber/30 text-amber px-0.5 rounded-sm">{match}</mark>
      {after}
    </>
  );
}

export const FileExplorer: React.FC<FileExplorerProps> = ({ nodes, truncated }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [collapsedPaths, setCollapsedPaths] = useState<Set<string>>(new Set());

  const tree = useMemo(() => buildTree(nodes), [nodes]);

  const toggleCollapse = (path: string) => {
    setCollapsedPaths((prev) => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  };

  const expandAll = () => setCollapsedPaths(new Set());
  const collapseAll = () => {
    const allDirs = new Set<string>();
    nodes.forEach((n) => {
      if (n.type === 'dir') allDirs.add(n.path);
    });
    setCollapsedPaths(allDirs);
  };

  // Check if item or any of its children match search
  function matchesSearch(item: TreeItem, query: string): boolean {
    if (!query) return true;
    if (item.name.toLowerCase().includes(query.toLowerCase())) return true;
    if (item.description?.toLowerCase().includes(query.toLowerCase())) return true;
    return item.children.some((child) => matchesSearch(child, query));
  }

  // Count total matches
  const totalFiles = nodes.filter((n) => n.type === 'file').length;
  const totalDirs = nodes.filter((n) => n.type === 'dir').length;

  const renderTree = (items: TreeItem[], depth = 0): React.ReactNode => {
    const query = searchQuery.trim();

    return items
      .filter((item) => matchesSearch(item, query))
      .map((item) => {
        const isDir = item.type === 'dir';
        // Auto-expand if active search query, otherwise respect collapsedPaths
        const isCollapsed = query ? false : collapsedPaths.has(item.path);
        const badge = getKindBadge(item.file_kind);

        return (
          <div key={item.path} className="flex flex-col">
            <div
              className={`group flex items-center justify-between py-1 px-2 hover:bg-bg-2/70 transition-colors rounded-[2px] text-xs font-mono select-none ${
                isDir ? 'cursor-pointer text-text-0' : 'text-text-1'
              }`}
              style={{ paddingLeft: `${Math.max(depth * 16 + 8, 8)}px` }}
              onClick={isDir ? () => toggleCollapse(item.path) : undefined}
            >
              <div className="flex items-center gap-2 min-w-0 flex-1">
                {/* Expand icon / bullet */}
                {isDir ? (
                  <button
                    type="button"
                    className="p-0.5 text-text-2 group-hover:text-cyan transition-colors"
                    aria-label={isCollapsed ? 'Expand directory' : 'Collapse directory'}
                  >
                    {isCollapsed ? (
                      <ChevronRight className="w-3.5 h-3.5" />
                    ) : (
                      <ChevronDown className="w-3.5 h-3.5" />
                    )}
                  </button>
                ) : (
                  <span className="w-3.5 flex justify-center text-text-2">•</span>
                )}

                {/* Type Icon */}
                {isDir ? (
                  isCollapsed ? (
                    <Folder className="w-3.5 h-3.5 text-amber shrink-0" />
                  ) : (
                    <FolderOpen className="w-3.5 h-3.5 text-amber shrink-0" />
                  )
                ) : item.file_kind === 'config' ? (
                  <Settings className="w-3.5 h-3.5 text-amber shrink-0" />
                ) : item.file_kind === 'docs' ? (
                  <FileText className="w-3.5 h-3.5 text-text-2 shrink-0" />
                ) : (
                  <FileCode className="w-3.5 h-3.5 text-cyan shrink-0" />
                )}

                {/* Name */}
                <span className="truncate font-medium text-text-0">
                  {highlightMatch(item.name, query)}
                </span>

                {/* Description if any */}
                {item.description && (
                  <span className="hidden md:inline text-text-2 text-[11px] truncate ml-2">
                    — {highlightMatch(item.description, query)}
                  </span>
                )}
              </div>

              {/* Badges & Size & Link */}
              <div className="flex items-center gap-3 shrink-0 ml-2">
                {badge && (
                  <span
                    className={`px-1.5 py-0.2 rounded text-[10px] font-mono border ${badge.colorClass}`}
                  >
                    {badge.label}
                  </span>
                )}

                {item.size !== null && item.size !== undefined && (
                  <span className="text-[11px] text-text-2 font-mono w-14 text-right">
                    {(item.size / 1024).toFixed(1)} KB
                  </span>
                )}

                {item.github_url && (
                  <a
                    href={item.github_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-text-2 hover:text-cyan p-0.5 opacity-0 group-hover:opacity-100 transition-opacity"
                    title="View file on GitHub"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
            </div>

            {/* Render children if directory is expanded */}
            {isDir && !isCollapsed && item.children.length > 0 && (
              <div className="border-l border-border/60 ml-4 my-0.5">
                {renderTree(item.children, depth + 1)}
              </div>
            )}
          </div>
        );
      });
  };

  return (
    <div className="bg-bg-1 border border-border rounded flex flex-col overflow-hidden">
      {/* Explorer Controls Bar */}
      <div className="p-3 border-b border-border bg-bg-2/50 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2.5">
        <div className="relative flex-1">
          <Search className="w-3.5 h-3.5 text-text-2 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search files by path or description..."
            className="w-full bg-bg-2 border border-border rounded px-3 py-1.5 pl-8 text-xs font-mono text-text-0 placeholder:text-text-2 focus:border-cyan focus:outline-none"
          />
        </div>

        <div className="flex items-center gap-2 justify-between sm:justify-end text-xs font-mono text-text-2">
          <div className="flex items-center gap-1.5">
            <button
              type="button"
              onClick={expandAll}
              className="px-2 py-1 rounded bg-bg-2 hover:bg-bg-0 hover:text-cyan transition-colors"
            >
              Expand
            </button>
            <button
              type="button"
              onClick={collapseAll}
              className="px-2 py-1 rounded bg-bg-2 hover:bg-bg-0 hover:text-cyan transition-colors"
            >
              Collapse
            </button>
          </div>

          <div className="border-l border-border pl-2 flex items-center gap-2 text-[11px]">
            <span>{totalFiles} files</span>
            <span>•</span>
            <span>{totalDirs} dirs</span>
          </div>
        </div>
      </div>

      {/* File Tree View */}
      <div className="p-2 max-h-[500px] overflow-y-auto font-mono text-xs">
        {tree.length === 0 ? (
          <div className="p-8 text-center text-text-2 font-mono text-xs">
            Repository has an empty file tree.
          </div>
        ) : (
          renderTree(tree)
        )}
      </div>

      {/* Truncated notice footer if tree was truncated */}
      {truncated && (
        <div className="px-3 py-2 border-t border-border bg-amber/5 text-amber text-xs font-mono flex items-center justify-between">
          <span>Notice: File tree was truncated by GitHub API cap (first 100,000 entries).</span>
        </div>
      )}
    </div>
  );
};
