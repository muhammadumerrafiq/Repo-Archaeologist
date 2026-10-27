/**
 * Repo Archaeologist Data Contract
 * Synchronized with backend/app/schemas/contract.py
 */

export type Confidence = 'confirmed' | 'heuristic';

export type NodeRole = 'entry' | 'source' | 'config' | 'test' | 'docs' | 'dependency_group';

export type EdgeType = 'import' | 'config' | 'dependency';

export type FileKind =
  | 'source'
  | 'test'
  | 'config'
  | 'docs'
  | 'asset'
  | 'data'
  | 'build'
  | 'ci'
  | 'lockfile'
  | 'unknown';

export type ErrorCode =
  | 'INVALID_URL'
  | 'UNSUPPORTED_HOST'
  | 'NOT_FOUND'
  | 'PRIVATE_OR_FORBIDDEN'
  | 'RATE_LIMITED'
  | 'UPSTREAM_ERROR'
  | 'TIMEOUT';

export interface HealthResponse {
  status: 'ok';
  github_token_configured: boolean;
}

export interface AnalyzeRequest {
  url: string;
}

export interface Evidence {
  path: string;
  reason: string;
  github_url: string;
}

export interface Finding {
  id: string; // e.g. ART-001
  label: string;
  category: string;
  confidence: Confidence;
  summary: string;
  evidence: Evidence[];
}

export interface RepoMeta {
  owner: string;
  name: string;
  full_name: string;
  description: string | null;
  html_url: string;
  default_branch: string;
  stars: number;
  forks: number;
  open_issues: number;
  license: string | null;
  primary_language: string | null;
  topics: string[];
  size_kb: number;
  pushed_at: string | null;
  archived: boolean;
}

export interface LanguageBreakdown {
  name: string;
  bytes: number;
  percent: number;
}

export interface DependencyItem {
  name: string;
  version_spec: string | null;
  evidence: Evidence;
}

export interface EcosystemDependencies {
  ecosystem: string;
  manifest_path: string;
  runtime: DependencyItem[];
  dev: DependencyItem[];
}

export interface DependenciesReport {
  ecosystems: EcosystemDependencies[];
}

export interface FileTreeNode {
  path: string;
  type: 'file' | 'dir';
  size: number | null;
  file_kind: FileKind;
  description: string | null;
  github_url: string;
}

export interface FileTreeReport {
  nodes: FileTreeNode[];
  truncated: boolean;
}

export interface GraphNode {
  id: string;
  path: string;
  role: NodeRole;
  confidence: Confidence;
  evidence: Evidence[];
}

export interface GraphEdge {
  source: string;
  target: string;
  type: EdgeType;
  confidence: Confidence;
  evidence: Evidence[];
}

export interface GraphReport {
  nodes: GraphNode[];
  edges: GraphEdge[];
  capped: boolean;
}

export interface GuideSection {
  title: string;
  body: string;
  finding_refs: string[];
}

export interface ReadmeReport {
  found: boolean;
  excerpt: string | null;
  html_url: string | null;
}

export interface AnalysisWarning {
  code: string;
  message: string;
}

export interface AnalysisStats {
  files_in_tree: number;
  files_fetched: number;
  api_calls_made: number;
  analysis_ms: number;
}

export interface AnalyzeResponse {
  repo: RepoMeta;
  languages: LanguageBreakdown[];
  tech_stack: Finding[];
  config_files: Finding[];
  entry_points: Finding[];
  dependencies: DependenciesReport;
  file_tree: FileTreeReport;
  graph: GraphReport;
  guide: GuideSection[];
  readme: ReadmeReport;
  warnings: AnalysisWarning[];
  stats: AnalysisStats;
}

export interface ErrorDetail {
  code: ErrorCode;
  message: string;
  retry_after: number | null;
}

export interface ErrorResponse {
  error: ErrorDetail;
}
