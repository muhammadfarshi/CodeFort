# TRD.md

# SupplyGuard Technical Requirements Document

## 1. Scope

This document defines how SupplyGuard must behave technically after the product requirements are accepted.

## 2. Functional Requirements

### TR-001 GitHub Integration

The system shall receive GitHub App events and identify repositories and pull requests requiring analysis.

### TR-002 PR Diff Acquisition

The system shall securely fetch changed files and relevant metadata for an authorized repository.

### TR-003 Dependency Parsing

The system shall parse supported dependency manifests and lockfiles.

### TR-004 Static Security Analysis

The system shall identify suspicious changes involving:

- command execution
- environment access
- unexpected network behavior
- encoded/obfuscated content
- install/build scripts
- dangerous workflow patterns
- unexpected binaries/files

### TR-005 Dependency Intelligence

The system shall correlate dependency versions against configured vulnerability and malicious-package intelligence sources.

### TR-006 Security Capability Diff

The system shall compare security-sensitive capabilities before and after the PR.

Example capabilities:

```text
network
shell
process
filesystem
credential/env access
install hooks
binary/native code
workflow privilege
```

### TR-007 Attack-Chain Correlation

The system shall build relationships among findings to identify connected sequences of suspicious behavior.

### TR-008 Artifact Drift

The system shall compare available source trees against release artifacts and report unexpected, modified, or missing files.

### TR-009 Provenance

The system shall record and evaluate available provenance/attestation information.

### TR-010 Runtime Behavior Analysis

The system shall optionally execute eligible artifacts in an isolated sandbox and capture:

- process events
- child processes
- file events
- environment access
- DNS events
- network connections
- downloads
- selected system events

### TR-011 Runtime Safety

Runtime analysis shall:

- use synthetic credentials only
- enforce resource limits
- prevent host access
- use controlled network egress
- destroy the environment after execution

### TR-012 BARQAI

The system shall generate evidence-linked, human-readable explanations.

Every BARQAI output must expose:

```text
observed facts
correlated signals
inferences
relevant evidence
recommended next action
```

### TR-013 AI Prompt-Injection Defense

Repository content must never be treated as trusted instructions to the AI model.

### TR-014 Policy Engine

The system shall support pass/review/block outcomes according to organization policy.

### TR-015 GitHub Feedback

The system shall publish findings to GitHub using supported checks/comments/annotations where available.

### TR-016 Web Dashboard

The system shall expose repository health, PR results, findings, attack chains, provenance, artifacts, runtime reports, policies, and history according to plan entitlements.

### TR-017 Chrome Extension

The extension shall display analysis results on supported GitHub pages and link to detailed web results.

### TR-018 Continuous Monitoring

Premium/team plans shall support monitoring of connected dependencies and relevant repository changes.

### TR-019 Remediation

Premium/team plans may generate suggested patches or draft remediation PRs after explicit user action and authorization.

## 3. Non-Functional Requirements

### Performance

- Basic PR scan target: under 60 seconds for common small/medium PRs excluding queued runtime analysis.
- Initial dashboard response: under 2 seconds for common cached pages.
- Extension panel should render quickly and load analysis asynchronously.

These are targets, not guarantees.

### Availability

- API target suitable for a production SaaS service.
- Workers should tolerate retry and duplicate delivery.

### Security

- TLS for external traffic
- Tenant isolation
- Secure secret storage
- Signed webhook verification
- Sandbox isolation

### Observability

Track:

```text
request latency
queue latency
scan duration
engine failure rate
external API rate limits
runtime sandbox failures
BARQAI latency
false-positive feedback
```

## 4. Analysis Pipeline

```text
Input
 â†“
Normalization
 â†“
Parallel Static Engines
 â†“
Dependency/Workflow Intelligence
 â†“
Artifact/Provenance
 â†“
Evidence Graph
 â†“
Attack-Chain Correlation
 â†“
Optional Runtime Analysis
 â†“
BARQAI
 â†“
Policy
 â†“
GitHub + Web + Extension
```

## 5. Feature Gating

Every protected feature must have a server-side entitlement check.

```text
request
 â†’ authenticated user
 â†’ organization
 â†’ subscription
 â†’ feature entitlement
 â†’ operation
```

## 6. Idempotency

Repeated GitHub webhook delivery must not create duplicate scans for the same event unnecessarily.

Recommended scan key:

```text
organization + repository + PR + head_sha + analysis_profile
```

## 7. Versioning

Version:

- API
- detector rules
- prompts
- analysis profiles
- database schema

Example rule identifier:

```text
workflow.untrusted_checkout@1
```

## 8. Supported Analysis Profiles

```text
basic
advanced
runtime_deep
enterprise_policy
```

Profile determines enabled analyzers and quota cost.

## 9. Data Integrity

Artifact identity must use cryptographic digests such as SHA-256 or stronger supported digest schemes.

Finding evidence must remain immutable once a scan is finalized, with later user state changes represented separately.
ok verification fails
- Real secrets are detected in repository/build artifacts
- Runtime sandbox isolation fails
- BARQAI invents unsupported evidence in tested scenarios
- Premium restrictions can be bypassed through direct API calls
- Database migrations fail from a clean installation
