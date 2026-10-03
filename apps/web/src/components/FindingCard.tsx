'use client';
import { useState } from "react";
import { Finding } from "@/lib/types";
import { SeverityBadge } from "./SeverityBadge";
import { ChevronDown, ChevronUp, FileCode } from "lucide-react";

export function FindingCard({ finding }: { finding: Finding }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-surface-elevated rounded-card border border-border overflow-hidden">
      <div className="p-16 flex items-start justify-between">
        <div className="space-y-4 flex-1">
          <div className="flex items-center gap-3">
            <SeverityBadge severity={finding.severity} />
            <span className="font-mono text-[12px] text-text-secondary bg-surface px-2 py-1 rounded border border-border">
              {finding.rule_id}
            </span>
          </div>
          <h3 className="text-lg font-semibold text-text-primary">{finding.title}</h3>
          <p className="text-sm text-text-secondary">{finding.description}</p>
          
          {finding.location && (
            <div className="flex items-center gap-2 text-sm text-text-secondary mt-4 bg-surface p-2 rounded-md inline-flex border border-border">
              <FileCode className="w-4 h-4" />
              <span className="font-mono">{finding.location.file_path}</span>
              {finding.location.line_start && <span>:{finding.location.line_start}</span>}
            </div>
          )}
        </div>
        
        {finding.evidence.length > 0 && (
          <button 
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 text-sm text-brand hover:underline px-3 py-1.5 rounded-md bg-brand/10"
          >
            {finding.evidence.length} Evidence
            {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        )}
      </div>

      {finding.recommended_action && (
        <div className="px-16 py-12 bg-brand/5 border-t border-brand/10">
          <p className="text-sm text-text-primary"><span className="font-semibold text-brand">Recommendation:</span> {finding.recommended_action}</p>
        </div>
      )}

      {expanded && finding.evidence.length > 0 && (
        <div className="p-16 bg-surface border-t border-border space-y-4">
          <h4 className="text-sm font-semibold mb-2 text-text-secondary">Evidence Details</h4>
          {finding.evidence.map((ev) => (
            <div key={ev.evidence_id} className="p-12 border border-border rounded-md bg-surface-elevated">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-border text-text-secondary">
                  {ev.evidence_type}
                </span>
                <span className="text-sm font-medium">{ev.description}</span>
              </div>
              {ev.snippet && (
                <pre className="mt-2 p-3 bg-[#0d1117] rounded border border-border overflow-x-auto text-xs font-mono text-gray-300">
                  {ev.snippet}
                </pre>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
