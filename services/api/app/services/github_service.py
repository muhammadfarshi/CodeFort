"""
CodeFort GitHub Service — Posts analysis results to GitHub.

Uses GitHub App installation tokens (short-lived) for Check Runs
and PR annotations. Falls back to PR comments if Checks API fails.

Security: Uses installation identity only (AGENTS.md §8).
"""

from __future__ import annotations

import logging
from typing import Any

from codefort_schemas.models import (
    Finding,
    PolicyDecision,
    ScanResult,
    Severity,
)

logger = logging.getLogger("codefort.github")


# Map CodeFort severity to GitHub annotation level
_SEVERITY_TO_ANNOTATION: dict[str, str] = {
    "critical": "failure",
    "high": "failure",
    "medium": "warning",
    "low": "notice",
    "info": "notice",
}

# Map PolicyDecision to GitHub Check conclusion
_DECISION_TO_CONCLUSION: dict[str, str] = {
    "pass": "success",
    "review": "neutral",
    "block": "failure",
}


class GitHubService:
    """
    Posts CodeFort analysis results to GitHub via the Checks API.

    Uses PyGithub with installation access tokens.
    """

    def __init__(self) -> None:
        self._github: Any = None

    def _get_github(self, installation_id: int | None = None) -> Any:
        """Get an authenticated GitHub client using App installation token."""
        try:
            from github import Github, GithubIntegration
            from app.core.config import settings

            if not settings.GITHUB_APP_ID or not settings.GITHUB_APP_PRIVATE_KEY_PATH:
                logger.warning("GitHub App credentials not configured")
                return None

            # Read private key
            with open(settings.GITHUB_APP_PRIVATE_KEY_PATH, "r") as f:
                private_key = f.read()

            integration = GithubIntegration(
                integration_id=int(settings.GITHUB_APP_ID),
                private_key=private_key,
            )

            if installation_id:
                access_token = integration.get_access_token(installation_id)
                return Github(access_token.token)

            return None

        except Exception as e:
            logger.warning("GitHub client initialization failed: %s", e)
            return None

    async def post_check_run(
        self,
        result: ScanResult,
        installation_id: int | None = None,
    ) -> bool:
        """
        Post analysis results as a GitHub Check Run with annotations.

        Falls back to a PR comment if the Checks API fails.

        Args:
            result: Complete scan result with findings and policy.
            installation_id: GitHub App installation ID.

        Returns:
            True if the result was posted successfully.
        """
        gh = self._get_github(installation_id)
        if not gh:
            logger.info("GitHub not configured — skipping Check Run post")
            return False

        try:
            repo = gh.get_repo(result.repository_full_name)

            # Determine conclusion from policy
            conclusion = "neutral"
            if result.policy_result:
                conclusion = _DECISION_TO_CONCLUSION.get(
                    result.policy_result.decision.value, "neutral"
                )

            # Build annotations from findings (max 50 per API call)
            annotations = self._build_annotations(result)

            # Build summary
            summary = self._build_summary(result)

            # Create Check Run
            repo.create_check_run(
                name="CodeFort Security Analysis",
                head_sha=result.head_sha,
                status="completed",
                conclusion=conclusion,
                output={
                    "title": f"CodeFort: {result.findings_count} finding(s)",
                    "summary": summary,
                    "annotations": annotations[:50],  # GitHub limits to 50
                },
            )

            logger.info(
                "Posted Check Run for %s PR #%d: %s (%d findings)",
                result.repository_full_name,
                result.pr_number,
                conclusion,
                result.findings_count,
            )
            return True

        except Exception as e:
            logger.warning("Check Run failed, attempting PR comment fallback: %s", e)
            return await self._post_pr_comment(result, gh)

    async def _post_pr_comment(self, result: ScanResult, gh: Any) -> bool:
        """Fallback: post results as a PR comment."""
        try:
            repo = gh.get_repo(result.repository_full_name)
            pr = repo.get_pull(result.pr_number)

            comment_body = self._build_comment_body(result)
            pr.create_issue_comment(comment_body)

            logger.info(
                "Posted PR comment for %s PR #%d",
                result.repository_full_name,
                result.pr_number,
            )
            return True

        except Exception as e:
            logger.error("PR comment fallback also failed: %s", e)
            return False

    @staticmethod
    def _build_annotations(result: ScanResult) -> list[dict]:
        """Build GitHub Check Run annotations from findings."""
        annotations = []

        for engine_result in result.engine_results:
            for finding in engine_result.findings:
                if finding.location and finding.location.file_path:
                    annotations.append({
                        "path": finding.location.file_path,
                        "start_line": finding.location.line_start or 1,
                        "end_line": finding.location.line_end or finding.location.line_start or 1,
                        "annotation_level": _SEVERITY_TO_ANNOTATION.get(
                            finding.severity.value, "notice"
                        ),
                        "title": f"[{finding.rule_id}] {finding.title}",
                        "message": finding.description,
                    })

        return annotations

    @staticmethod
    def _build_summary(result: ScanResult) -> str:
        """Build a markdown summary for the Check Run."""
        lines = [
            "## 🏰 CodeFort Security Analysis",
            "",
            f"**Repository:** {result.repository_full_name}",
            f"**PR:** #{result.pr_number}",
            f"**Commit:** `{result.head_sha[:7]}`",
            f"**Profile:** {result.profile.value}",
            "",
        ]

        # Severity breakdown
        if result.severity_summary:
            lines.append("### Severity Breakdown")
            for sev, count in result.severity_summary.items():
                emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵", "info": "⚪"}.get(sev, "⚪")
                lines.append(f"- {emoji} **{sev.upper()}**: {count}")
            lines.append("")

        # Policy decision
        if result.policy_result:
            decision = result.policy_result.decision.value.upper()
            emoji = {"PASS": "✅", "REVIEW": "⚠️", "BLOCK": "🚫"}.get(decision, "❓")
            lines.append(f"### Decision: {emoji} {decision}")
            for reason in result.policy_result.reasons:
                lines.append(f"- {reason}")
            lines.append("")

        # BARQAI summary
        if result.barqai_explanation:
            lines.append("### Analysis Summary")
            lines.append(result.barqai_explanation.summary)
            if result.barqai_explanation.recommended_action:
                lines.append(f"\n**Recommended:** {result.barqai_explanation.recommended_action}")

        lines.append("\n---\n*🏰 CodeFort — Build with confidence.*")

        return "\n".join(lines)

    @staticmethod
    def _build_comment_body(result: ScanResult) -> str:
        """Build a PR comment body (fallback for Check Run)."""
        lines = [
            "## 🏰 CodeFort Security Analysis",
            "",
            f"Found **{result.findings_count}** security finding(s) in this PR.",
            "",
        ]

        # List top findings
        all_findings: list[Finding] = []
        for er in result.engine_results:
            all_findings.extend(er.findings)

        # Sort by severity (critical first)
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        all_findings.sort(key=lambda f: severity_order.get(f.severity.value, 5))

        for finding in all_findings[:10]:  # Top 10
            sev = finding.severity.value.upper()
            lines.append(f"- **[{sev}]** `{finding.rule_id}` — {finding.title}")

        if len(all_findings) > 10:
            lines.append(f"\n*...and {len(all_findings) - 10} more. See full results in the CodeFort dashboard.*")

        lines.append("\n---\n*🏰 CodeFort — Build with confidence.*")
        return "\n".join(lines)
