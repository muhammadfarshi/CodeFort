# 🏰 CodeFort

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![Chrome Extension](https://img.shields.io/badge/Chrome_Extension-MV3-yellow.svg)](https://developer.chrome.com/docs/extensions/mv3/)
[![AI Powered](https://img.shields.io/badge/AI_Engine-BARQAI-indigo.svg)](#barqai-explainable-ai)
[![CI Tests](https://github.com/muhammadfarshi/CodeFort/actions/workflows/python-package.yml/badge.svg)](https://github.com/muhammadfarshi/CodeFort/actions)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Build with confidence.**

*An intelligent software supply-chain security platform for GitHub that stops malicious pull requests, poisoned dependencies, CI/CD workflow exploits, and secret exfiltration before code reaches production.*

[Features](#-key-features) • [Architecture](#-architecture) • [BARQAI](#-barqai-ai-layer) • [Quickstart](#-quickstart) • [Chrome Extension](#-codefort-guard-chrome-extension) • [Documentation](#-documentation)

---

</div>

## 💡 Why CodeFort?

Modern software supply-chain attacks are getting subtler and deadlier:
- **XZ Utils (CVE-2024-3094)**: Sneaking obfuscated test payloads that hijack build-time execution.
- **Event-Stream & SolarWinds**: Poisoned transitive dependencies and install-time execution hooks (`postinstall`).
- **CI/CD "Pwn Requests"**: Exploiting `pull_request_target` workflows to leak repository secrets (`GITHUB_TOKEN`, AWS keys).
- **Typosquatting**: Registering packages named `reqeusts` or `cross-env-js` to hijack unsuspecting imports.

Traditional vulnerability scanners (Dependabot, basic SAST) only check for *already-known CVEs*. **CodeFort inspects behavioral anomalies, capability differentials, and multi-step attack chains in pull requests in real time.**

---

## 🛡️ Key Features

### 1. 🔍 Multi-Engine Deep Inspection
- **Code Engine**:
  - AST-level tracing for dangerous calls (`subprocess.Popen`, `os.system`, `eval()`, `exec()`).
  - High-entropy data & Base64 blob extraction for obfuscated payload detection.
  - Credential & secret access profiling (`os.environ`, `.env`, tokens).
  - Outbound C2 communication detection (hardcoded IPs, socket imports).
- **Dependency Engine**:
  - Levenshtein distance typosquatting detection across npm and PyPI ecosystems.
  - Detection of hazardous install-time lifecycle hooks (`preinstall`, `postinstall`, `prepare`).
  - Real-time vulnerability intelligence queries against [OSV.dev](https://osv.dev).
- **Workflow Engine**:
  - Prevention of **Pwn Requests** (detects `pull_request_target` checking out untrusted PR head refs).
  - Expression injection detection (`${{ github.event.* }}` evaluated inside shell scripts).
  - Overly permissive CI privileges (`permissions: write-all`, `contents: write`).
  - Action integrity verification (unpinned mutable tags vs. commit SHAs).

### 2. ⚡ BARQAI (AI-Powered Analysis)
CodeFort incorporates **BARQAI**, an explainable AI security layer built on Google Gemini:
- **Zero Hallucination Constraint**: Structured prompts ingest verified evidence data only—never raw PR instructions.
- **Tri-Tier Evidence Taxonomy**:
  - 🟢 **Observed**: Facts directly measured from diffs, manifests, and AST nodes.
  - 🟡 **Correlated**: Multiple behavioral signals linked together.
  - 🟣 **Inferred**: Contextual risk assessment and blast-radius interpretation.
- **Graceful Deterministic Fallback**: Operates at 100% capacity with rule-based heuristics if AI keys are not configured.

### 3. ⛓️ Attack-Chain Correlation
Instead of flooding developers with isolated warnings, CodeFort correlates multi-stage attack scenarios:
```
[New Dependency Added] ──> [Install-time Hook Triggers] ──> [System Command Spawns] ──> [Env Secret Harvested] ──> [Exfiltration to External IP]
```
If an entire chain is identified, CodeFort automatically upgrades the incident to **CRITICAL** and issues an immediate **BLOCK** policy decision.

---

## 🏛️ Architecture

```
                       GitHub Pull Request Event
                                  │
                       [HMAC-SHA256 Verification]
                                  │
                     ┌────────────▼────────────┐
                     │   CodeFort FastAPI API  │
                     └────────────┬────────────┘
                                  │
       ┌──────────────────────────┼──────────────────────────┐
       ▼                          ▼                          ▼
  Code Engine             Dependency Engine           Workflow Engine
  (AST & Entropy)         (Typosquat & OSV)           (Pwn & Actions)
       └──────────────────────────┬──────────────────────────┘
                                  │
                                  ▼
                        [Evidence Graph Builder]
                                  │
                                  ▼
                     [Attack-Chain Correlation]
                                  │
                                  ▼
                       [BARQAI Explanation Engine]
                                  │
                                  ▼
                         [Policy Gate Evaluator]
                        (PASS / REVIEW / BLOCK)
                                  │
          ┌───────────────────────┼───────────────────────┐
          ▼                       ▼                       ▼
   GitHub Check Run        Next.js Dashboard       CodeFort Guard (MV3)
   & Annotations           (/scans/:id)            (In-Browser Overlay)
```

---

## 📁 Monorepo Structure

```
codefort/
├── apps/
│   ├── web/                    # Next.js 14 Web Dashboard (Tailwind CSS, React 18)
│   └── extension/              # CodeFort Guard Chrome Extension (Manifest V3)
├── services/
│   ├── api/                    # FastAPI backend orchestrator & security endpoints
│   └── worker/                 # Async scan workers & queue consumers
├── packages/
│   ├── schemas/                # Shared Pydantic (Python) & TypeScript types
│   ├── security-rules/         # Versioned detection rules catalog (YAML)
│   └── ui/                     # Reusable design system tokens & icons
├── docs/                       # Complete engineering specifications
│   ├── PRD.md                  # Product Requirements Document
│   ├── ARCHITECTURE.md         # System Topology & Service Flow
│   ├── SECURITY.md             # Threat Model & Canary Credential Invariants
│   ├── TRD.md                  # Technical Requirements & SLAs
│   ├── AGENTS.md               # Detector Development Contract
│   ├── CODE_STYLE.md           # Engineering Standards & Guidelines
│   └── DESIGN_SYSTEM.md        # UI/UX Specifications & Color Tokens
├── tests/                      # Automated test suite (Pytest + Asyncio)
└── infrastructure/             # Docker Compose configurations
```

---

## 🚀 Quickstart

### Prerequisites
- **Python**: 3.12+
- **Node.js**: 18+ (tested on Node 20 & 24)
- **Git**

### 1. Clone & Set Up Environment

```bash
git clone https://github.com/muhammadfarshi/CodeFort.git
cd CodeFort

# Copy environment template
cp .env.example .env
```

### 2. Run the Backend API

```bash
cd services/api

# Install dependencies
pip install -r requirements.txt
pip install -e ../../packages/schemas/python

# Start the API server
uvicorn app.main:app --reload --port 8000
```
- API will be accessible at: `http://localhost:8000`
- Interactive API Docs (Swagger): `http://localhost:8000/docs`

### 3. Run the Web Dashboard

```bash
cd apps/web

# Install dependencies
npm install

# Start development server
npm run dev
```
- Web Dashboard will be accessible at: `http://localhost:3000`

### 4. Trigger a Demo Security Scan

Test CodeFort's multi-engine analysis against a planted supply-chain attack scenario:
```bash
curl -X POST http://localhost:8000/api/webhooks/demo-scan
```
Open `http://localhost:3000` to inspect the detected findings, correlated attack chains, and BARQAI explanation!

---

## 🧩 CodeFort Guard (Chrome Extension)

CodeFort Guard injects a defensive security HUD directly into GitHub Pull Request pages without altering GitHub's DOM state.

### Build and Load the Extension:
```bash
cd apps/extension

# Install dependencies and compile bundle
npm install
npm run build
```

1. Open Google Chrome and navigate to `chrome://extensions`.
2. Toggle on **Developer mode** (top right corner).
3. Click **Load unpacked**.
4. Select the `apps/extension/dist/` directory.
5. Open any GitHub PR to view real-time security postures!

---

## 🧪 Running Automated Tests

Run the full Python test suite (API endpoints, engines, policies):
```bash
python -m pytest
```

Build verification for frontend:
```bash
cd apps/web && npm run build
cd apps/extension && npm run build
```

---

## 🔒 Security Invariants

1. **Isolation**: Untrusted code from PRs is never evaluated inside the API process.
2. **Canary Credentials**: Built-in synthetic tokens (`CODEFORT_CANARY_*`) detect exfiltration attempts without using real production secrets.
3. **Cryptographic Validation**: Webhook payloads are verified using HMAC-SHA256 signatures before processing.
4. **Non-Alarmist Tone**: Clear, evidence-backed security decisions rather than speculative warnings.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
<b>CodeFort</b> — Defending the open-source supply chain. Built for Hackathons & Production.
</div>
