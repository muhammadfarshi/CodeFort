/**
 * CodeFort Shared TypeScript Types
 *
 * Mirrors the Python Pydantic schemas from packages/schemas/python/codefort_schemas/models.py
 * Evidence taxonomy (SECURITY.md §15, DESIGN_SYSTEM.md §7):
 *   - Observed: directly measured from code/config/runtime
 *   - Correlated: multiple observed signals connected
 *   - Inferred: AI interpretation derived from evidence
 */

// ---------------------------------------------------------------------------
// Enumerations
// ---------------------------------------------------------------------------

export type Severity = 'info' | 'low' | 'medium' | 'high' | 'critical';

export type Confidence = 'low' | 'medium' | 'high';

export type EvidenceType = 'observed' | 'correlated' | 'inferred';

export type ScanStatus = 'pending' | 'running' | 'completed' | 'failed' | 'partial';

export type EngineStatus = 'pending' | 'running' | 'success' | 'failed' | 'skipped';

export type PolicyDecision = 'pass' | 'review' | 'block';

export type AnalysisProfile = 'basic' | 'advanced' | 'runtime_deep' | 'enterprise_policy';

export type PlanTier = 'free' | 'premium' | 'team' | 'enterprise';

export type CapabilityType =
  | 'network'
  | 'shell'
  | 'process'
  | 'filesystem'
  | 'credential_access'
  | 'install_hooks'
  | 'binary_native'
  | 'workflow_privilege';

// ---------------------------------------------------------------------------
// Core Models
// ---------------------------------------------------------------------------

export interface Evidence {
  evidence_id: string;
  evidence_type: EvidenceType;
  description: string;
  file_path?: string;
  line_start?: number;
  line_end?: number;
  snippet?: string;
  metadata?: Record<string, unknown>;
}

export interface Location {
  file_path: string;
  line_start?: number;
  line_end?: number;
  column_start?: number;
  column_end?: number;
}

export interface Finding {
  finding_id: string;
  rule_id: string;
  severity: Severity;
  confidence: Confidence;
  title: string;
  description: string;
  evidence: Evidence[];
  location?: Location;
  explanation_key: string;
  recommended_action?: string;
  metadata?: Record<string, unknown>;
}

export interface CapabilityDiff {
  capability: CapabilityType;
  present_in_base: boolean;
  present_in_head: boolean;
  details?: string;
}

export interface AttackChainNode {
  step: number;
  category: string;
  description: string;
  finding_id?: string;
  evidence_ids: string[];
}

export interface AttackChain {
  chain_id: string;
  severity: Severity;
  title: string;
  nodes: AttackChainNode[];
}

export interface EngineResult {
  engine_name: string;
  status: EngineStatus;
  findings: Finding[];
  capability_diffs: CapabilityDiff[];
  duration_ms?: number;
  error_message?: string;
}

export interface BARQAIExplanation {
  observed: string[];
  correlated: string[];
  inferred: string[];
  evidence_ids: string[];
  summary: string;
  recommended_action: string;
  model_version?: string;
}

export interface PolicyResult {
  decision: PolicyDecision;
  reasons: string[];
  triggered_rules: string[];
}

// ---------------------------------------------------------------------------
// Scan Models
// ---------------------------------------------------------------------------

export interface ScanResult {
  scan_id: string;
  scan_status: ScanStatus;
  repository_full_name: string;
  pr_number: number;
  head_sha: string;
  base_sha: string;
  profile: AnalysisProfile;
  engine_results: EngineResult[];
  attack_chains: AttackChain[];
  barqai_explanation?: BARQAIExplanation;
  policy_result?: PolicyResult;
  created_at: string;
  completed_at?: string;
  findings_count: number;
  severity_summary: Record<string, number>;
}

export interface ScanSummary {
  scan_id: string;
  scan_status: ScanStatus;
  repository_full_name: string;
  pr_number: number;
  head_sha: string;
  profile: AnalysisProfile;
  findings_count: number;
  severity_summary: Record<string, number>;
  policy_decision?: PolicyDecision;
  created_at: string;
  completed_at?: string;
}

export interface HealthResponse {
  status: string;
  app_name: string;
  version: string;
}

// ---------------------------------------------------------------------------
// UI Helpers
// ---------------------------------------------------------------------------

export const SEVERITY_ORDER: Record<Severity, number> = {
  info: 0,
  low: 1,
  medium: 2,
  high: 3,
  critical: 4,
};

export const SEVERITY_COLORS: Record<Severity, { bg: string; text: string; border: string }> = {
  info: { bg: 'bg-gray-500/10', text: 'text-gray-400', border: 'border-gray-500/30' },
  low: { bg: 'bg-blue-500/10', text: 'text-blue-400', border: 'border-blue-500/30' },
  medium: { bg: 'bg-amber-500/10', text: 'text-amber-400', border: 'border-amber-500/30' },
  high: { bg: 'bg-orange-500/10', text: 'text-orange-400', border: 'border-orange-500/30' },
  critical: { bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/30' },
};

export const EVIDENCE_TYPE_LABELS: Record<EvidenceType, string> = {
  observed: 'Observed',
  correlated: 'Correlated',
  inferred: 'Inferred',
};

export const POLICY_COLORS: Record<PolicyDecision, { bg: string; text: string }> = {
  pass: { bg: 'bg-green-500/10', text: 'text-green-400' },
  review: { bg: 'bg-amber-500/10', text: 'text-amber-400' },
  block: { bg: 'bg-red-500/10', text: 'text-red-400' },
};
