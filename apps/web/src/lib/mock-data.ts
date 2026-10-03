import { ScanResult, AttackChain, BARQAIExplanation } from "./types";

export const MOCK_SCAN_RESULT: ScanResult = {
  scan_id: "scan_12345",
  scan_status: "completed",
  repository_full_name: "acmecorp/api-gateway",
  pr_number: 442,
  head_sha: "a1b2c3d4e5f6",
  base_sha: "f6e5d4c3b2a1",
  profile: "advanced",
  findings_count: 3,
  severity_summary: {
    critical: 1,
    high: 0,
    medium: 1,
    low: 1,
    info: 0,
  },
  created_at: new Date(Date.now() - 500000).toISOString(),
  completed_at: new Date(Date.now() - 10000).toISOString(),
  policy_result: {
    decision: "review",
    reasons: ["Critical severity finding detected", "Suspicious attack chain correlated"],
    triggered_rules: ["policy.fail_on_critical"]
  },
  engine_results: [
    {
      engine_name: "Code Analysis",
      status: "success",
      findings: [
        {
          finding_id: "f_001",
          rule_id: "code.injection.sql",
          severity: "critical",
          confidence: "high",
          title: "SQL Injection in User Profile Update",
          description: "User input is directly concatenated into a SQL query string without parameterization.",
          explanation_key: "sql_injection",
          recommended_action: "Use parameterized queries or an ORM to handle user input.",
          location: {
            file_path: "src/db/user.ts",
            line_start: 45,
            line_end: 47,
          },
          evidence: [
            {
              evidence_id: "ev_001",
              evidence_type: "observed",
              description: "Direct string concatenation with req.body.username",
              file_path: "src/db/user.ts",
              line_start: 46,
              snippet: "const query = `UPDATE users SET name = '${req.body.username}' WHERE id = ${id}`;",
            }
          ]
        },
        {
          finding_id: "f_002",
          rule_id: "code.style.lint",
          severity: "low",
          confidence: "high",
          title: "Missing return type on function",
          description: "Function does not declare a return type.",
          explanation_key: "lint_missing_type",
          location: {
            file_path: "src/utils/helpers.ts",
            line_start: 12,
          },
          evidence: []
        }
      ]
    },
    {
      engine_name: "Dependency Analysis",
      status: "success",
      findings: [
        {
          finding_id: "f_003",
          rule_id: "dependency.malicious.install_hook",
          severity: "medium",
          confidence: "medium",
          title: "Suspicious install script in dependency",
          description: "A newly added dependency 'color-utils-pro' contains a preinstall script that executes an obfuscated binary.",
          explanation_key: "dep_malicious_hook",
          location: {
            file_path: "package.json",
            line_start: 124,
          },
          evidence: [
            {
              evidence_id: "ev_002",
              evidence_type: "observed",
              description: "preinstall script present",
              file_path: "node_modules/color-utils-pro/package.json",
            }
          ]
        }
      ]
    }
  ],
  attack_chains: [
    {
      chain_id: "ac_001",
      severity: "critical",
      title: "Malicious Package Execution Chain",
      nodes: [
        {
          step: 1,
          category: "dependency",
          description: "New dependency 'color-utils-pro' introduced in PR",
          evidence_ids: []
        },
        {
          step: 2,
          category: "install_hook",
          description: "Package defines a preinstall script",
          finding_id: "f_003",
          evidence_ids: ["ev_002"]
        },
        {
          step: 3,
          category: "process",
          description: "Preinstall script executes base64 decoded payload",
          evidence_ids: []
        },
        {
          step: 4,
          category: "credential_access",
          description: "Payload accesses ~/.aws/credentials",
          evidence_ids: []
        },
        {
          step: 5,
          category: "network",
          description: "Data exfiltrated to suspicious IP via HTTPS",
          evidence_ids: []
        }
      ]
    }
  ],
  barqai_explanation: {
    summary: "The PR introduces a new dependency 'color-utils-pro' which exhibits malicious behavior during installation. The package attempts to read AWS credentials and exfiltrate them.",
    observed: [
      "New package 'color-utils-pro' added to package.json",
      "Package contains preinstall script",
      "File read operation on ~/.aws/credentials"
    ],
    correlated: [
      "Preinstall script execution is directly linked to the file read and subsequent network request to 192.168.1.100"
    ],
    inferred: [
      "The combination of obfuscated install scripts, credential access, and external network requests strongly indicates a supply chain attack (credential exfiltration payload)."
    ],
    evidence_ids: ["ev_002"],
    recommended_action: "Block the PR. Remove 'color-utils-pro' from dependencies and investigate the source of this package."
  }
};
