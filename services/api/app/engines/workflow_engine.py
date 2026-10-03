"""
CodeFort Workflow Engine — Analyzes GitHub Actions workflows for CI/CD threats.

Detects: pull_request_target abuse, untrusted checkouts, unpinned actions,
excessive permissions, and expression injection.

Detector contract: input → observations → evidence → finding
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass

import yaml

from codefort_schemas.models import (
    Confidence,
    EngineResult,
    EngineStatus,
    Evidence,
    EvidenceType,
    Finding,
    Location,
    Severity,
)


@dataclass
class FileChange:
    """A changed file in the PR."""
    path: str
    content: str
    patch: str | None = None


# Patterns for detection
_EXPRESSION_INJECTION_PATTERN = re.compile(
    r"\$\{\{\s*github\.event\.(pull_request\.(title|body|head\.ref)|"
    r"issue\.(title|body)|comment\.body|"
    r"review\.body|pages\.\*\.page_name)\s*\}\}"
)

_UNPINNED_ACTION_PATTERN = re.compile(
    r"uses:\s+([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)@(main|master|v\d+|latest)",
)

_SHA_ACTION_PATTERN = re.compile(
    r"uses:\s+[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+@[a-f0-9]{40}",
)

_DANGEROUS_PERMISSIONS = {
    "write-all", "contents: write", "packages: write",
    "actions: write", "security-events: write",
}


class WorkflowEngine:
    """
    Analyzes GitHub Actions workflow YAML files for CI/CD security threats.

    Focuses on trust boundary violations that can lead to credential theft
    or unauthorized code execution.
    """

    async def analyze(self, files: list[FileChange]) -> EngineResult:
        """
        Run workflow security detectors on .github/workflows/*.yml files.

        Args:
            files: List of changed files with path and content.

        Returns:
            EngineResult with workflow findings.
        """
        findings: list[Finding] = []

        for file in files:
            if not self._is_workflow_file(file.path):
                continue

            try:
                workflow = yaml.safe_load(file.content)
                if not isinstance(workflow, dict):
                    continue
            except yaml.YAMLError:
                continue

            findings.extend(self._detect_pull_request_target(workflow, file))
            findings.extend(self._detect_untrusted_checkout(workflow, file))
            findings.extend(self._detect_unpinned_actions(file))
            findings.extend(self._detect_excessive_permissions(workflow, file))
            findings.extend(self._detect_expression_injection(file))

        return EngineResult(
            engine_name="workflow_engine",
            status=EngineStatus.SUCCESS,
            findings=findings,
        )

    @staticmethod
    def _is_workflow_file(path: str) -> bool:
        """Check if a file is a GitHub Actions workflow."""
        normalized = path.replace("\\", "/").lower()
        return (
            ".github/workflows/" in normalized
            and (normalized.endswith(".yml") or normalized.endswith(".yaml"))
        )

    def _detect_pull_request_target(
        self,
        workflow: dict,
        file: FileChange,
    ) -> list[Finding]:
        """Detect usage of the pull_request_target trigger."""
        findings: list[Finding] = []
        triggers = workflow.get("on") if "on" in workflow else workflow.get(True, {})

        if isinstance(triggers, dict) and "pull_request_target" in triggers:
            findings.append(Finding(
                finding_id=str(uuid.uuid4()),
                rule_id="workflow.pull_request_target@1",
                severity=Severity.HIGH,
                confidence=Confidence.HIGH,
                title="pull_request_target trigger detected",
                description=(
                    "This workflow uses `pull_request_target` which runs with base repository "
                    "permissions and has access to repository secrets. An attacker can submit a "
                    "malicious PR that executes code with elevated privileges."
                ),
                evidence=[Evidence(
                    evidence_id=str(uuid.uuid4()),
                    evidence_type=EvidenceType.OBSERVED,
                    description="on: pull_request_target trigger present in workflow",
                    file_path=file.path,
                    snippet="on: pull_request_target",
                )],
                location=Location(file_path=file.path),
                explanation_key="workflow.pull_request_target",
                recommended_action="Use `pull_request` instead unless you specifically need base repo secrets. Never checkout untrusted PR code with this trigger.",
            ))

        elif isinstance(triggers, list) and "pull_request_target" in triggers:
            findings.append(Finding(
                finding_id=str(uuid.uuid4()),
                rule_id="workflow.pull_request_target@1",
                severity=Severity.HIGH,
                confidence=Confidence.HIGH,
                title="pull_request_target trigger detected",
                description="This workflow uses `pull_request_target` which grants elevated privileges.",
                evidence=[Evidence(
                    evidence_id=str(uuid.uuid4()),
                    evidence_type=EvidenceType.OBSERVED,
                    description="pull_request_target in trigger list",
                    file_path=file.path,
                )],
                location=Location(file_path=file.path),
                explanation_key="workflow.pull_request_target",
            ))

        return findings

    def _detect_untrusted_checkout(
        self,
        workflow: dict,
        file: FileChange,
    ) -> list[Finding]:
        """
        Detect checkout of untrusted PR head code combined with pull_request_target.

        This is the critical 'pwn request' pattern.
        """
        findings: list[Finding] = []
        triggers = workflow.get("on") if "on" in workflow else workflow.get(True, {})

        has_prt = (
            (isinstance(triggers, dict) and "pull_request_target" in triggers)
            or (isinstance(triggers, list) and "pull_request_target" in triggers)
        )

        if not has_prt:
            return findings

        jobs = workflow.get("jobs", {})
        for job_name, job in jobs.items():
            if not isinstance(job, dict):
                continue

            steps = job.get("steps", [])
            for step_idx, step in enumerate(steps):
                if not isinstance(step, dict):
                    continue

                uses = step.get("uses", "")
                if "actions/checkout" in uses:
                    with_block = step.get("with", {})
                    ref = with_block.get("ref", "")

                    if "pull_request.head" in str(ref) or "event.pull_request" in str(ref):
                        findings.append(Finding(
                            finding_id=str(uuid.uuid4()),
                            rule_id="workflow.untrusted_checkout@1",
                            severity=Severity.CRITICAL,
                            confidence=Confidence.HIGH,
                            title="Untrusted code checkout with elevated privileges",
                            description=(
                                f"Job `{job_name}` step {step_idx + 1} checks out the PR head code "
                                f"using `pull_request_target`, granting it access to repository secrets. "
                                f"This is a critical 'pwn request' vulnerability."
                            ),
                            evidence=[Evidence(
                                evidence_id=str(uuid.uuid4()),
                                evidence_type=EvidenceType.OBSERVED,
                                description=f"actions/checkout with ref: {ref} under pull_request_target",
                                file_path=file.path,
                                snippet=f"uses: {uses}\nwith:\n  ref: {ref}",
                            )],
                            location=Location(file_path=file.path),
                            explanation_key="workflow.untrusted_checkout",
                            recommended_action="Never checkout and execute untrusted PR code under pull_request_target. Use pull_request trigger instead.",
                        ))

        return findings

    def _detect_unpinned_actions(self, file: FileChange) -> list[Finding]:
        """Detect GitHub Actions references using mutable tags instead of SHA pins."""
        findings: list[Finding] = []
        lines = file.content.split("\n")

        for line_num, line in enumerate(lines, start=1):
            match = _UNPINNED_ACTION_PATTERN.search(line)
            if match and not _SHA_ACTION_PATTERN.search(line):
                action_name = match.group(1)
                tag = match.group(2)

                findings.append(Finding(
                    finding_id=str(uuid.uuid4()),
                    rule_id="workflow.unpinned_action@1",
                    severity=Severity.MEDIUM,
                    confidence=Confidence.HIGH,
                    title=f"Unpinned action: {action_name}@{tag}",
                    description=(
                        f"Action `{action_name}` is referenced with mutable tag `@{tag}` "
                        f"instead of a commit SHA. A compromised action repository could "
                        f"push malicious code to this tag."
                    ),
                    evidence=[Evidence(
                        evidence_id=str(uuid.uuid4()),
                        evidence_type=EvidenceType.OBSERVED,
                        description=f"Unpinned reference: {action_name}@{tag} at line {line_num}",
                        file_path=file.path,
                        line_start=line_num,
                        snippet=line.strip(),
                    )],
                    location=Location(file_path=file.path, line_start=line_num),
                    explanation_key="workflow.unpinned_action",
                    recommended_action=f"Pin `{action_name}` to a specific commit SHA for supply-chain safety.",
                ))

        return findings

    def _detect_excessive_permissions(
        self,
        workflow: dict,
        file: FileChange,
    ) -> list[Finding]:
        """Detect workflows with overly broad permissions."""
        findings: list[Finding] = []

        # Check top-level permissions
        permissions = workflow.get("permissions", {})
        self._check_permissions(permissions, "workflow", file, findings)

        # Check per-job permissions
        jobs = workflow.get("jobs", {})
        for job_name, job in jobs.items():
            if isinstance(job, dict):
                job_perms = job.get("permissions", {})
                self._check_permissions(job_perms, f"jobs.{job_name}", file, findings)

        return findings

    def _check_permissions(
        self,
        permissions: dict | str,
        context: str,
        file: FileChange,
        findings: list[Finding],
    ) -> None:
        """Check a permissions block for overly broad grants."""
        if isinstance(permissions, str) and permissions in ("write-all", "read-all"):
            if permissions == "write-all":
                findings.append(Finding(
                    finding_id=str(uuid.uuid4()),
                    rule_id="workflow.excessive_permissions@1",
                    severity=Severity.HIGH,
                    confidence=Confidence.HIGH,
                    title=f"Excessive permissions: write-all in {context}",
                    description=f"`{context}` grants `write-all` permissions, violating the principle of least privilege.",
                    evidence=[Evidence(
                        evidence_id=str(uuid.uuid4()),
                        evidence_type=EvidenceType.OBSERVED,
                        description=f"permissions: write-all in {context}",
                        file_path=file.path,
                        snippet=f"permissions: {permissions}",
                    )],
                    location=Location(file_path=file.path),
                    explanation_key="workflow.excessive_permissions",
                    recommended_action="Specify only the minimum required permissions.",
                ))

        elif isinstance(permissions, dict):
            for perm_key, perm_value in permissions.items():
                if perm_value == "write" and perm_key in ("contents", "packages", "actions"):
                    findings.append(Finding(
                        finding_id=str(uuid.uuid4()),
                        rule_id="workflow.excessive_permissions@1",
                        severity=Severity.HIGH,
                        confidence=Confidence.HIGH,
                        title=f"Broad write permission: {perm_key}: write",
                        description=f"`{context}` grants `{perm_key}: write` which may be more than needed.",
                        evidence=[Evidence(
                            evidence_id=str(uuid.uuid4()),
                            evidence_type=EvidenceType.OBSERVED,
                            description=f"{perm_key}: write in {context}",
                            file_path=file.path,
                            snippet=f"{perm_key}: {perm_value}",
                        )],
                        location=Location(file_path=file.path),
                        explanation_key="workflow.excessive_permissions",
                    ))

    def _detect_expression_injection(self, file: FileChange) -> list[Finding]:
        """Detect GitHub expression injection in run: steps."""
        findings: list[Finding] = []
        lines = file.content.split("\n")
        in_run_block = False

        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()

            if stripped.startswith("run:"):
                in_run_block = True

            if in_run_block or "run:" in line:
                matches = _EXPRESSION_INJECTION_PATTERN.findall(line)
                if matches or _EXPRESSION_INJECTION_PATTERN.search(line):
                    findings.append(Finding(
                        finding_id=str(uuid.uuid4()),
                        rule_id="workflow.expression_injection@1",
                        severity=Severity.CRITICAL,
                        confidence=Confidence.HIGH,
                        title="Potential expression injection in workflow",
                        description=(
                            "A `run:` step uses `${{ github.event.* }}` which allows an attacker "
                            "to inject arbitrary commands via PR title, body, or comment content."
                        ),
                        evidence=[Evidence(
                            evidence_id=str(uuid.uuid4()),
                            evidence_type=EvidenceType.OBSERVED,
                            description=f"Expression injection pattern at line {line_num}",
                            file_path=file.path,
                            line_start=line_num,
                            snippet=stripped,
                        )],
                        location=Location(file_path=file.path, line_start=line_num),
                        explanation_key="workflow.expression_injection",
                        recommended_action="Store the expression in an environment variable instead of interpolating directly in `run:`.",
                    ))

            if stripped and not stripped.startswith("|") and not stripped.startswith("-"):
                if not stripped.startswith("run:"):
                    in_run_block = False

        return findings
