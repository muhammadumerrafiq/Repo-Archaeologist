import React, { useState } from 'react';
import { ProvenanceStamp } from '../components/ui/ProvenanceStamp';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Banner } from '../components/ui/Banner';
import { Skeleton } from '../components/ui/Skeleton';
import { ArtifactCard } from '../components/artifacts/ArtifactCard';
import { EvidenceDrawer } from '../components/artifacts/EvidenceDrawer';
import { ExplorerRow } from '../components/explorer/ExplorerRow';
import type { Finding, FileTreeNode } from '../types/contract';

const SAMPLE_CONFIRMED_FINDING: Finding = {
  id: 'ART-001',
  label: 'React Framework',
  category: 'Framework',
  confidence: 'confirmed',
  summary: 'Declared in package.json dependencies as ^18.2.0',
  evidence: [
    {
      path: 'package.json',
      reason: "Declared under 'dependencies.react: ^18.2.0' in root package.json",
      github_url: 'https://github.com/facebook/react/blob/main/package.json',
    },
    {
      path: 'src/main.tsx',
      reason: "Direct import 'import React from \"react\"' parsed in source AST",
      github_url: 'https://github.com/facebook/react/blob/main/src/main.tsx',
    },
  ],
};

const SAMPLE_HEURISTIC_FINDING: Finding = {
  id: 'ART-002',
  label: 'Application Entry Candidate',
  category: 'Entry Point',
  confidence: 'heuristic',
  summary: 'Inferred by standard entry point naming convention (src/main.tsx)',
  evidence: [
    {
      path: 'src/main.tsx',
      reason: 'Standard frontend bootstrap entry file; candidate execution start',
      github_url: 'https://github.com/facebook/react/blob/main/src/main.tsx',
    },
  ],
};

const SAMPLE_FILE_NODES: FileTreeNode[] = [
  {
    path: 'package.json',
    type: 'file',
    size: 1024,
    file_kind: 'config',
    description: 'Node.js package manifest and dependency definitions',
    github_url: 'https://github.com/owner/repo/blob/main/package.json',
  },
  {
    path: 'src',
    type: 'dir',
    size: null,
    file_kind: 'unknown',
    description: null,
    github_url: 'https://github.com/owner/repo/tree/main/src',
  },
  {
    path: 'src/main.tsx',
    type: 'file',
    size: 2048,
    file_kind: 'source',
    description: null,
    github_url: 'https://github.com/owner/repo/blob/main/src/main.tsx',
  },
  {
    path: 'src/App.test.tsx',
    type: 'file',
    size: 1536,
    file_kind: 'test',
    description: null,
    github_url: 'https://github.com/owner/repo/blob/main/src/App.test.tsx',
  },
];

export const StyleguidePage: React.FC = () => {
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [inputValue, setInputValue] = useState('facebook/react');
  const [inputError, setInputError] = useState('');

  const handleInspect = (finding: Finding) => {
    setSelectedFinding(finding);
    setIsDrawerOpen(true);
  };

  return (
    <div className="min-h-screen bg-bg-0 text-text-0 py-10 px-4 sm:px-8 max-w-5xl mx-auto space-y-12">
      {/* Header */}
      <header className="border-b border-line pb-6">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-mono text-xs text-cyan uppercase tracking-widest bg-cyan/10 px-2 py-0.5 border border-cyan/20">
            Design System Verification
          </span>
          <span className="font-mono text-xs text-text-2">/styleguide</span>
        </div>
        <h1 className="text-3xl font-medium tracking-tight mt-2">
          The Survey Sheet Design System
        </h1>
        <p className="text-sm text-text-1 mt-1 max-w-2xl font-mono">
          Precision instrument interface tokens, provenances, typography, and signature components.
          Zero AI hype, no gradient blobs, strict WCAG AA contrast.
        </p>
      </header>

      {/* 1. Color Palette Tokens */}
      <section className="space-y-4">
        <h2 className="font-mono text-xs uppercase tracking-widest text-text-2 flex items-center gap-2">
          <span className="w-1.5 h-1.5 bg-cyan rounded-full" />
          <span>01. Semantic Color Tokens</span>
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-3">
          <div className="p-3 bg-bg-0 border border-line rounded-[2px] space-y-1">
            <div className="w-full h-8 bg-bg-0 border border-line-strong rounded-[2px]" />
            <div className="font-mono text-xs text-text-0 font-medium">--bg-0</div>
            <div className="font-mono text-[10px] text-text-2">#07080A (App BG)</div>
          </div>
          <div className="p-3 bg-bg-1 border border-line rounded-[2px] space-y-1">
            <div className="w-full h-8 bg-bg-1 border border-line-strong rounded-[2px]" />
            <div className="font-mono text-xs text-text-0 font-medium">--bg-1</div>
            <div className="font-mono text-[10px] text-text-2">#0C0E12 (Panels)</div>
          </div>
          <div className="p-3 bg-bg-2 border border-line rounded-[2px] space-y-1">
            <div className="w-full h-8 bg-bg-2 border border-line-strong rounded-[2px]" />
            <div className="font-mono text-xs text-text-0 font-medium">--bg-2</div>
            <div className="font-mono text-[10px] text-text-2">#12151B (Inputs)</div>
          </div>
          <div className="p-3 bg-bg-1 border border-cyan/40 rounded-[2px] space-y-1">
            <div className="w-full h-8 bg-cyan rounded-[2px]" />
            <div className="font-mono text-xs text-cyan font-medium">--cyan</div>
            <div className="font-mono text-[10px] text-text-2">#4FD8EB (Confirmed)</div>
          </div>
          <div className="p-3 bg-bg-1 border border-violet/40 rounded-[2px] space-y-1">
            <div className="w-full h-8 bg-violet rounded-[2px]" />
            <div className="font-mono text-xs text-violet font-medium">--violet</div>
            <div className="font-mono text-[10px] text-text-2">#9D8CFF (Heuristic)</div>
          </div>
          <div className="p-3 bg-bg-1 border border-amber/40 rounded-[2px] space-y-1">
            <div className="w-full h-8 bg-amber rounded-[2px]" />
            <div className="font-mono text-xs text-amber font-medium">--amber</div>
            <div className="font-mono text-[10px] text-text-2">#E8B964 (Warning)</div>
          </div>
        </div>
      </section>

      {/* 2. Type Scale */}
      <section className="space-y-4">
        <h2 className="font-mono text-xs uppercase tracking-widest text-text-2 flex items-center gap-2">
          <span className="w-1.5 h-1.5 bg-cyan rounded-full" />
          <span>02. Typography &amp; Scale</span>
        </h2>
        <div className="bg-bg-1 border border-line p-5 rounded-[2px] space-y-4 font-mono">
          <div>
            <span className="text-[11px] text-text-2 block uppercase mb-1">Display Title (44px)</span>
            <div className="text-4xl font-medium tracking-tight text-text-0">Site Survey &amp; Excavation</div>
          </div>
          <div className="border-t border-line pt-3">
            <span className="text-[11px] text-text-2 block uppercase mb-1">Section Header (20px)</span>
            <div className="text-xl font-medium text-text-0">Architecture Stratum Breakdown</div>
          </div>
          <div className="border-t border-line pt-3">
            <span className="text-[11px] text-text-2 block uppercase mb-1">Mono Header (14px)</span>
            <div className="text-sm font-medium text-cyan">ART-001: Vite Configuration Spec</div>
          </div>
          <div className="border-t border-line pt-3">
            <span className="text-[11px] text-text-2 block uppercase mb-1">Body Text (14px Sans)</span>
            <p className="font-sans text-sm text-text-1 max-w-xl">
              Survey of repository structure reveals declared npm dependencies and explicit entry point candidates.
              Deterministic parsing validates file tree contents without executing foreign code.
            </p>
          </div>
        </div>
      </section>

      {/* 3. Provenance Stamps */}
      <section className="space-y-4">
        <h2 className="font-mono text-xs uppercase tracking-widest text-text-2 flex items-center gap-2">
          <span className="w-1.5 h-1.5 bg-cyan rounded-full" />
          <span>03. Provenance Stamps (Section 8.3)</span>
        </h2>
        <div className="bg-bg-1 border border-line p-5 rounded-[2px] flex flex-wrap items-center gap-6">
          <div className="space-y-1.5">
            <ProvenanceStamp confidence="confirmed" />
            <p className="font-mono text-xs text-text-2">Solid outline + filled dot (Direct fact)</p>
          </div>
          <div className="space-y-1.5">
            <ProvenanceStamp confidence="heuristic" />
            <p className="font-mono text-xs text-text-2">Dashed outline + hollow dot (Inferred)</p>
          </div>
        </div>
      </section>

      {/* 4. Artifact Cards */}
      <section className="space-y-4">
        <h2 className="font-mono text-xs uppercase tracking-widest text-text-2 flex items-center gap-2">
          <span className="w-1.5 h-1.5 bg-cyan rounded-full" />
          <span>04. Artifact Cards with Evidence Trigger</span>
        </h2>
        <div className="border border-line rounded-[2px] overflow-hidden">
          <ArtifactCard finding={SAMPLE_CONFIRMED_FINDING} onInspect={handleInspect} />
          <ArtifactCard finding={SAMPLE_HEURISTIC_FINDING} onInspect={handleInspect} />
        </div>
      </section>

      {/* 5. Buttons */}
      <section className="space-y-4">
        <h2 className="font-mono text-xs uppercase tracking-widest text-text-2 flex items-center gap-2">
          <span className="w-1.5 h-1.5 bg-cyan rounded-full" />
          <span>05. Buttons</span>
        </h2>
        <div className="bg-bg-1 border border-line p-5 rounded-[2px] flex flex-wrap items-center gap-3">
          <Button variant="primary">Analyze Repository</Button>
          <Button variant="secondary">View Source Tree</Button>
          <Button variant="ghost">Toggle Details</Button>
          <Button variant="danger">Clear Cache</Button>
          <Button variant="primary" disabled>
            Processing...
          </Button>
        </div>
      </section>

      {/* 6. Inputs */}
      <section className="space-y-4">
        <h2 className="font-mono text-xs uppercase tracking-widest text-text-2 flex items-center gap-2">
          <span className="w-1.5 h-1.5 bg-cyan rounded-full" />
          <span>06. Inputs with Affordance &amp; Validation</span>
        </h2>
        <div className="bg-bg-1 border border-line p-5 rounded-[2px] space-y-4 max-w-xl">
          <Input
            id="sample-url-input"
            prefixAffordance="github.com/"
            value={inputValue}
            onChange={(e) => {
              setInputValue(e.target.value);
              if (e.target.value.includes(' ')) {
                setInputError('Repository URL cannot contain whitespace');
              } else {
                setInputError('');
              }
            }}
            error={inputError}
            placeholder="owner/repo"
          />
        </div>
      </section>

      {/* 7. Explorer Rows */}
      <section className="space-y-4">
        <h2 className="font-mono text-xs uppercase tracking-widest text-text-2 flex items-center gap-2">
          <span className="w-1.5 h-1.5 bg-cyan rounded-full" />
          <span>07. File Explorer Rows with Depth Rail</span>
        </h2>
        <div className="bg-bg-1 border border-line rounded-[2px] overflow-hidden">
          <ExplorerRow node={SAMPLE_FILE_NODES[0]} depth={0} />
          <ExplorerRow node={SAMPLE_FILE_NODES[1]} depth={0} />
          <ExplorerRow node={SAMPLE_FILE_NODES[2]} depth={1} />
          <ExplorerRow node={SAMPLE_FILE_NODES[3]} depth={1} searchQuery="test" />
        </div>
      </section>

      {/* 8. Banners */}
      <section className="space-y-4">
        <h2 className="font-mono text-xs uppercase tracking-widest text-text-2 flex items-center gap-2">
          <span className="w-1.5 h-1.5 bg-cyan rounded-full" />
          <span>08. Honest Warning &amp; Error Banners</span>
        </h2>
        <div className="space-y-2.5">
          <Banner
            type="warning"
            code="TREE_TRUNCATED"
            message="Repository tree was truncated by GitHub API. Analysis covers returned subset."
          />
          <Banner
            type="error"
            code="RATE_LIMITED"
            message="GitHub API rate limit reached. Analysis temporarily throttled; resets in 14 minutes."
          />
        </div>
      </section>

      {/* 9. Skeletons */}
      <section className="space-y-4">
        <h2 className="font-mono text-xs uppercase tracking-widest text-text-2 flex items-center gap-2">
          <span className="w-1.5 h-1.5 bg-cyan rounded-full" />
          <span>09. Layout Skeletons</span>
        </h2>
        <div className="bg-bg-1 border border-line p-5 rounded-[2px] space-y-3">
          <Skeleton className="h-6 w-1/3" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-5/6" />
        </div>
      </section>

      {/* Interactive Evidence Drawer */}
      <EvidenceDrawer
        finding={selectedFinding}
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
      />
    </div>
  );
};
