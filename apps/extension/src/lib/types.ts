/**
 * CodeFort Guard Extension Types
 */

export type Severity = 'info' | 'low' | 'medium' | 'high' | 'critical';
export type Confidence = 'low' | 'medium' | 'high';
export type EvidenceType = 'observed' | 'correlated' | 'inferred';
export type ScanStatus = 'pending' | 'running' | 'completed' | 'failed' | 'partial';
export type PolicyDecision = 'pass' | 'review' | 'block';
export type AnalysisProfile = 'basic' | 'advanced' | 'runtime_deep' | 'enterprise_policy';

export interface Evidence {
  evidence_id: string;
  evidence_type: EvidenceType;
  description: string;
  file_path?: string;
  line_start?: number;
  line_end?: number;
  snippet?: string;
}

export interface Finding {
  finding_id: string;
  rule_id: string;
  severity: Severity;
  confidence: Confidence;
  title: string;
  description: string;
  evidence: Evidence[];
  explanation_key: string;
  recommended_action?: string;
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
  status: string;
  findings: Finding[];
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

export interface PRContext {
  owner: string;
  repo: string;
  prNumber: number;
}
