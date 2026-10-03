"""
CodeFort Dependency Engine — Analyzes package manifests for supply-chain threats.

Detects: typosquatting, known vulnerabilities (OSV.dev), install hooks,
and newly added dependencies.

Detector contract: input → observations → evidence → finding
"""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass

import httpx

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

try:
    import Levenshtein
    _HAS_LEVENSHTEIN = True
except ImportError:
    _HAS_LEVENSHTEIN = False


@dataclass
class FileChange:
    """A changed file in the PR."""
    path: str
    content: str
    patch: str | None = None


# Top popular packages that typosquatters target
_POPULAR_NPM_PACKAGES = [
    "react", "express", "lodash", "axios", "webpack", "typescript", "next",
    "vue", "angular", "moment", "chalk", "debug", "commander", "inquirer",
    "request", "underscore", "bluebird", "async", "uuid", "dotenv",
    "cors", "body-parser", "mongoose", "pg", "redis", "socket.io",
    "jsonwebtoken", "bcrypt", "nodemailer", "passport", "jest", "mocha",
    "eslint", "prettier", "babel", "rollup", "vite", "esbuild",
    "tailwindcss", "postcss", "autoprefixer", "node-fetch", "got", "yargs",
]

_POPULAR_PYPI_PACKAGES = [
    "requests", "flask", "django", "numpy", "pandas", "scipy", "matplotlib",
    "fastapi", "uvicorn", "pydantic", "sqlalchemy", "alembic", "celery",
    "redis", "boto3", "httpx", "aiohttp", "cryptography", "paramiko",
    "pillow", "beautifulsoup4", "scrapy", "selenium", "pytest", "black",
    "ruff", "mypy", "setuptools", "pip", "wheel", "twine", "poetry",
    "click", "typer", "rich", "tqdm", "python-dotenv", "gunicorn",
    "psycopg2", "pymongo", "pyarrow", "tensorflow", "torch", "transformers",
]

_DANGEROUS_HOOKS = {"preinstall", "postinstall", "preuninstall", "install", "prepare"}


class DependencyEngine:
    """
    Analyzes dependency manifests for supply-chain threats.

    Supports: package.json, requirements.txt, pyproject.toml
    """

    def __init__(self) -> None:
        self._osv_client = httpx.AsyncClient(
            base_url="https://api.osv.dev",
            timeout=10.0,
        )

    async def analyze(self, files: list[FileChange]) -> EngineResult:
        """
        Run all dependency detectors on manifest files.

        Args:
            files: List of changed files with path and content.

        Returns:
            EngineResult with dependency findings.
        """
        findings: list[Finding] = []

        for file in files:
            filename = file.path.split("/")[-1].lower()

            if filename == "package.json":
                findings.extend(self._analyze_package_json(file))
            elif filename == "requirements.txt":
                findings.extend(self._analyze_requirements_txt(file))
            elif filename == "pyproject.toml":
                findings.extend(self._analyze_pyproject_toml(file))

        # Run OSV vulnerability checks for detected packages
        packages = self._extract_all_packages(files)
        if packages:
            vuln_findings = await self._check_osv_vulnerabilities(packages)
            findings.extend(vuln_findings)

        return EngineResult(
            engine_name="dependency_engine",
            status=EngineStatus.SUCCESS,
            findings=findings,
        )

    def _analyze_package_json(self, file: FileChange) -> list[Finding]:
        """Analyze a package.json for suspicious dependencies and hooks."""
        findings: list[Finding] = []

        try:
            pkg = json.loads(file.content)
        except json.JSONDecodeError:
            return findings

        # Check for install hooks (scripts section)
        scripts = pkg.get("scripts", {})
        for hook_name in _DANGEROUS_HOOKS:
            if hook_name in scripts:
                script_value = scripts[hook_name]
                findings.append(Finding(
                    finding_id=str(uuid.uuid4()),
                    rule_id="dependency.install_hook@1",
                    severity=Severity.HIGH,
                    confidence=Confidence.HIGH,
                    title=f"Install-time script detected: {hook_name}",
                    description=f"package.json defines a `{hook_name}` script that executes during installation: `{script_value}`",
                    evidence=[Evidence(
                        evidence_id=str(uuid.uuid4()),
                        evidence_type=EvidenceType.OBSERVED,
                        description=f"scripts.{hook_name} = \"{script_value}\"",
                        file_path=file.path,
                        snippet=f'"{hook_name}": "{script_value}"',
                    )],
                    location=Location(file_path=file.path),
                    explanation_key="dependency.install_hook",
                ))

        # Check dependencies for typosquatting
        all_deps: dict[str, str] = {}
        all_deps.update(pkg.get("dependencies", {}))
        all_deps.update(pkg.get("devDependencies", {}))

        for dep_name, dep_version in all_deps.items():
            # New dependency notification
            findings.append(Finding(
                finding_id=str(uuid.uuid4()),
                rule_id="dependency.new_dependency@1",
                severity=Severity.LOW,
                confidence=Confidence.HIGH,
                title=f"New dependency: {dep_name}@{dep_version}",
                description=f"Package `{dep_name}` at version `{dep_version}` was added.",
                evidence=[Evidence(
                    evidence_id=str(uuid.uuid4()),
                    evidence_type=EvidenceType.OBSERVED,
                    description=f"Dependency {dep_name}@{dep_version} found in package.json",
                    file_path=file.path,
                )],
                location=Location(file_path=file.path),
                explanation_key="dependency.new_dependency",
            ))

            # Typosquatting check
            typo_finding = self._check_typosquatting(dep_name, _POPULAR_NPM_PACKAGES, file)
            if typo_finding:
                findings.append(typo_finding)

        return findings

    def _analyze_requirements_txt(self, file: FileChange) -> list[Finding]:
        """Analyze requirements.txt for suspicious packages."""
        findings: list[Finding] = []
        lines = file.content.strip().split("\n")

        for line_num, line in enumerate(lines, start=1):
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue

            # Parse package name (handle ==, >=, ~=, etc.)
            match = re.match(r"^([a-zA-Z0-9_.-]+)", line)
            if not match:
                continue

            pkg_name = match.group(1).lower()

            findings.append(Finding(
                finding_id=str(uuid.uuid4()),
                rule_id="dependency.new_dependency@1",
                severity=Severity.LOW,
                confidence=Confidence.HIGH,
                title=f"New dependency: {pkg_name}",
                description=f"Package `{pkg_name}` was added to requirements.txt",
                evidence=[Evidence(
                    evidence_id=str(uuid.uuid4()),
                    evidence_type=EvidenceType.OBSERVED,
                    description=f"Dependency {line} at line {line_num}",
                    file_path=file.path,
                    line_start=line_num,
                    snippet=line,
                )],
                location=Location(file_path=file.path, line_start=line_num),
                explanation_key="dependency.new_dependency",
            ))

            typo_finding = self._check_typosquatting(pkg_name, _POPULAR_PYPI_PACKAGES, file)
            if typo_finding:
                findings.append(typo_finding)

        return findings

    def _analyze_pyproject_toml(self, file: FileChange) -> list[Finding]:
        """Analyze pyproject.toml for suspicious dependencies."""
        findings: list[Finding] = []
        # Simple regex extraction for [project.dependencies] section
        dep_pattern = re.compile(r'"([a-zA-Z0-9_.-]+)')

        in_deps = False
        for line_num, line in enumerate(file.content.split("\n"), start=1):
            if "[project.dependencies]" in line or "dependencies" in line and "=" in line:
                in_deps = True
                continue
            if in_deps and line.strip().startswith("["):
                in_deps = False
                continue
            if in_deps:
                match = dep_pattern.search(line)
                if match:
                    pkg_name = match.group(1).lower()
                    typo_finding = self._check_typosquatting(pkg_name, _POPULAR_PYPI_PACKAGES, file)
                    if typo_finding:
                        findings.append(typo_finding)

        return findings

    def _check_typosquatting(
        self,
        package_name: str,
        popular_packages: list[str],
        file: FileChange,
    ) -> Finding | None:
        """Check if a package name is suspiciously similar to a popular package."""
        if not _HAS_LEVENSHTEIN:
            return None

        pkg_lower = package_name.lower()

        # Skip if the package IS a popular package
        if pkg_lower in popular_packages:
            return None

        for popular in popular_packages:
            distance = Levenshtein.distance(pkg_lower, popular)
            # Flag if edit distance is 1-2 (very close but not exact)
            if 0 < distance <= 2 and len(pkg_lower) >= 3:
                return Finding(
                    finding_id=str(uuid.uuid4()),
                    rule_id="dependency.typosquat@1",
                    severity=Severity.CRITICAL,
                    confidence=Confidence.HIGH,
                    title=f"Potential typosquatting: '{package_name}' resembles '{popular}'",
                    description=(
                        f"Package `{package_name}` has a Levenshtein distance of {distance} "
                        f"from the popular package `{popular}`. This may be a typosquatting attack."
                    ),
                    evidence=[Evidence(
                        evidence_id=str(uuid.uuid4()),
                        evidence_type=EvidenceType.OBSERVED,
                        description=f"Name similarity: '{package_name}' vs '{popular}' (distance={distance})",
                        file_path=file.path,
                    )],
                    location=Location(file_path=file.path),
                    explanation_key="dependency.typosquat",
                    recommended_action=f"Verify that you intended to install `{package_name}` and not `{popular}`.",
                )

        return None

    async def _check_osv_vulnerabilities(
        self,
        packages: list[tuple[str, str, str]],
    ) -> list[Finding]:
        """
        Query OSV.dev for known vulnerabilities.

        Args:
            packages: List of (name, version, ecosystem) tuples.

        Returns:
            List of findings for packages with known CVEs.
        """
        findings: list[Finding] = []

        for name, version, ecosystem in packages:
            try:
                response = await self._osv_client.post(
                    "/v1/query",
                    json={
                        "package": {"name": name, "ecosystem": ecosystem},
                        "version": version,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    vulns = data.get("vulns", [])
                    for vuln in vulns[:3]:  # Limit to top 3 per package
                        vuln_id = vuln.get("id", "UNKNOWN")
                        summary = vuln.get("summary", "No summary available")
                        severity_str = vuln.get("database_specific", {}).get("severity", "HIGH")

                        findings.append(Finding(
                            finding_id=str(uuid.uuid4()),
                            rule_id="dependency.known_vulnerability@1",
                            severity=Severity.HIGH,
                            confidence=Confidence.HIGH,
                            title=f"Known vulnerability {vuln_id} in {name}@{version}",
                            description=summary,
                            evidence=[Evidence(
                                evidence_id=str(uuid.uuid4()),
                                evidence_type=EvidenceType.OBSERVED,
                                description=f"OSV.dev reports {vuln_id} for {name}@{version}",
                            )],
                            location=Location(file_path=""),
                            explanation_key="dependency.known_vulnerability",
                            recommended_action=f"Update {name} to a patched version.",
                        ))
            except httpx.HTTPError:
                continue  # Graceful degradation on API failure

        return findings

    @staticmethod
    def _extract_all_packages(files: list[FileChange]) -> list[tuple[str, str, str]]:
        """Extract (name, version, ecosystem) from all manifest files."""
        packages: list[tuple[str, str, str]] = []

        for file in files:
            filename = file.path.split("/")[-1].lower()

            if filename == "package.json":
                try:
                    pkg = json.loads(file.content)
                    for name, version in pkg.get("dependencies", {}).items():
                        clean_ver = re.sub(r"[^0-9.]", "", version)
                        if clean_ver:
                            packages.append((name, clean_ver, "npm"))
                except json.JSONDecodeError:
                    pass

            elif filename == "requirements.txt":
                for line in file.content.strip().split("\n"):
                    match = re.match(r"^([a-zA-Z0-9_.-]+)==([0-9.]+)", line.strip())
                    if match:
                        packages.append((match.group(1), match.group(2), "PyPI"))

        return packages
