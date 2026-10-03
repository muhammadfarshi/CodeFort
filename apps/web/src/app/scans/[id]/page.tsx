import { MOCK_SCAN_RESULT } from "@/lib/mock-data";
import { PolicyBadge } from "@/components/PolicyBadge";
import { ScanProgress } from "@/components/ScanProgress";
import { FindingCard } from "@/components/FindingCard";
import { AttackChainView } from "@/components/AttackChainView";
import { BARQAIPanel } from "@/components/BARQAIPanel";
import { ShieldAlert, GitCommit, GitPullRequest } from "lucide-react";

export default function ScanDetailPage({ params }: { params: { id: string } }) {
  const scan = MOCK_SCAN_RESULT; // Use mock data

  const progressSteps = [
    { name: "Fetching PR", status: "success" as const },
    { name: "Code analysis", status: "success" as const },
    { name: "Dependency analysis", status: "success" as const },
    { name: "Workflow analysis", status: "success" as const },
    { name: "BARQAI", status: "success" as const },
    { name: "Policy", status: "success" as const },
  ];

  const allFindings = scan.engine_results.flatMap(er => er.findings);

  return (
    <div className="space-y-32 max-w-6xl mx-auto pb-32">
      <header className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-3">
            {scan.repository_full_name}
            {scan.policy_result && <PolicyBadge decision={scan.policy_result.decision} />}
          </h1>
          <div className="flex items-center gap-6 mt-4 text-sm text-text-secondary">
            <span className="flex items-center gap-1.5"><GitPullRequest className="w-4 h-4" /> PR #{scan.pr_number}</span>
            <span className="flex items-center gap-1.5"><GitCommit className="w-4 h-4" /> {scan.head_sha.substring(0, 7)}</span>
            <span>{new Date(scan.completed_at || scan.created_at).toLocaleString()}</span>
          </div>
        </div>
      </header>

      <section className="bg-surface-elevated p-24 rounded-card border border-border">
        <h2 className="text-sm font-semibold mb-12 text-text-secondary uppercase tracking-wider">Analysis Progress</h2>
        <ScanProgress steps={progressSteps} />
      </section>

      {scan.attack_chains.length > 0 && (
        <section className="space-y-16">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-severity-critical" /> Correlated Attack Chains
          </h2>
          {scan.attack_chains.map(chain => (
            <AttackChainView key={chain.chain_id} chain={chain} />
          ))}
        </section>
      )}

      {scan.barqai_explanation && (
        <section className="space-y-16">
          <h2 className="text-xl font-semibold">Security Insight</h2>
          <BARQAIPanel explanation={scan.barqai_explanation} />
        </section>
      )}

      <section className="space-y-16">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Security Findings ({allFindings.length})</h2>
          {allFindings.length === 0 && (
            <span className="text-sm text-text-secondary">No security findings were detected in this scan.</span>
          )}
        </div>
        <div className="grid grid-cols-1 gap-16">
          {allFindings.map(finding => (
            <FindingCard key={finding.finding_id} finding={finding} />
          ))}
        </div>
      </section>
      
      {scan.profile === "advanced" && (
        <div className="mt-32 p-16 bg-brand/5 border border-brand/20 rounded-card flex items-center justify-between">
          <div>
            <h4 className="font-semibold text-brand">Deeper analysis available</h4>
            <p className="text-sm text-text-secondary mt-1">Upgrade to Enterprise Policy profile to unlock runtime deep scanning and custom policies.</p>
          </div>
          <button className="px-16 py-8 bg-brand text-white rounded-md text-sm font-medium hover:bg-brand/90 transition-colors">
            View Capabilities
          </button>
        </div>
      )}
    </div>
  );
}
