import React from "react";
import { LucideIcon } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  badge?: string;
  trend?: string;
  variant?: "cyan" | "emerald" | "amber" | "indigo" | "rose";
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  badge,
  trend,
  variant = "cyan",
}) => {
  const variantStyles = {
    cyan: "border-sky-500/20 text-brand-cyan bg-sky-500/10",
    emerald: "border-emerald-500/20 text-brand-emerald bg-emerald-500/10",
    amber: "border-amber-500/20 text-brand-amber bg-amber-500/10",
    indigo: "border-indigo-500/20 text-brand-indigo bg-indigo-500/10",
    rose: "border-rose-500/20 text-brand-rose bg-rose-500/10",
  };

  return (
    <div className="glass-card p-5 relative overflow-hidden group hover:border-slate-700 transition-all">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-slate-400 tracking-wide uppercase">{title}</p>
          <h3 className="text-2xl font-bold font-mono text-white mt-1.5 tracking-tight">{value}</h3>
          {subtitle && <p className="text-[11px] text-slate-400 mt-1">{subtitle}</p>}
        </div>
        <div className={`p-2.5 rounded-xl border ${variantStyles[variant]}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      {(badge || trend) && (
        <div className="mt-3 flex items-center gap-2 pt-2 border-t border-slate-800/60 text-[11px]">
          {badge && (
            <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono font-medium">
              {badge}
            </span>
          )}
          {trend && <span className="text-emerald-400 font-medium">{trend}</span>}
        </div>
      )}
    </div>
  );
};

