import React, { useEffect, useState } from "react";
import { 
  FileText, 
  Download, 
  CheckCircle2, 
  Clock, 
  Search, 
  ShieldCheck, 
  ExternalLink,
  Layers,
  Sparkles
} from "lucide-react";
import { api } from "../services/api";
import { JobRecord } from "../types";

export const ReportGenerator: React.FC = () => {
  const [jobs, setJobs] = useState<JobRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedJob, setSelectedJob] = useState<any | null>(null);
  const [jobDetailsLoading, setJobDetailsLoading] = useState(false);

  useEffect(() => {
    api.getJobs(30)
      .then((data) => {
        setJobs(data);
        if (data.length > 0) {
          fetchDetails(data[0].id);
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const fetchDetails = (jobId: string) => {
    setJobDetailsLoading(true);
    api.getJob(jobId)
      .then((data) => setSelectedJob(data))
      .catch((err) => console.error(err))
      .finally(() => setJobDetailsLoading(false));
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold font-mono text-white tracking-tight flex items-center gap-2.5">
          <FileText className="w-6 h-6 text-brand-emerald" />
          <span>Forensic Verification Reports & Audit Ledger</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Generate, preview, and download official cryptographic audit certificates and PDF laboratory reports.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Historical Jobs Table (5 cols) */}
        <div className="lg:col-span-5 glass-card p-5 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800/80">
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">
              Audit Operations Ledger
            </h3>
            <span className="text-[10px] text-slate-500 font-mono">{jobs.length} recorded</span>
          </div>

          {loading ? (
            <div className="py-12 text-center text-xs text-slate-500 font-mono">Loading audit ledger...</div>
          ) : jobs.length === 0 ? (
            <div className="py-12 text-center text-xs text-slate-500 font-mono">
              No audit records available yet.
            </div>
          ) : (
            <div className="space-y-2 max-h-[560px] overflow-y-auto pr-1">
              {jobs.map((j) => {
                const active = selectedJob?.id === j.id;
                return (
                  <div
                    key={j.id}
                    onClick={() => fetchDetails(j.id)}
                    className={`p-3.5 rounded-xl border text-xs font-mono cursor-pointer transition-all ${
                      active
                        ? "bg-sky-500/10 border-sky-500/50 shadow-md shadow-sky-500/10"
                        : "bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                        j.operation_type === "embed"
                          ? "bg-sky-500/10 text-brand-cyan border border-sky-500/20"
                          : "bg-emerald-500/10 text-brand-emerald border border-emerald-500/20"
                      }`}>
                        {j.operation_type}
                      </span>
                      <span className="text-slate-500 text-[10px]">
                        {j.created_at ? new Date(j.created_at).toLocaleTimeString() : ""}
                      </span>
                    </div>

                    <div className="mt-2 flex items-center justify-between text-slate-300">
                      <span className="font-semibold">{j.id.slice(0, 12)}...</span>
                      <span className="text-[11px] text-slate-500">
                        {j.image_width && j.image_height ? `${j.image_width}x${j.image_height}` : ""}
                      </span>
                    </div>

                    {j.metrics && (
                      <div className="mt-2 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-400">
                        <span>PSNR: {j.metrics.psnr_db ? `${j.metrics.psnr_db} dB` : "—"}</span>
                        <span>SSIM: {j.metrics.ssim || "—"}</span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right Column: Report Metadata Preview & PDF Download (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {!selectedJob ? (
            <div className="glass-card p-12 text-center border border-slate-800 flex flex-col items-center justify-center gap-3">
              <div className="w-14 h-14 rounded-2xl bg-slate-800/60 border border-slate-700/80 flex items-center justify-center text-slate-400">
                <FileText className="w-7 h-7 text-brand-emerald" />
              </div>
              <h3 className="text-base font-bold text-white font-mono">Select an Audit Record</h3>
              <p className="text-xs text-slate-400 max-w-md">
                Click on any operation in the audit ledger on the left to preview its forensic parameters and download the full official PDF report.
              </p>
            </div>
          ) : jobDetailsLoading ? (
            <div className="glass-card p-12 text-center border border-slate-800 font-mono text-xs text-slate-500">
              Loading report metadata...
            </div>
          ) : (
            <div className="glass-card p-6 border-slate-800 space-y-6 animate-fadeIn">
              {/* Header Card */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800/80 gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-white font-mono uppercase tracking-wider">
                      Audit Certificate #{selectedJob.id.slice(0, 8).toUpperCase()}
                    </span>
                    <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 text-[10px] font-mono border border-emerald-500/20">
                      VERIFIED
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 font-mono mt-1">
                    Job ID: {selectedJob.id}
                  </p>
                </div>

                <a
                  href={`/api/v1/reports/${selectedJob.id}/download`}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 text-xs font-mono font-bold shadow-lg shadow-emerald-500/20 hover:shadow-emerald-500/40 transition-all"
                >
                  <Download className="w-4 h-4" />
                  <span>Download Forensic PDF</span>
                </a>
              </div>

              {/* Asset & Technical Details */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 font-mono text-xs">
                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
                  <span className="text-[10px] uppercase text-slate-500">Asset Dimensions</span>
                  <p className="text-slate-200 font-bold">
                    {selectedJob.image_width} × {selectedJob.image_height} px
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
                  <span className="text-[10px] uppercase text-slate-500">Image Format</span>
                  <p className="text-slate-200 font-bold uppercase">{selectedJob.image_format || "PNG"}</p>
                </div>

                <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 space-y-1">
                  <span className="text-[10px] uppercase text-slate-500">Algorithm Engine</span>
                  <p className="text-brand-cyan font-bold">{selectedJob.algorithm_version || "DCT-SVD-QIM"}</p>
                </div>
              </div>

              {/* Baseline Metrics Summary */}
              {selectedJob.metrics && (
                <div className="space-y-3">
                  <h4 className="text-xs font-bold text-slate-300 font-mono uppercase tracking-wider">
                    Baseline Fidelity Metrics
                  </h4>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs">
                    <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                      <span className="text-[10px] text-slate-500">PSNR Fidelity</span>
                      <p className="text-base font-bold text-emerald-400 mt-0.5">
                        {selectedJob.metrics.psnr_db ? `${selectedJob.metrics.psnr_db} dB` : "—"}
                      </p>
                    </div>

                    <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                      <span className="text-[10px] text-slate-500">Structural SSIM</span>
                      <p className="text-base font-bold text-emerald-400 mt-0.5">
                        {selectedJob.metrics.ssim || "—"}
                      </p>
                    </div>

                    <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                      <span className="text-[10px] text-slate-500">Latency</span>
                      <p className="text-base font-bold text-brand-cyan mt-0.5">
                        {selectedJob.metrics.execution_time_seconds ? `${selectedJob.metrics.execution_time_seconds}s` : "—"}
                      </p>
                    </div>

                    <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                      <span className="text-[10px] text-slate-500">Block Utilization</span>
                      <p className="text-base font-bold text-brand-indigo mt-0.5">
                        {selectedJob.metrics.utilization_percentage ? `${selectedJob.metrics.utilization_percentage}%` : "—"}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Experiments Table if present */}
              {selectedJob.experiments && selectedJob.experiments.length > 0 && (
                <div className="space-y-3">
                  <h4 className="text-xs font-bold text-slate-300 font-mono uppercase tracking-wider">
                    Robustness Attack Evaluations ({selectedJob.experiments.length})
                  </h4>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs font-mono">
                      <thead className="bg-slate-900/80 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
                        <tr>
                          <th className="py-2.5 px-3">Attack</th>
                          <th className="py-2.5 px-3">Attacked PSNR</th>
                          <th className="py-2.5 px-3">SSIM</th>
                          <th className="py-2.5 px-3">BER (%)</th>
                          <th className="py-2.5 px-3">Verdict</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800/60 text-slate-300 text-[11px]">
                        {selectedJob.experiments.map((exp: any) => (
                          <tr key={exp.id}>
                            <td className="py-2 px-3 font-semibold text-slate-200">{exp.attack_name}</td>
                            <td className="py-2 px-3">{exp.psnr} dB</td>
                            <td className="py-2 px-3">{exp.ssim}</td>
                            <td className="py-2 px-3">{exp.ber !== null ? `${exp.ber}%` : "—"}</td>
                            <td className="py-2 px-3">
                              <span className={exp.extraction_status === "success" ? "text-emerald-400" : "text-rose-400"}>
                                {exp.extraction_status.toUpperCase()}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Recovery Manifest JSON Viewer */}
              {selectedJob.recovery_manifest && (
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-slate-300 font-mono uppercase tracking-wider">
                    Recovery Manifest
                  </h4>
                  <pre className="p-4 rounded-xl bg-slate-950/90 border border-slate-800 text-[11px] font-mono text-slate-300 overflow-x-auto max-h-48">
                    {JSON.stringify(selectedJob.recovery_manifest, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

