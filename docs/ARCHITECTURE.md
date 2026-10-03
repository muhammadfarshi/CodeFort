# ARCHITECTURE.md

# SupplyGuard System Architecture

## 1. Architecture Overview

```text
                         â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                         â”‚      GitHub.com       â”‚
                         â”‚ PR / Repo / Actions   â”‚
                         â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                    â”‚ Webhooks / API
                                    â–¼
                         â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                         â”‚   GitHub App Layer   â”‚
                         â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                    â–¼
                         â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                         â”‚ Webhook Gateway/API  â”‚
                         â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                    â–¼
                         â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                         â”‚ Security Orchestratorâ”‚
                         â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                    â”‚
        â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
        â–¼                           â–¼                           â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”          â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”          â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Code Engine  â”‚          â”‚ Dependency     â”‚          â”‚ Workflow       â”‚
â”‚ AST/Semgrep  â”‚          â”‚ Engine         â”‚          â”‚ Engine/zizmor  â”‚
â””â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜          â””â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜          â””â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜
       â”‚                           â”‚                           â”‚
       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                   â–¼
                         â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                         â”‚ Artifact +           â”‚
                         â”‚ Provenance Engine    â”‚
                         â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                    â–¼
                         â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                         â”‚ Evidence Graph       â”‚
                         â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                    â–¼
                         â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                         â”‚ Attack-Chain Engine  â”‚
                         â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                    â”‚
                         â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                         â–¼                      â–¼
                â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”      â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                â”‚ Runtime Sandboxâ”‚      â”‚ Threat Intel   â”‚
                â””â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜      â””â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                        â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                   â–¼
                         â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                         â”‚ AI / BARQAI Layer       â”‚
                         â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                    â–¼
                         â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                         â”‚ Policy Engine        â”‚
                         â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                              â”Œâ”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”
                              â–¼           â–¼
                         GitHub Check   Dashboard/API
                              â”‚           â”‚
                              â””â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”˜
                                    â–¼
                           Chrome Extension
```

## 2. Frontend

### Web

Recommended: Next.js/React with TypeScript.

Responsibilities:

- Authentication UX
- Dashboard
- Repository management
- Findings and evidence
- Attack-chain visualization
- Runtime Lab
- Policies
- Billing
- Settings

The web client must not contain service secrets.

### Chrome Extension

Manifest V3.

Responsibilities:

- Detect relevant GitHub pages
- Render security overlays/panels
- Fetch authoritative analysis from backend
- Provide links/actions
- Show Free/Premium status

The extension is not a replacement for the backend analysis engine.

## 3. Backend

### API Service

Recommended: FastAPI.

Responsibilities:

- Authentication/session APIs
- Repository APIs
- Scan orchestration
- Findings APIs
- Billing/entitlements
- Policies
- Notifications

### Worker Service

Background workers execute analysis jobs asynchronously.

Workers must be stateless and horizontally scalable.

## 4. Analysis Engines

### Code Engine

- AST parsing
- Semgrep integration
- Tree-sitter where cross-language parsing is useful
- Regex only for narrowly defined patterns

### Dependency Engine

- Manifest/lockfile parser
- OSV or equivalent vulnerability intelligence
- Malicious package intelligence
- Fuzzy package-name matching
- Dependency graph construction

### Workflow Engine

- GitHub Actions YAML parsing
- zizmor integration where useful
- Custom organization rules

### Artifact Engine

- Package/archive inventory
- Hashes
- Source/artifact file-tree comparison
- Unexpected file detection
- Binary/executable detection

### Provenance Engine

- Attestation parsing
- Source-to-build relationship validation
- Builder/workflow identity
- Artifact digest verification

### Runtime Engine

- Isolated sandbox launcher
- Synthetic credential injection
- Process/file/network/DNS telemetry
- Time/resource limits
- Ephemeral cleanup

## 5. Evidence Graph

Normalize observations from all engines into common entities:

```text
PR
File
Dependency
Workflow
Artifact
Publisher
Commit
Runtime Event
Finding
```

The graph enables correlation such as:

```text
PR
 â†’ modifies manifest
 â†’ adds package
 â†’ package has install hook
 â†’ runtime launches process
 â†’ runtime reads canary credential
 â†’ runtime makes outbound request
```

## 6. AI / BARQAI Layer

Inputs:

- Structured evidence
- Diff summary
- Relevant code snippets
- Rule matches
- Runtime observations
- Dependency metadata
- Provenance data

Outputs:

- Explanation
- Risk-context summary
- Evidence ranking
- Remediation suggestion

The model must not directly access secrets or privileged GitHub write APIs.

## 7. Storage

- PostgreSQL: metadata, findings, policies, users, organizations
- Object storage: large artifacts/telemetry/reports
- Redis/queue: transient jobs and rate limits

## 8. Event Flow

```text
GitHub PR webhook
 â†’ verify signature
 â†’ persist minimal event metadata
 â†’ create scan
 â†’ enqueue analysis job
 â†’ parallel scanners
 â†’ aggregate evidence
 â†’ optional runtime scan
 â†’ BARQAI
 â†’ policy evaluation
 â†’ GitHub Check
 â†’ dashboard/extension update
```

## 9. Deployment

For a hackathon:

```text
Next.js â†’ managed web hosting
FastAPI â†’ container service
Worker â†’ container/background job service
PostgreSQL â†’ managed PostgreSQL
Redis â†’ managed Redis
Object storage â†’ S3/GCS-compatible
```

A container platform such as Cloud Run is a suitable deployment option, but the architecture must remain provider-agnostic.

## 10. Scaling Strategy

- Queue scans asynchronously.
- Run independent detectors in parallel.
- Cache package intelligence.
- Cache repeated commit/artifact hashes.
- Deduplicate scans using repository + commit + analysis profile.
- Apply plan-aware quotas.

## 11. Failure Isolation

If one analyzer fails:

```text
Code Engine âœ“
Dependency Engine âœ“
Workflow Engine âœ—
Runtime Engine pending
BARQAI available with partial evidence
```

The system should report partial analysis rather than pretending the repository is fully scanned.
