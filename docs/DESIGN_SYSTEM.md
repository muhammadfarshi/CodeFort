# DESIGN_SYSTEM.md

# SupplyGuard Design System

## 1. Design Goal

SupplyGuard should feel like a professional developer-security tool: calm, precise, technical, and trustworthy.

Do not use visual alarmism for every warning. Reserve strong warning treatment for high-severity findings.

## 2. Color Roles

Use semantic tokens rather than hard-coded colors in components.

```text
Background
Surface
Surface Elevated
Text Primary
Text Secondary
Border
Brand
Success
Info
Warning
Danger
Critical
Focus
```

Recommended semantic direction:

- Success: green family
- Info: blue family
- Warning: amber family
- Danger: orange/red family
- Critical: deep red family

Exact values should be defined centrally in theme tokens and tested for WCAG AA contrast.

## 3. Typography

Recommended font stack:

```text
Inter, ui-sans-serif, system-ui, sans-serif
```

Use a monospaced font for:

- code
- file paths
- hashes
- rule IDs
- command/config snippets

Type scale:

```text
Display: 32-40px
H1: 28-32px
H2: 22-24px
H3: 18-20px
Body: 14-16px
Small: 12-13px
Mono: 12-14px
```

## 4. Spacing

Use an 8px base scale:

```text
4px  8px  12px  16px  24px  32px  40px  48px  64px
```

Avoid arbitrary one-off spacing values.

## 5. Radius and Elevation

- Small controls: 6-8px radius
- Cards: 10-14px radius
- Modals: 12-16px radius
- Use subtle shadows only for elevation; security dashboards should remain information-dense and readable.

## 6. Security Severity UI

```text
INFO      neutral/informational
LOW       subtle warning
MEDIUM    warning
HIGH      danger
CRITICAL  critical
```

Every severity indicator must also have text; do not rely on color alone.

## 7. Core Components

### Security Status Card

Shows:

```text
status
severity
confidence
short explanation
primary action
```

### Finding Card

Shows:

```text
category
rule ID
summary
evidence count
file/line location
severity
confidence
recommended action
```

### Attack Chain

Graph/vertical flow:

```text
Dependency
   â†“
Install Hook
   â†“
Process Execution
   â†“
Credential Access
   â†“
Network Request
```

### Evidence Panel

Must distinguish:

```text
Observed
Correlated
Inferred
```

### Runtime Timeline

Show ordered events with timestamps:

```text
Process â†’ Environment â†’ DNS â†’ Network â†’ File
```

### Provenance Card

Show:

```text
Source
Commit
Builder
Workflow
Artifact Digest
Verification
```

## 8. Chrome Extension UI

Extension panel width target: 320-380px.

Use progressive disclosure:

```text
Summary
 â†“
Why flagged?
 â†“
Evidence
 â†“
Attack chain
 â†“
Deep runtime details
```

Do not overwhelm the GitHub page.

## 9. Premium UX

Premium features should be framed as deeper analysis rather than hiding basic security truth.

Good:

> â€œDeep Runtime Analysis is available in Premium.â€

Avoid:

> â€œYour project is unsafe. Pay to see why.â€

## 10. Accessibility

- Keyboard navigation
- Visible focus states
- WCAG AA contrast target
- Reduced-motion support
- Screen-reader labels
- Status conveyed using icon + text, not color alone

## 11. Empty States

Use helpful states:

```text
No findings

No security findings were detected in this scan.
```

Do not say â€œ100% Safeâ€.

## 12. Loading States

Use staged progress for longer scans:

```text
Fetching PR
âœ“

Code analysis
âœ“

Dependency analysis
âœ“

Workflow analysis
...

Runtime analysis
Queued
```

## 13. Copy Guidelines

Prefer:

- â€œPotential credential exfiltration behaviorâ€
- â€œObserved outbound network requestâ€
- â€œProvenance unavailableâ€
- â€œSource/artifact mismatch detectedâ€

Avoid unsupported claims such as:

- â€œHacker detectedâ€
- â€œDefinitely maliciousâ€
- â€œYour account has been compromisedâ€

unless deterministic evidence actually establishes those claims.
