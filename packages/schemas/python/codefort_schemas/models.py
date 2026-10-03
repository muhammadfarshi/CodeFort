"""
CodeFort Shared Schemas — Core data models used across API, workers, and engines.

Evidence taxonomy (SECURITY.md §15, DESIGN_SYSTEM.md §7):
  - Observed: directly measured from code/config/runtime
  - Correlated: multiple observed signals connected
  - Inferred: AI interpretation derived from evidence
"""

from __future__ import annotations

import enum
import hashlib
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class Severity(str, enum.Enum):
    """Finding severity levels (DESIGN_SYSTEM.md §6)."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Confidence(str, enum.Enum):
    """Confidence in a finding."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EvidenceType(str, enum.Enum):
    """Evidence taxonomy (SECURITY.md §15)."""
    OBSERVED = "observed"
    CORRELATED = "correlated"
    INFERRED = "inferred"


class ScanStatus(str, enum.Enum):
    """Lifecycle status of a scan."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class EngineStatus(str, enum.Enum):
    """Status of an individual engine within a scan."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class PolicyDecision(str, enum.Enum):
    """Policy evaluation outcome (TRD §TR-014)."""
    PASS = "pass"
    REVIEW = "review"
    BLOCK = "block"


class AnalysisProfile(str, enum.Enum):
    """Analysis depth profiles (TRD §8)."""
    BASIC = "basic"
    ADVANCED = "advanced"
    RUNTIME_DEEP = "runtime_deep"
    ENTERPRISE_POLICY = "enterprise_policy"


class PlanTier(str, enum.Enum):
    """Subscription tiers (PRD §7)."""
    FREE = "free"
    PREMIUM = "premium"
    TEAM = "team"
    ENTERPRISE = "enterprise"


class CapabilityType(str, enum.Enum):
    """Security-sensitive capabilities for diff comparison (TRD §TR-006)."""
    NETWORK = "network"
    SHELL = "shell"
    PROCESS = "process"
    FILESYSTEM = "filesystem"
    CREDENTIAL_ACCESS = "credential_access"
    INSTALL_HOOKS = "install_hooks"
    BINARY_NATIVE = "binary_native"
    WORKFLOW_PRIVILEGE = "workflow_privilege"


# ---------------------------------------------------------------------------
# Core Models
# ---------------------------------------------------------------------------

class Evidence(BaseModel):
    """A single piece of evidence supporting a finding."""
    evidence_id: str
    evidence_type: EvidenceType
    description: str
    file_path: str | None = None
    line_start: int | None = None
    line_end: int | None = None
    snippet: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Location(BaseModel):
    """Location within a file where a finding was detected."""
    file_path: str
    line_start: int | None = None
    line_end: int | None = None
    column_start: int | None = None
    column_end: int | None = None


class Finding(BaseModel):
    """
    A security finding produced by an engine (CODE_STYLE.md §9).

    Contract: input → observations/signals → evidence → finding
    """
    finding_id: str
    rule_id: str  # e.g. "workflow.untrusted_checkout@1"
    severity: Severity
    confidence: Confidence
    title: str
    description: str
    evidence: list[Evidence] = Field(default_factory=list)
    location: Location | None = None
    explanation_key: str  # Key for BARQAI template
    recommended_action: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CapabilityDiff(BaseModel):
    """Before/after security capability comparison (TRD §TR-006)."""
    capability: CapabilityType
    present_in_base: bool
    present_in_head: bool
    details: str | None = None


class AttackChainNode(BaseModel):
    """A single node in an attack-chain correlation."""
    step: int
    category: str  # e.g. "dependency", "install_hook", "process", "credential_access", "network"
    description: str
    finding_id: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)


class AttackChain(BaseModel):
    """A correlated sequence of suspicious behaviors (TRD §TR-007)."""
    chain_id: str
    severity: Severity
    title: str
    nodes: list[AttackChainNode]


class EngineResult(BaseModel):
    """Result from a single analysis engine."""
    engine_name: str
    status: EngineStatus
    findings: list[Finding] = Field(default_factory=list)
    capability_diffs: list[CapabilityDiff] = Field(default_factory=list)
    duration_ms: int | None = None
    error_message: str | None = None


class BARQAIExplanation(BaseModel):
    """
    AI-generated explanation grounded in evidence (TRD §TR-012).

    Must expose: observed facts, correlated signals, inferences,
    relevant evidence, recommended next action.
    """
    observed: list[str]
    correlated: list[str]
    inferred: list[str]
    evidence_ids: list[str]
    summary: str
    recommended_action: str
    model_version: str | None = None


class PolicyResult(BaseModel):
    """Outcome of policy evaluation (TRD §TR-014)."""
    decision: PolicyDecision
    reasons: list[str]
    triggered_rules: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Scan Models
# ---------------------------------------------------------------------------

class ScanRequest(BaseModel):
    """Incoming scan request from a webhook or API call."""
    installation_id: int
    repository_full_name: str  # "owner/repo"
    pr_number: int
    head_sha: str
    base_sha: str
    profile: AnalysisProfile = AnalysisProfile.BASIC
    sender: str | None = None

    @property
    def dedup_key(self) -> str:
        """Idempotency key (TRD §6)."""
        raw = f"{self.repository_full_name}:{self.pr_number}:{self.head_sha}:{self.profile.value}"
        return hashlib.sha256(raw.encode()).hexdigest()


class ScanResult(BaseModel):
    """Complete scan result aggregating all engine outputs."""
    scan_id: str
    scan_status: ScanStatus
    repository_full_name: str
    pr_number: int
    head_sha: str
    base_sha: str
    profile: AnalysisProfile
    engine_results: list[EngineResult] = Field(default_factory=list)
    attack_chains: list[AttackChain] = Field(default_factory=list)
    barqai_explanation: BARQAIExplanation | None = None
    policy_result: PolicyResult | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    findings_count: int = 0
    severity_summary: dict[str, int] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# API Response Models
# ---------------------------------------------------------------------------

class ScanSummary(BaseModel):
    """Lightweight scan summary for listing endpoints."""
    scan_id: str
    scan_status: ScanStatus
    repository_full_name: str
    pr_number: int
    head_sha: str
    profile: AnalysisProfile
    findings_count: int
    severity_summary: dict[str, int] = Field(default_factory=dict)
    policy_decision: PolicyDecision | None = None
    created_at: datetime
    completed_at: datetime | None = None


class WebhookEvent(BaseModel):
    """Parsed GitHub webhook event."""
    event_type: str  # "pull_request"
    action: str  # "opened", "synchronize"
    installation_id: int
    repository_full_name: str
    pr_number: int
    head_sha: str
    base_sha: str
    sender: str
    delivery_id: str


class HealthResponse(BaseModel):
    """API health check response."""
    status: str = "ok"
    app_name: str = "CodeFort"
    version: str = "0.1.0"
