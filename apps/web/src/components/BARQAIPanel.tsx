import { BARQAIExplanation } from "@/lib/types";
import { Sparkles, CheckCircle2, Link2, Eye } from "lucide-react";

export function BARQAIPanel({ explanation }: { explanation: BARQAIExplanation }) {
  return (
    <div className="bg-gradient-to-b from-[#1e1b4b]/40 to-surface-elevated border border-indigo-500/20 rounded-card overflow-hidden">
      <div className="p-16 border-b border-indigo-500/10 flex items-center gap-2 bg-[#312e81]/20">
        <Sparkles className="w-5 h-5 text-indigo-400" />
        <h3 className="font-semibold text-indigo-100">BARQAI Analysis</h3>
      </div>
      
      <div className="p-24 space-y-24">
        <p className="text-sm leading-relaxed text-text-primary">{explanation.summary}</p>
        
        <div className="grid grid-cols-3 gap-16">
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-text-secondary flex items-center gap-1.5">
              <Eye className="w-4 h-4" /> Observed
            </h4>
            <ul className="space-y-2">
              {explanation.observed.map((obs, i) => (
                <li key={i} className="text-xs text-text-secondary pl-3 border-l-2 border-border">{obs}</li>
              ))}
            </ul>
          </div>
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-text-secondary flex items-center gap-1.5">
              <Link2 className="w-4 h-4" /> Correlated
            </h4>
            <ul className="space-y-2">
              {explanation.correlated.map((cor, i) => (
                <li key={i} className="text-xs text-text-secondary pl-3 border-l-2 border-brand/50">{cor}</li>
              ))}
            </ul>
          </div>
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-text-secondary flex items-center gap-1.5">
              <Sparkles className="w-4 h-4" /> Inferred
            </h4>
            <ul className="space-y-2">
              {explanation.inferred.map((inf, i) => (
                <li key={i} className="text-xs text-text-secondary pl-3 border-l-2 border-indigo-500/50">{inf}</li>
              ))}
            </ul>
          </div>
        </div>

        <div className="mt-24 p-16 bg-surface rounded-md border border-border">
          <h4 className="text-sm font-semibold mb-2 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-500" /> Recommended Action
          </h4>
          <p className="text-sm text-text-secondary">{explanation.recommended_action}</p>
        </div>
        
        <div className="text-center">
          <span className="text-[10px] text-text-secondary/50 uppercase tracking-widest">
            Powered by AI — evidence-grounded analysis
          </span>
        </div>
      </div>
    </div>
  );
}
