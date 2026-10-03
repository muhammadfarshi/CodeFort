from codefort_schemas.models import PolicyResult, PolicyDecision, Finding, Severity

class PolicyEngine:
    def evaluate(self, findings: list[Finding]) -> PolicyResult:
        decision = PolicyDecision.PASS
        reasons = ["No high or critical findings"]
        triggered = []
        for f in findings:
            if f.severity == Severity.CRITICAL:
                decision = PolicyDecision.BLOCK
                reasons.append("Critical finding detected")
                triggered.append(f.rule_id)
            elif f.severity == Severity.HIGH and decision != PolicyDecision.BLOCK:
                decision = PolicyDecision.REVIEW
                reasons.append("High finding detected")
                triggered.append(f.rule_id)
        return PolicyResult(decision=decision, reasons=reasons, triggered_rules=triggered)
