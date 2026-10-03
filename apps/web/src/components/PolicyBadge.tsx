import { PolicyDecision } from "@/lib/types";
import { CheckCircle2, AlertCircle, XOctagon } from "lucide-react";

export function PolicyBadge({ decision }: { decision: PolicyDecision }) {
  const config = {
    pass: { icon: CheckCircle2, color: "text-emerald-500", bg: "bg-emerald-500/10", border: "border-emerald-500/20", label: "PASS" },
    review: { icon: AlertCircle, color: "text-severity-medium", bg: "bg-severity-medium/10", border: "border-severity-medium/20", label: "REVIEW" },
    block: { icon: XOctagon, color: "text-severity-critical", bg: "bg-severity-critical/10", border: "border-severity-critical/20", label: "BLOCK" },
  };

  const { icon: Icon, color, bg, border, label } = config[decision];

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-md border font-semibold text-sm ${bg} ${border} ${color}`}>
      <Icon className="w-4 h-4" />
      {label}
    </div>
  );
}
