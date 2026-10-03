# PRD.md

# SupplyGuard â€” Product Requirements Document

## 1. Product Summary

**SupplyGuard** is an intelligent software supply-chain security platform for GitHub. It detects suspicious pull requests, dependency changes, CI/CD workflow risks, artifact drift, provenance anomalies, and runtime behavior before software reaches production.

The product combines a GitHub App, web dashboard, Chrome Extension, static analysis, dependency intelligence, runtime sandboxing, attack-chain correlation, and Explainable AI.

## 2. Problem

Modern software depends on many third-party packages, repositories, build tools, CI/CD workflows, and published artifacts. A malicious change can appear legitimate at the individual-file level but reveal a larger attack chain when dependencies, workflow permissions, publisher identity, release artifacts, and runtime behavior are considered together.

Developers need a security system that answers three questions quickly:

1. **What changed?**
2. **Why is it risky?**
3. **What should I do next?**

## 3. Target Users

### Free / Individual

- Students
- Individual developers
- Open-source maintainers

### Premium / Professional

- Startup development teams
- Security-conscious engineering teams
- Freelance developers managing multiple repositories

### Team / Enterprise

- Software companies
- Platform engineering teams
- Application-security teams
- Organizations with many repositories

## 4. Product Goals

- Detect supply-chain threats before merge where practical.
- Reduce time required to understand a security finding.
- Correlate multiple weak signals into meaningful attack chains.
- Provide evidence-linked BARQAI explanations.
- Safely inspect suspicious packages in an isolated runtime.
- Help users remediate issues.
- Provide continuous post-merge monitoring.
- Make security visible directly inside GitHub.

## 5. Core Features

### A. PR Security Analysis

- Code diff analysis
- Security-sensitive capability detection
- Build/install script analysis
- Suspicious network/process/file behavior patterns

### B. Dependency Intelligence

- Vulnerability intelligence
- Malicious-package intelligence
- Typosquatting detection
- Dependency confusion indicators
- Version/publisher/provenance changes
- Blast-radius analysis

### C. CI/CD Security

- GitHub Actions analysis
- Untrusted checkout detection
- Excessive permissions
- Expression/template injection patterns
- Unpinned action references
- Secret exposure paths

### D. Artifact & Provenance

- Source â†” artifact drift analysis
- Artifact hashes/digests
- Provenance verification
- Publisher/build identity checks
- Unexpected release contents

### E. Runtime Behavior Analysis

Suspicious packages/artifacts can be executed in a controlled sandbox using only synthetic credentials.

Monitor:

- Process execution
- Child processes
- File modifications
- Environment-variable access
- DNS
- Network connections
- Downloads
- Persistence-like behavior

### F. Attack-Chain Correlation

Connect observations into chains such as:

```text
New dependency
 â†’ install hook
 â†’ shell execution
 â†’ environment access
 â†’ network request
```

### G. BARQAI (AI-Powered Analysis)

AI produces human-readable explanations grounded in evidence. Each explanation should separate observed facts from inference and provide relevant file/line references.

### H. AI Remediation

- Suggested fixes
- Dependency upgrade/downgrade suggestions
- Workflow patch suggestions
- Optional draft remediation PR in premium plans

### I. Monitoring

- Supply-Chain Watchtower
- Dependency release monitoring
- Repository security health
- Incident timeline
- Notifications

### J. Policy Builder

Users can configure warn/review/block rules.

## 6. Chrome Extension

The Chrome Extension augments GitHub pages with:

- PR security panel
- Finding indicators
- Dependency hover intelligence
- Runtime-analysis status
- Attack-chain summary
- Link to full web dashboard
- Premium deep-analysis actions

The extension is a presentation and workflow layer; authoritative analysis remains server-side.

## 7. Freemium Model

### FREE

- Basic PR scanning
- Basic dependency checks
- Known vulnerability lookup
- Basic GitHub Actions checks
- Basic BARQAI
- Chrome Extension
- Basic dashboard
- Limited monitoring and analysis quota

### PREMIUM

- Advanced attack-chain correlation
- Runtime Behavior Analysis
- Sandboxed dynamic analysis
- Artifact drift
- Provenance verification
- Dependency blast radius
- Advanced BARQAI
- AI semantic analysis
- AI auto-fix
- Draft remediation PR
- Continuous monitoring
- Threat intelligence correlation
- Security policies
- Incident forensics
- Advanced notifications

### TEAM / ENTERPRISE

- Multiple repositories and organizations
- Central policy management
- RBAC
- Audit logs
- SSO/SCIM where supported
- SIEM/webhook integrations
- Custom retention and enterprise controls

## 8. User Value Proposition

> **Detect. Investigate. Explain. Fix. Monitor.**

SupplyGuard turns scattered supply-chain security signals into an understandable security story directly inside the developer workflow.

## 9. Key User Stories

- As a developer, I want my PR checked before merge so I can catch dangerous changes early.
- As a developer, I want to know exactly why something was flagged.
- As a security engineer, I want connected evidence instead of isolated warnings.
- As a maintainer, I want to know when an existing dependency becomes suspicious after release.
- As a team admin, I want policies that automatically enforce our security requirements.
- As a premium user, I want deeper runtime analysis and remediation assistance.

## 10. Success Metrics

Track:

- PR analyses completed
- High-confidence findings per 1,000 scans
- False-positive rate
- Mean analysis latency
- Runtime-analysis completion rate
- BARQAI explanation usefulness feedback
- Remediation acceptance rate
- Monitored repositories
- Free-to-premium conversion
- 30-day retention

Do not use a single security score as the only quality measure.

## 11. Non-Goals for Initial Release

- Full malware reverse engineering platform
- General-purpose endpoint protection
- Autonomous unrestricted code execution
- Guaranteed detection of every future zero-day
- Replacing all existing SAST/SCA/CI security tools

## 12. MVP Acceptance Criteria

A demo-ready MVP must:

1. Install as a GitHub App.
2. Receive a PR webhook.
3. Fetch changed files and dependency manifests.
4. Run static/security rules.
5. Produce evidence-linked findings.
6. Run basic workflow checks.
7. Post a GitHub Check/comment.
8. Display results in the web dashboard.
9. Show the result in the Chrome Extension.
10. Provide basic BARQAI explanations.
11. Enforce Free/Premium feature entitlements on the server.
