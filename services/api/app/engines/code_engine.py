"""
CodeFort Code Engine — Static analysis of source code changes.

Detects: subprocess calls, eval/exec, obfuscated content, environment variable
access, hardcoded IPs, and suspicious network imports.

Detector contract (CODE_STYLE.md §9): input → observations → evidence → finding
"""

from __future__ import annotations

import ast
import math
import re
import uuid
from dataclasses import dataclass
from typing import Any

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
    """A single changed file in a PR."""
    path: str
    content: str
    patch: str | None = None  # unified diff patch


# Patterns for detection
_SUSPICIOUS_IMPORTS = {
    "subprocess", "os", "socket", "http.client", "urllib",
    "urllib.request", "requests", "httpx", "paramiko", "ftplib",
    "smtplib", "telnetlib", "xmlrpc",
}

_CREDENTIAL_PATTERNS = [
    re.compile(r"os\.environ\[", re.IGNORECASE),
    re.compile(r"os\.environ\.get\(", re.IGNORECASE),
    re.compile(r"os\.getenv\(", re.IGNORECASE),
    re.compile(r"\.env\b"),
    re.compile(r"(SECRET|TOKEN|PASSWORD|API_KEY|PRIVATE_KEY)", re.IGNORECASE),
]

_IP_PATTERN = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"
)

_BASE64_PATTERN = re.compile(
    r"[A-Za-z0-9+/]{40,}={0,2}"
)

_OBFUSCATION_PATTERNS = [
    re.compile(r"\\x[0-9a-fA-F]{2}"),  # hex escapes
    re.compile(r"chr\(\d+\)"),  # chr() obfuscation
    re.compile(r"base64\.b64decode"),
    re.compile(r"codecs\.decode"),
    re.compile(r"exec\s*\("),
    re.compile(r"eval\s*\("),
    re.compile(r"compile\s*\(.*exec"),
]

# Exclude common safe IPs
_SAFE_IPS = {"127.0.0.1", "0.0.0.0", "255.255.255.255", "192.168.", "10.", "172."}


class CodeEngine:
    """
    Analyzes changed source files for security-sensitive patterns.

    Produces findings with evidence of type OBSERVED (directly measured).
    """

    async def analyze(self, files: list[FileChange]) -> EngineResult:
        """
        Run all code analysis detectors on the changed files.

        Args:
            files: List of changed files with path and content.

        Returns:
            EngineResult with findings from all detectors.
        """
        findings: list[Finding] = []

        for file_change in files:
            if not file_change.path.endswith(".py"):
                # For MVP, focus on Python files
                # TODO: Add JS/TS support via tree-sitter
                continue

            try:
                findings.extend(self._analyze_python_file(file_change))
            except SyntaxError:
                # File has syntax errors — skip AST analysis, still run regex
                findings.extend(self._analyze_with_regex(file_change))

        return EngineResult(
            engine_name="code_engine",
            status=EngineStatus.SUCCESS,
            findings=findings,
        )

    def _analyze_python_file(self, file: FileChange) -> list[Finding]:
        """Analyze a Python file using AST + regex detectors."""
        findings: list[Finding] = []
        tree = ast.parse(file.content, filename=file.path)

        findings.extend(self._detect_dangerous_calls(tree, file))
        findings.extend(self._detect_eval_exec(tree, file))
        findings.extend(self._detect_suspicious_imports(tree, file))
        findings.extend(self._analyze_with_regex(file))

        return findings

    def _detect_dangerous_calls(self, tree: ast.AST, file: FileChange) -> list[Finding]:
        """Detect subprocess, os.system, os.popen calls."""
        findings: list[Finding] = []
        dangerous_attrs = {"system", "popen", "exec", "execvp", "execvpe", "spawn"}

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_call_name(node)
                if func_name and (
                    func_name.startswith("subprocess.")
                    or func_name.startswith("os.system")
                    or func_name.startswith("os.popen")
                    or any(attr in func_name for attr in dangerous_attrs)
                ):
                    findings.append(Finding(
                        finding_id=str(uuid.uuid4()),
                        rule_id="code.subprocess_call@1",
                        severity=Severity.HIGH,
                        confidence=Confidence.HIGH,
                        title="Subprocess or system command execution detected",
                        description=f"Call to `{func_name}` detected which can execute arbitrary commands.",
                        evidence=[Evidence(
                            evidence_id=str(uuid.uuid4()),
                            evidence_type=EvidenceType.OBSERVED,
                            description=f"Function call `{func_name}` found at line {node.lineno}",
                            file_path=file.path,
                            line_start=node.lineno,
                            line_end=node.end_lineno,
                            snippet=ast.get_source_segment(file.content, node) or "",
                        )],
                        location=Location(
                            file_path=file.path,
                            line_start=node.lineno,
                            line_end=node.end_lineno,
                        ),
                        explanation_key="code.subprocess_call",
                    ))

        return findings

    def _detect_eval_exec(self, tree: ast.AST, file: FileChange) -> list[Finding]:
        """Detect eval() and exec() usage."""
        findings: list[Finding] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_call_name(node)
                if func_name in ("eval", "exec", "compile"):
                    findings.append(Finding(
                        finding_id=str(uuid.uuid4()),
                        rule_id="code.eval_exec@1",
                        severity=Severity.CRITICAL,
                        confidence=Confidence.HIGH,
                        title="Dynamic code execution via eval/exec",
                        description=f"Use of `{func_name}()` detected which can execute arbitrary code payloads.",
                        evidence=[Evidence(
                            evidence_id=str(uuid.uuid4()),
                            evidence_type=EvidenceType.OBSERVED,
                            description=f"`{func_name}()` call at line {node.lineno}",
                            file_path=file.path,
                            line_start=node.lineno,
                            line_end=node.end_lineno,
                            snippet=ast.get_source_segment(file.content, node) or "",
                        )],
                        location=Location(
                            file_path=file.path,
                            line_start=node.lineno,
                            line_end=node.end_lineno,
                        ),
                        explanation_key="code.eval_exec",
                    ))

        return findings

    def _detect_suspicious_imports(self, tree: ast.AST, file: FileChange) -> list[Finding]:
        """Detect imports of network/system libraries."""
        findings: list[Finding] = []
        seen_modules: set[str] = set()

        for node in ast.walk(tree):
            module_name: str | None = None
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module

            if module_name and module_name in _SUSPICIOUS_IMPORTS and module_name not in seen_modules:
                seen_modules.add(module_name)
                findings.append(Finding(
                    finding_id=str(uuid.uuid4()),
                    rule_id="code.network_import@1",
                    severity=Severity.MEDIUM,
                    confidence=Confidence.MEDIUM,
                    title="Network/system library import detected",
                    description=f"Import of `{module_name}` detected which provides network or system access capabilities.",
                    evidence=[Evidence(
                        evidence_id=str(uuid.uuid4()),
                        evidence_type=EvidenceType.OBSERVED,
                        description=f"Import `{module_name}` at line {node.lineno}",
                        file_path=file.path,
                        line_start=node.lineno,
                        snippet=f"import {module_name}",
                    )],
                    location=Location(file_path=file.path, line_start=node.lineno),
                    explanation_key="code.network_import",
                ))

        return findings

    def _analyze_with_regex(self, file: FileChange) -> list[Finding]:
        """Run regex-based detectors for patterns not easily caught by AST."""
        findings: list[Finding] = []
        lines = file.content.split("\n")

        for line_num, line in enumerate(lines, start=1):
            # Hardcoded IP detection
            for match in _IP_PATTERN.finditer(line):
                ip = match.group()
                if not any(ip.startswith(safe) for safe in _SAFE_IPS):
                    findings.append(Finding(
                        finding_id=str(uuid.uuid4()),
                        rule_id="code.hardcoded_ip@1",
                        severity=Severity.MEDIUM,
                        confidence=Confidence.MEDIUM,
                        title="Hardcoded IP address detected",
                        description=f"Hardcoded IP `{ip}` found which may indicate C2 server communication.",
                        evidence=[Evidence(
                            evidence_id=str(uuid.uuid4()),
                            evidence_type=EvidenceType.OBSERVED,
                            description=f"IP address `{ip}` at line {line_num}",
                            file_path=file.path,
                            line_start=line_num,
                            snippet=line.strip(),
                        )],
                        location=Location(file_path=file.path, line_start=line_num),
                        explanation_key="code.hardcoded_ip",
                    ))

            # Credential/env access patterns
            for pattern in _CREDENTIAL_PATTERNS:
                if pattern.search(line):
                    findings.append(Finding(
                        finding_id=str(uuid.uuid4()),
                        rule_id="code.env_secret_access@1",
                        severity=Severity.HIGH,
                        confidence=Confidence.HIGH,
                        title="Environment variable or secret access",
                        description="Code reads environment variables or references credential-like patterns.",
                        evidence=[Evidence(
                            evidence_id=str(uuid.uuid4()),
                            evidence_type=EvidenceType.OBSERVED,
                            description=f"Credential access pattern at line {line_num}",
                            file_path=file.path,
                            line_start=line_num,
                            snippet=line.strip(),
                        )],
                        location=Location(file_path=file.path, line_start=line_num),
                        explanation_key="code.env_secret_access",
                    ))
                    break  # One finding per line for this rule

        # Obfuscation / high-entropy detection
        entropy = self._shannon_entropy(file.content)
        if entropy > 5.5:  # High entropy threshold
            findings.append(Finding(
                finding_id=str(uuid.uuid4()),
                rule_id="code.obfuscated_content@1",
                severity=Severity.HIGH,
                confidence=Confidence.MEDIUM,
                title="Potentially obfuscated content detected",
                description=f"File has unusually high Shannon entropy ({entropy:.2f}), suggesting obfuscated or encoded content.",
                evidence=[Evidence(
                    evidence_id=str(uuid.uuid4()),
                    evidence_type=EvidenceType.OBSERVED,
                    description=f"Shannon entropy: {entropy:.2f} (threshold: 5.5)",
                    file_path=file.path,
                )],
                location=Location(file_path=file.path),
                explanation_key="code.obfuscated_content",
            ))

        # Base64 blob detection
        for match in _BASE64_PATTERN.finditer(file.content):
            blob = match.group()
            if len(blob) > 60:  # Long base64 strings are suspicious
                line_num = file.content[:match.start()].count("\n") + 1
                findings.append(Finding(
                    finding_id=str(uuid.uuid4()),
                    rule_id="code.obfuscated_content@1",
                    severity=Severity.HIGH,
                    confidence=Confidence.MEDIUM,
                    title="Large base64-encoded blob detected",
                    description="A large base64-encoded string was found which may conceal a malicious payload.",
                    evidence=[Evidence(
                        evidence_id=str(uuid.uuid4()),
                        evidence_type=EvidenceType.OBSERVED,
                        description=f"Base64 blob ({len(blob)} chars) at line {line_num}",
                        file_path=file.path,
                        line_start=line_num,
                        snippet=blob[:80] + "...",
                    )],
                    location=Location(file_path=file.path, line_start=line_num),
                    explanation_key="code.obfuscated_content",
                ))

        return findings

    @staticmethod
    def _shannon_entropy(data: str) -> float:
        """Calculate Shannon entropy of a string."""
        if not data:
            return 0.0
        entropy = 0.0
        for char in set(data):
            p = data.count(char) / len(data)
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy

    @staticmethod
    def _get_call_name(node: ast.Call) -> str | None:
        """Extract the full function name from a Call node."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        if isinstance(node.func, ast.Attribute):
            parts: list[str] = [node.func.attr]
            current: Any = node.func.value
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return ".".join(reversed(parts))
        return None
