import { Check, Loader2, X, Clock } from "lucide-react";

interface Step {
  name: string;
  status: "success" | "running" | "failed" | "queued";
}

export function ScanProgress({ steps }: { steps: Step[] }) {
  return (
    <div className="flex items-center justify-between w-full">
      {steps.map((step, idx) => (
        <div key={idx} className="flex items-center flex-1 last:flex-none">
          <div className="flex flex-col items-center gap-2">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 
              ${step.status === 'success' ? 'bg-brand/10 border-brand text-brand' : 
                step.status === 'running' ? 'bg-brand/10 border-brand text-brand' : 
                step.status === 'failed' ? 'bg-severity-critical/10 border-severity-critical text-severity-critical' : 
                'bg-surface border-border text-text-secondary'}`}>
              {step.status === 'success' && <Check className="w-4 h-4" />}
              {step.status === 'running' && <Loader2 className="w-4 h-4 animate-spin" />}
              {step.status === 'failed' && <X className="w-4 h-4" />}
              {step.status === 'queued' && <Clock className="w-4 h-4" />}
            </div>
            <span className={`text-[12px] font-medium ${step.status === 'queued' ? 'text-text-secondary' : 'text-text-primary'}`}>
              {step.name}
            </span>
          </div>
          {idx < steps.length - 1 && (
            <div className={`flex-1 h-0.5 mx-4 ${step.status === 'success' ? 'bg-brand' : 'bg-border'}`} />
          )}
        </div>
      ))}
    </div>
  );
}
