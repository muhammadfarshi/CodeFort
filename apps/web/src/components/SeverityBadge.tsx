import { Info, Shield, AlertTriangle, AlertOctagon, Skull } from "lucide-react";
import { Severity } from "@/lib/types";

interface Props {
  severity: Severity;
  count?: number;
  showLabel?: boolean;
}

export function SeverityBadge({ severity, count, showLabel = true }: Props) {
  const config = {
    info: { icon: Info, color: "text-severity-info", bg: "bg-severity-info/10", border: "border-severity-info/20", label: "Info" },
    low: { icon: Shield, color: "text-severity-low", bg: "bg-severity-low/10", border: "border-severity-low/20", label: "Low" },
    medium: { icon: AlertTriangle, color: "text-severity-medium", bg: "bg-severity-medium/10", border: "border-severity-medium/20", label: "Medium" },
    high: { icon: AlertOctagon, color: "text-severity-high", bg: "bg-severity-high/10", border: "border-severity-high/20", label: "High" },
    critical: { icon: Skull, color: "text-severity-critical", bg: "bg-severity-critical/10", border: "border-severity-critical/20", label: "Critical" },
  };

  const { icon: Icon, color, bg, border, label } = config[severity];

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${bg} ${border} ${color}`}>
      <Icon className="w-3.5 h-3.5" />
      {showLabel && <span>{label}</span>}
      {count !== undefined && <span className="ml-1 opacity-80">({count})</span>}
    </span>
  );
}
