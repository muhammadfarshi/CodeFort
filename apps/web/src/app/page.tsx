import Link from "next/link";
import { Shield, AlertTriangle, CheckCircle, Clock } from "lucide-react";
import { MOCK_SCAN_RESULT } from "@/lib/mock-data";
import { SeverityBadge } from "@/components/SeverityBadge";

export default function Dashboard() {
  const scans = [MOCK_SCAN_RESULT]; // Mocked list

  return (
    <div className="space-y-32">
      <header>
        <h1 className="text-2xl font-bold text-text-primary">CodeFort Dashboard</h1>
        <p className="text-text-secondary mt-2">Overview of security scans and findings.</p>
      </header>

      <div className="grid grid-cols-4 gap-16">
        <div className="bg-surface-elevated p-16 rounded-card border border-border">
          <p className="text-sm text-text-secondary font-medium">Total Scans</p>
          <p className="text-3xl font-bold text-text-primary mt-4">1,248</p>
        </div>
        <div className="bg-surface-elevated p-16 rounded-card border border-border">
          <p className="text-sm text-text-secondary font-medium">Active Repos</p>
          <p className="text-3xl font-bold text-text-primary mt-4">42</p>
        </div>
        <div className="bg-surface-elevated p-16 rounded-card border border-border">
          <p className="text-sm text-text-secondary font-medium">Findings Today</p>
          <p className="text-3xl font-bold text-text-primary mt-4">18</p>
        </div>
        <div className="bg-surface-elevated p-16 rounded-card border border-border border-l-4 border-l-severity-critical">
          <p className="text-sm text-text-secondary font-medium">Critical Issues</p>
          <p className="text-3xl font-bold text-severity-critical mt-4">3</p>
        </div>
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-16">Recent Scans</h2>
        <div className="bg-surface-elevated rounded-card border border-border overflow-hidden">
          <table className="w-full text-left text-sm">
            <thead className="bg-surface text-text-secondary border-b border-border">
              <tr>
                <th className="px-16 py-12 font-medium">Repository</th>
                <th className="px-16 py-12 font-medium">PR / Commit</th>
                <th className="px-16 py-12 font-medium">Status</th>
                <th className="px-16 py-12 font-medium">Findings</th>
                <th className="px-16 py-12 font-medium">Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {scans.map((scan) => (
                <tr key={scan.scan_id} className="hover:bg-surface transition-colors">
                  <td className="px-16 py-12">
                    <Link href={`/scans/${scan.scan_id}`} className="font-medium text-brand hover:underline">
                      {scan.repository_full_name}
                    </Link>
                  </td>
                  <td className="px-16 py-12">
                    #{scan.pr_number} <span className="text-text-secondary font-mono ml-2">{scan.head_sha.substring(0,7)}</span>
                  </td>
                  <td className="px-16 py-12">
                    <span className="flex items-center gap-2 text-severity-medium">
                      <Clock className="w-4 h-4" /> Completed
                    </span>
                  </td>
                  <td className="px-16 py-12">
                    <div className="flex gap-2">
                      {scan.severity_summary.critical > 0 && <SeverityBadge severity="critical" count={scan.severity_summary.critical} />}
                      {scan.severity_summary.high > 0 && <SeverityBadge severity="high" count={scan.severity_summary.high} />}
                      {scan.severity_summary.medium > 0 && <SeverityBadge severity="medium" count={scan.severity_summary.medium} />}
                    </div>
                  </td>
                  <td className="px-16 py-12 text-text-secondary">
                    {new Date(scan.completed_at || scan.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {scans.length === 0 && (
            <div className="p-32 text-center text-text-secondary">
              No security findings were detected in recent scans.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
