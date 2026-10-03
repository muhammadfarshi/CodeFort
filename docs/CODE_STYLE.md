# CODE_STYLE.md

# SupplyGuard Coding Standards

## 1. Goals

Code must be:

- Readable
- Explicit
- Typed
- Testable
- Secure by default
- Easy for another developer or AI coding agent to modify safely

## 2. Repository Structure

Recommended monorepo layout:

```text
/apps
  /web                 # Next.js web dashboard
  /extension           # Chrome Extension (Manifest V3)
/services
  /api                 # FastAPI application
  /worker              # Background analysis workers
/packages
  /schemas             # Shared API/event schemas
  /ui                  # Shared design tokens/components where practical
  /security-rules      # Versioned detection rules
/infrastructure
/docs
/tests
```

## 3. Python Standards

- Python with type hints on public functions.
- Prefer small pure functions for parsers and detectors.
- Use `ruff`/formatting equivalent and a type checker such as `mypy` or `pyright`.
- Use Pydantic models for API input/output validation.
- Avoid `Any` unless explicitly justified.
- Never use dynamic shell execution when a library API exists.
- When subprocess execution is required, pass an argument array rather than a shell string.
- Treat repository paths and filenames as untrusted.

Example:

```python
from pathlib import Path


def read_manifest(path: Path) -> str:
    """Read a repository manifest after validating that the path is inside the analysis root."""
    return path.read_text(encoding="utf-8")
```

## 4. TypeScript / React Standards

- TypeScript strict mode.
- No implicit `any`.
- Prefer functional React components.
- Validate API responses at the boundary.
- Keep UI components small and composable.
- Use accessible semantic HTML.
- Never inject unsanitized repository-derived HTML.

## 5. Chrome Extension Standards

- Manifest V3.
- Keep permissions minimal.
- Separate content-script UI from background/service-worker logic.
- Never bundle secrets.
- Never trust DOM text as authoritative security data; use backend API results.
- Handle GitHub DOM changes defensively because GitHub UI can change independently.

## 6. Naming

Python:

```text
snake_case for functions, variables, modules
PascalCase for classes
UPPER_SNAKE_CASE for constants
```

TypeScript:

```text
camelCase for functions/variables
PascalCase for React components/types
UPPER_SNAKE_CASE for constants only when truly constant/config-like
```

Security concepts should use stable vocabulary:

```text
finding
signal
observation
correlation
attack_chain
provenance
runtime_event
policy_result
explanation
```

## 7. Error Handling

- Never silently swallow exceptions.
- Return structured errors from APIs.
- Do not expose stack traces or secrets to end users.
- Log a safe internal error ID and contextual metadata.
- Retry only idempotent or explicitly retry-safe operations.
- Use exponential backoff for external API rate limits.

## 8. Logging

Logs must be structured JSON in production.

Never log:

- access tokens
- private keys
- cookies
- authorization headers
- full secrets
- raw sandbox credentials

Use correlation IDs:

```text
request_id
organization_id
repository_id
scan_id
```

## 9. Security Detector Style

Each detector should expose a stable contract:

```text
input â†’ observations/signals â†’ evidence â†’ finding
```

Detector output should include:

```json
{
  "rule_id": "workflow.untrusted_checkout",
  "severity": "high",
  "confidence": "high",
  "evidence": [],
  "location": {},
  "explanation_key": "workflow.untrusted_checkout"
}
```

Detectors should not directly decide account permissions, billing, or repository access.

## 10. AI Code Rules

- AI-generated code must be reviewed like human-written code.
- Prompts must be versioned.
- Structured model output must be schema-validated.
- Never allow model output to execute automatically.
- AI must not invent evidence.
- Every BARQAI statement should link to an observation or rule when practical.

## 11. Tests

Every new security rule requires:

- Positive test
- Negative test
- Hard-negative test
- Regression test when a production false positive/negative is found

## 12. Documentation

Public behavior changes require corresponding updates to:

- API.md
- PRD.md when product behavior changes
- TRD.md or ARCHITECTURE.md for architectural changes
- TESTING.md when test strategy changes

## 13. Git Practices

Commit messages should be meaningful and scoped.

Recommended:

```text
feat(runtime): add DNS event collector
fix(api): enforce organization resource ownership
feat(BARQAI): add evidence-linked explanations
```

Do not commit generated secrets, local `.env` files, or test artifacts containing sensitive data.
