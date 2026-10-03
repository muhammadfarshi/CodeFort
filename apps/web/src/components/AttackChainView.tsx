import { AttackChain } from "@/lib/types";
import { ArrowDown } from "lucide-react";
import { SeverityBadge } from "./SeverityBadge";

export function AttackChainView({ chain }: { chain: AttackChain }) {
  return (
    <div className="bg-surface-elevated border border-border rounded-card p-24">
      <div className="flex items-center justify-between mb-24">
        <h3 className="text-lg font-semibold flex items-center gap-3">
          {chain.title}
        </h3>
        <SeverityBadge severity={chain.severity} />
      </div>
      
      <div className="relative space-y-4 ml-4">
        <div className="absolute left-6 top-6 bottom-6 w-0.5 bg-border -z-10" />
        
        {chain.nodes.map((node, i) => (
          <div key={i} className="flex items-start gap-16 relative">
            <div className="w-12 h-12 rounded-full bg-surface border-2 border-border flex items-center justify-center font-bold text-text-secondary shadow-sm z-10 shrink-0">
              {node.step}
            </div>
            <div className="bg-surface border border-border rounded-card p-16 flex-1 shadow-sm mt-1">
              <div className="flex items-center justify-between">
                <span className="text-xs uppercase font-bold tracking-wider text-brand mb-1 block">
                  {node.category.replace('_', ' ')}
                </span>
                {node.evidence_ids.length > 0 && (
                  <span className="text-[11px] text-text-secondary font-mono bg-surface-elevated px-2 py-1 rounded">
                    Evidence: {node.evidence_ids.join(', ')}
                  </span>
                )}
              </div>
              <p className="text-sm font-medium text-text-primary mt-2">{node.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
