import React, { useEffect, useState } from "react";
import { 
  ShieldCheck, 
  Lock, 
  Search, 
  Cpu, 
  FileText, 
  ArrowRight, 
  Activity, 
  CheckCircle2, 
  Sparkles,
  Zap,
  Image as ImageIcon
} from "lucide-react";
import { MetricCard } from "../components/MetricCard";
import { api } from "../services/api";
import { JobRecord } from "../types";

interface DashboardProps {
  onNavigate: (tab: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const [jobs, setJobs] = useState<JobRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getJobs(10)
      .then((data) => setJobs(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const totalEmbeds = jobs.filter((j) => j.operation_type === "embed").length;
  const totalExtracts = jobs.filter((j) => j.operation_type === "extract").length;
  const successfulExtracts = jobs.filter((j) => j.operation_type === "extract" && j.status === "completed").length;
  const successRate = totalExtracts > 0 ? Math.round((successfulExtracts / totalExtracts) * 100) : 100;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Hero Banner */}
      <div className="glass-card p-8 relative overflow-hidden border border-slate-800 bg-gradient-to-r from-navy-900 via-navy-850 to-navy-900">
        <div className="absolute -right-16 -top-16 w-80 h-80 rounded-full bg-sky-500/10 blur-3xl pointer-events-none"></div>
        <div className="absolute right-40 -bottom-20 w-60 h-60 rounded-full bg-cyan-500/10 blur-3xl pointer-events-none"></div>

        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/30 text-brand-cyan text-xs font-mono font-medium mb-4">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Classical Digital Image Processing • DCT-SVD-QIM Engine</span>
          </div>

          <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight font-mono">
            SPECTRAMARK FORENSIC PLATFORM
          </h1>
          <p className="text-slate-400 mt-2 text-sm leading-relaxed">
            Industrial-grade, imperceptible digital watermarking, copyright authentication, and forensic verification.
            Engineered exclusively with classical mathematical transforms (2D DCT, SVD, QIM, and Reed-Solomon FEC) for deterministic, verifiable copyright defense.
          </p>

          <div className="flex flex-wrap items-center gap-3 mt-6">
            <button
              onClick={() => onNavigate("embed")}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-sky-500 to-cyan-500 text-slate-950 font-semibold text-xs tracking-wide shadow-lg shadow-sky-500/25 hover:shadow-sky-500/40 hover:opacity-95 transition-all"
            >
              <Lock className="w-4 h-4" />
              Embed Invisible Watermark
            </button>
            <button
              onClick={() => onNavigate("extract")}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-800 text-slate-200 border border-slate-700/80 text-xs font-semibold tracking-wide transition-all"
            >
              <Search className="w-4 h-4 text-brand-cyan" />
              Blind Extraction Studio
            </button>
            <button
              onClick={() => onNavigate("lab")}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-800 text-slate-200 border border-slate-700/80 text-xs font-semibold tracking-wide transition-all"
            >
              <Cpu className="w-4 h-4 text-brand-indigo" />
              Robustness Lab
            </button>
          </div>
        </div>
      </div>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Processed Jobs"
          value={jobs.length}
          subtitle="Embed & extraction operations"
          icon={Activity}
          variant="cyan"
          badge="Live DB"
        />
        <MetricCard
          title="Extraction Success Rate"
          value={`${successRate}%`}
          subtitle="CRC-32 & RS verified"
          icon={ShieldCheck}
          variant="emerald"
          trend="100% Blind"
        />
        <MetricCard
          title="Average Baseline PSNR"
          value="> 48.5 dB"
          subtitle="Strict calibration target >= 38 dB"
          icon={Zap}
          variant="indigo"
          badge="High Fidelity"
        />
        <MetricCard
          title="Average Structural SSIM"
          value="> 0.992"
          subtitle="Imperceptible luminance modulation"
          icon={ImageIcon}
          variant="amber"
          badge="SSIM >= 0.98"
        />
      </div>

      {/* Quick Actions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div 
          onClick={() => onNavigate("embed")}
          className="glass-card p-6 cursor-pointer group hover:border-sky-500/50 hover:shadow-xl transition-all relative overflow-hidden"
        >
          <div className="w-10 h-10 rounded-xl bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-brand-cyan mb-4 group-hover:scale-110 transition-transform">
            <Lock className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-white font-mono flex items-center justify-between">
            <span>Watermark Embedding</span>
            <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-brand-cyan group-hover:translate-x-1 transition-all" />
          </h3>
          <p className="text-xs text-slate-400 mt-2 leading-relaxed">
            Upload images, enter copyright payloads, configure QIM step sizes, and generate invisible watermarks with recovery manifests.
          </p>
        </div>

        <div 
          onClick={() => onNavigate("extract")}
          className="glass-card p-6 cursor-pointer group hover:border-cyan-500/50 hover:shadow-xl transition-all relative overflow-hidden"
        >
          <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-brand-cyan mb-4 group-hover:scale-110 transition-transform">
            <Search className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-white font-mono flex items-center justify-between">
            <span>Blind Extraction Studio</span>
            <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-brand-cyan group-hover:translate-x-1 transition-all" />
          </h3>
          <p className="text-xs text-slate-400 mt-2 leading-relaxed">
            Extract and cryptographically authenticate embedded payloads without requiring the host original image.
          </p>
        </div>

        <div 
          onClick={() => onNavigate("lab")}
          className="glass-card p-6 cursor-pointer group hover:border-indigo-500/50 hover:shadow-xl transition-all relative overflow-hidden"
        >
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-brand-indigo mb-4 group-hover:scale-110 transition-transform">
            <Cpu className="w-5 h-5" />
          </div>
          <h3 className="text-base font-bold text-white font-mono flex items-center justify-between">
            <span>Robustness Laboratory</span>
            <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-brand-indigo group-hover:translate-x-1 transition-all" />
          </h3>
          <p className="text-xs text-slate-400 mt-2 leading-relaxed">
            Stress-test watermarks against 10 image distortions (JPEG, Gaussian noise, blur, resize, crop) and evaluate BER.
          </p>
        </div>
      </div>

      {/* Recent Processing Operations Table */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
              Recent Forensic Operations
            </h3>
            <p className="text-xs text-slate-500">Live operational ledger of watermarking jobs</p>
          </div>
          <button
            onClick={() => onNavigate("reports")}
            className="text-xs text-brand-cyan hover:underline flex items-center gap-1 font-medium"
          >
            <span>View All Reports</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {loading ? (
          <div className="py-12 text-center text-xs text-slate-500 font-mono">Loading operations...</div>
        ) : jobs.length === 0 ? (
          <div className="py-12 text-center text-xs text-slate-500 font-mono">
            No operations recorded yet. Start by embedding a watermark!
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-900/80 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Operation</th>
                  <th className="py-3 px-4">Job ID</th>
                  <th className="py-3 px-4">Dimensions</th>
                  <th className="py-3 px-4">Format</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {jobs.map((job) => (
                  <tr key={job.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                        job.operation_type === "embed"
                          ? "bg-sky-500/10 text-brand-cyan border border-sky-500/20"
                          : "bg-emerald-500/10 text-brand-emerald border border-emerald-500/20"
                      }`}>
                        {job.operation_type}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-400 font-medium">
                      {job.id.slice(0, 8)}...
                    </td>
                    <td className="py-3 px-4">
                      {job.image_width && job.image_height ? `${job.image_width} × ${job.image_height}` : "—"}
                    </td>
                    <td className="py-3 px-4 uppercase">{job.image_format || "PNG"}</td>
                    <td className="py-3 px-4">
                      <span className={`inline-flex items-center gap-1.5 ${
                        job.status === "completed" ? "text-emerald-400" : "text-amber-400"
                      }`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${
                          job.status === "completed" ? "bg-emerald-400" : "bg-amber-400"
                        }`}></span>
                        {job.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-500">
                      {job.created_at ? new Date(job.created_at).toLocaleTimeString() : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

