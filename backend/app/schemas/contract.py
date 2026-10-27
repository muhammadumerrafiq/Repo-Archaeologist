from __future__ import annotations
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, HttpUrl

# Enums / Literal Types
Confidence = Literal["confirmed", "heuristic"]
NodeRole = Literal["entry", "source", "config", "test", "docs", "dependency_group"]
EdgeType = Literal["import", "config", "dependency"]
FileKind = Literal[
    "source",
    "test",
    "config",
    "docs",
    "asset",
    "data",
    "build",
    "ci",
    "lockfile",
    "unknown"
]
ErrorCode = Literal[
    "INVALID_URL",
    "UNSUPPORTED_HOST",
    "NOT_FOUND",
    "PRIVATE_OR_FORBIDDEN",
    "RATE_LIMITED",
    "UPSTREAM_ERROR",
    "TIMEOUT"
]

# Health Check Contract
class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    github_token_configured: bool

# Request Contract
class AnalyzeRequest(BaseModel):
    url: str = Field(..., description="Public GitHub repository URL (e.g. https://github.com/owner/repo)")

# Supporting Models
class Evidence(BaseModel):
    path: str
    reason: str
    github_url: str

class Finding(BaseModel):
    id: str = Field(..., description="Artifact catalog ID, e.g. ART-001")
    label: str
    category: str
    confidence: Confidence
    summary: str
    evidence: List[Evidence] = Field(default_factory=list)

class RepoMeta(BaseModel):
    owner: str
    name: str
    full_name: str
    description: Optional[str] = None
    html_url: str
    default_branch: str
    stars: int
    forks: int
    open_issues: int
    license: Optional[str] = None
    primary_language: Optional[str] = None
    topics: List[str] = Field(default_factory=list)
    size_kb: int
    pushed_at: Optional[str] = None
    archived: bool

class LanguageBreakdown(BaseModel):
    name: str
    bytes: int
    percent: float

class DependencyItem(BaseModel):
    name: str
    version_spec: Optional[str] = None
    evidence: Evidence

class EcosystemDependencies(BaseModel):
    ecosystem: str
    manifest_path: str
    runtime: List[DependencyItem] = Field(default_factory=list)
    dev: List[DependencyItem] = Field(default_factory=list)

class DependenciesReport(BaseModel):
    ecosystems: List[EcosystemDependencies] = Field(default_factory=list)

class FileTreeNode(BaseModel):
    path: str
    type: Literal["file", "dir"]
    size: Optional[int] = None
    file_kind: FileKind
    description: Optional[str] = None
    github_url: str

class FileTreeReport(BaseModel):
    nodes: List[FileTreeNode] = Field(default_factory=list)
    truncated: bool = False

class GraphNode(BaseModel):
    id: str
    path: str
    role: NodeRole
    confidence: Confidence
    evidence: List[Evidence] = Field(default_factory=list)

class GraphEdge(BaseModel):
    source: str
    target: str
    type: EdgeType
    confidence: Confidence
    evidence: List[Evidence] = Field(default_factory=list)

class GraphReport(BaseModel):
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)
    capped: bool = False

class GuideSection(BaseModel):
    title: str
    body: str
    finding_refs: List[str] = Field(default_factory=list)

class ReadmeReport(BaseModel):
    found: bool
    excerpt: Optional[str] = None
    html_url: Optional[str] = None

class AnalysisWarning(BaseModel):
    code: str
    message: str

class AnalysisStats(BaseModel):
    files_in_tree: int
    files_fetched: int
    api_calls_made: int
    analysis_ms: int

# Main Response Contract
class AnalyzeResponse(BaseModel):
    repo: RepoMeta
    languages: List[LanguageBreakdown] = Field(default_factory=list)
    tech_stack: List[Finding] = Field(default_factory=list)
    config_files: List[Finding] = Field(default_factory=list)
    entry_points: List[Finding] = Field(default_factory=list)
    dependencies: DependenciesReport
    file_tree: FileTreeReport
    graph: GraphReport
    guide: List[GuideSection] = Field(default_factory=list)
    readme: ReadmeReport
    warnings: List[AnalysisWarning] = Field(default_factory=list)
    stats: AnalysisStats

# Error Response Contract
class ErrorDetail(BaseModel):
    code: ErrorCode
    message: str
    retry_after: Optional[int] = None

class ErrorResponse(BaseModel):
    error: ErrorDetail
