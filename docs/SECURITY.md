# SECURITY.md

# SupplyGuard Security Specification

## 1. Purpose

SupplyGuard is a software supply-chain security platform that analyzes GitHub pull requests, dependencies, CI/CD workflows, release artifacts, provenance, and selected runtime behavior before risky changes reach production.

The platform consists of:

- Web application and dashboard
- GitHub App and webhook integration
- Chrome Extension for GitHub-native visibility
- Security analysis API and orchestrator
- Static analyzers and threat-intelligence integrations
- Sandboxed Runtime Behavior Analysis
- BARQAI (AI-Powered Analysis) and remediation services

## 2. Security Principles

1. **Least privilege**: every service, GitHub permission, database role, and API token gets only the minimum required access.
2. **Untrusted-by-default**: PR code, package contents, issue text, comments, README content, and workflow files are untrusted input.
3. **Evidence before inference**: security decisions must be grounded in observable evidence; AI explanations must distinguish observed behavior from inference.
4. **Never execute untrusted code in the application process**: dynamic analysis must run in a dedicated isolated sandbox.
5. **Never expose real secrets to analyzed code**: runtime tests use synthetic canary credentials only.
6. **Defense in depth**: no single detector, LLM, heuristic, or reputation signal can be the sole basis for a critical decision.
7. **Tenant isolation**: one organization must never be able to access another organization's repositories, scans, findings, logs, or billing data.
8. **Auditable decisions**: every block/review decision must reference the underlying evidence and policy rule.

## 3. Threat Model

### Assets

- GitHub App credentials and installation tokens
- User sessions and OAuth tokens
- Repository metadata and source-code snippets
- Security findings and evidence
- Package and artifact metadata
- Organization policies
- Billing and entitlement data
- Audit logs

### Threats

- Malicious pull requests
- Dependency poisoning, typosquatting, and dependency confusion
- Malicious install/build scripts
- GitHub Actions trust-boundary abuse
- Credential exfiltration attempts
- Prompt injection against the AI reviewer
- Compromised package publishers or maintainers
- Artifact/source drift
- Webhook replay or forgery
- Cross-tenant data access
- Abuse of the runtime sandbox
- API scraping, rate-limit exhaustion, and denial-of-service
- Malicious extension pages or browser-side token theft

## 4. Authentication and Authorization

### Website

- Prefer GitHub OAuth/OIDC for developer sign-in.
- Establish an application session using secure, HTTP-only, SameSite cookies.
- Never store OAuth access tokens in localStorage.
- Support organization membership and role-based access control.

### GitHub App

- Use GitHub App private-key signing only on the server side.
- Generate short-lived installation access tokens when needed.
- Request only required repository permissions.
- Verify every webhook using the GitHub App webhook secret/signature.
- Store installation IDs and repository IDs; do not persist long-lived installation tokens.

### Chrome Extension

- The extension must not receive the GitHub App private key.
- Do not embed backend master API keys in the extension bundle.
- Use an authenticated browser session or a short-lived extension token obtained through the website.
- Minimize host permissions and restrict content-script execution to GitHub domains needed for the product.
- Sanitize all server-provided HTML before injecting UI into GitHub.

## 5. Sensitive Data and Secrets

Never commit:

- GitHub App private keys
- Webhook secrets
- OAuth client secrets
- Database credentials
- LLM provider API keys
- Payment-provider secrets
- Runtime sandbox credentials
- Production encryption keys

Use environment variables or a managed secret manager. Rotate secrets immediately when exposed.

Runtime Behavior Analysis must use canary values such as:

```text
CANARY_GITHUB_TOKEN=SUPPLYGUARD_CANARY_GH
CANARY_AWS_KEY=SUPPLYGUARD_CANARY_AWS
CANARY_NPM_TOKEN=SUPPLYGUARD_CANARY_NPM
```

These values must never map to real credentials.

## 6. Code and Input Security

All external input is untrusted, including:

- PR titles and bodies
- Commit messages
- Issue comments
- README content
- Source files
- Workflow YAML
- Package manifests
- Registry metadata
- AI-generated text

Use strict schema validation, output encoding, path canonicalization, command allowlists, and safe subprocess handling.

Never build shell commands by string concatenation from repository content.

## 7. Runtime Sandbox Requirements

Runtime analysis must run outside the API application process.

Minimum controls:

- Ephemeral sandbox per analysis
- Non-root execution
- Read-only base image where possible
- CPU, memory, process-count, and execution-time limits
- Temporary filesystem
- No host filesystem access
- No Docker socket access
- No cloud metadata service access
- Controlled network egress
- DNS telemetry
- Process/file/network event capture
- Synthetic credentials only
- Automatic sandbox destruction after completion

A sandbox event is evidence, not proof of malicious intent by itself. Findings should include context and confidence.

## 8. AI / BARQAI Security

The LLM is an analysis and explanation component, not an authority with access to secrets or privileged tools.

Rules:

- Treat repository content as **data, never instructions**.
- Provide structured evidence to the model rather than unrestricted repository text where possible.
- Require strict JSON output validated against a schema.
- Never give the model write access to repositories or credentials by default.
- Do not let model output directly execute shell commands.
- Separate observed evidence from inferred intent.
- Record model version/configuration used for a decision.
- Never claim data theft unless evidence actually establishes it; use language such as â€œpotential credential exfiltration behaviorâ€ when appropriate.

## 9. API Security

- HTTPS everywhere outside local development.
- Short request timeouts and payload-size limits.
- Authentication on all private endpoints.
- Organization-level authorization on every resource query.
- Idempotency for webhook and scan-start operations.
- Rate limiting per user, organization, IP, extension client, and GitHub installation.
- Structured audit logging for security-sensitive actions.

## 10. Data Retention

Default recommendation:

- Raw webhook payloads: short retention, then delete or minimize.
- Source-code snippets: retain only the minimum needed for findings; support configurable retention.
- Runtime event logs: configurable retention; shorter for free users.
- Findings and policy decisions: longer retention for auditability.
- Billing records: retain according to legal/accounting requirements.

## 11. Free/Premium Entitlement Security

Feature access must be enforced on the backend, not only in the UI.

Example premium-only controls:

- Deep Runtime Behavior Analysis
- Full artifact/provenance analysis
- Advanced attack-chain correlation
- AI auto-fix and draft PR generation
- Continuous monitoring
- Custom policy enforcement
- Advanced incident forensics

The extension and website may hide unavailable controls, but the API must independently enforce subscription entitlements.

## 12. Auditability

Record:

- Authentication and authorization events
- GitHub installation/uninstallation
- Repository connection changes
- Scan start/completion/failure
- Policy changes
- Premium entitlement changes
- AI model/configuration used for a finding
- Remediation actions
- Security-setting changes

## 13. Secure Development Rules

- Dependency pinning for production builds where practical
- Dependency review on every release
- Static analysis and unit tests in CI
- Secret scanning in CI
- Container image scanning
- SBOM generation for releases
- Signed/provenance-aware release process where supported

## 14. Incident Response

Security incidents involving SupplyGuard itself must have a documented procedure covering:

1. Detection and triage
2. Containment
3. Credential rotation
4. Customer impact assessment
5. Evidence preservation
6. Remediation
7. Customer communication
8. Post-incident review

## 15. Security Decision Language

Use these terms consistently:

- **Observed**: directly measured or extracted from code/config/runtime telemetry.
- **Correlated**: multiple observed signals connected by the platform.
- **Inferred**: interpretation derived from evidence.
- **Potential**: plausible harmful behavior without conclusive proof.
- **Confirmed**: strong evidence establishes the condition according to a defined rule.

Avoid sensational or absolute language unless the evidence supports it.
