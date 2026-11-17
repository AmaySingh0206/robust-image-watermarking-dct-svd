import React, { useState, useEffect } from "react";
import { 
  Lock, 
  Eye, 
  EyeOff, 
  Download, 
  Cpu, 
  CheckCircle2, 
  AlertCircle, 
  FileJson, 
  FileText, 
  Layers, 
  ArrowRight,
  ShieldAlert
} from "lucide-react";
import { FileDropzone } from "../components/FileDropzone";
import { ImageCompareSlider } from "../components/ImageCompareSlider";
import { api } from "../services/api";
import { EmbedResult, CapacityInfo } from "../types";

interface EmbeddingStudioProps {
  onSendToExtract?: (imgUrl: string, manifest: any) => void;
  onSendToLab?: (imgUrl: string, manifest: any) => void;
}

export const EmbeddingStudio: React.FC<EmbeddingStudioProps> = ({ onSendToExtract, onSendToLab }) => {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [dimensions, setDimensions] = useState<[number, number] | null>(null);

  // Form parameters
  const [message, setMessage] = useState("SPECTRAMARK (C) 2026 Asset ID: SM-77402");
  const [secretKey, setSecretKey] = useState("AlphaSecurityKey#992");
  const [showKey, setShowKey] = useState(false);
  const [strengthProfile, setStrengthProfile] = useState("balanced");
  const [repetitionFactor, setRepetitionFactor] = useState(5);

  // Capacity & execution states
  const [capacity, setCapacity] = useState<CapacityInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<EmbedResult | null>(null);

  // Check capacity whenever file dimensions or repetition changes
  useEffect(() => {
    if (dimensions) {
      api.checkCapacity(dimensions[0], dimensions[1], repetitionFactor)
        .then((data) => setCapacity(data))
        .catch((err) => console.error("Capacity check error:", err));
    } else {
      setCapacity(null);
    }
  }, [dimensions, repetitionFactor]);

  const handleFileSelect = (selectedFile: File, url: string, dims: [number, number]) => {
    setFile(selectedFile);
    setPreviewUrl(url);
    setDimensions(dims);
    setError(null);
    setResult(null);
  };

  const handleClear = () => {
    setFile(null);
    setPreviewUrl(null);
    setDimensions(null);
    setResult(null);
    setError(null);
  };

  const handleEmbed = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please select an image file to embed.");
      return;
    }
    if (!message.trim()) {
      setError("Payload message cannot be empty.");
      return;
    }
    if (!secretKey.trim()) {
      setError("Secret watermark key cannot be empty.");
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("payload", message);
    formData.append("secret_key", secretKey);
    formData.append("strength_profile", strengthProfile);
    formData.append("repetition_factor", repetitionFactor.toString());

    try {
      const res = await api.embedWatermark(formData);
      setResult(res);
    } catch (err: any) {
      setError(err.message || "Watermark embedding failed.");
    } finally {
      setLoading(false);
    }
  };

  const downloadManifest = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result.recovery_manifest, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `recovery_manifest_${result.job_id.slice(0, 8)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const payloadByteCount = new TextEncoder().encode(message).length;

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold font-mono text-white tracking-tight flex items-center gap-2.5">
          <Lock className="w-6 h-6 text-brand-cyan" />
          <span>Watermark Embedding Studio</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Embed blind, cryptographically scheduled invisible watermarks using block-based 2D DCT, SVD, and QIM.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Form & Configuration (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <form onSubmit={handleEmbed} className="glass-card p-6 space-y-5 border border-slate-800">
            {/* Image Upload Area */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 font-mono">
                1. Select Host Image
              </label>
              <FileDropzone
                onFileSelect={handleFileSelect}
                selectedFile={file}
                onClear={handleClear}
                label="Upload Host Asset (PNG, JPEG, WebP)"
              />
            </div>

            {/* Capacity Diagnostic Bar */}
            {capacity && (
              <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs font-mono space-y-2">
                <div className="flex items-center justify-between text-slate-400">
                  <span>Payload Capacity:</span>
                  <span className={capacity.max_payload_bytes >= payloadByteCount ? "text-emerald-400" : "text-rose-400 font-bold"}>
                    {payloadByteCount} / {capacity.max_payload_bytes} bytes
                  </span>
                </div>
                {/* Progress bar */}
                <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className={`h-full transition-all ${
                      capacity.max_payload_bytes >= payloadByteCount ? "bg-brand-cyan" : "bg-rose-500"
                    }`}
                    style={{
                      width: `${Math.min(100, (payloadByteCount / (capacity.max_payload_bytes || 1)) * 100)}%`,
                    }}
                  ></div>
                </div>
                <div className="flex items-center justify-between text-[11px] text-slate-500">
                  <span>Available Blocks: {capacity.total_blocks}</span>
                  <span>Required: {capacity.overhead_blocks + payloadByteCount * 8 * repetitionFactor}</span>
                </div>
              </div>
            )}

            {/* Copyright Ownership Message */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider font-mono">
                  2. Copyright Payload Message
                </label>
                <span className="text-[11px] text-slate-500 font-mono">
                  {payloadByteCount}/219 bytes
                </span>
              </div>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                maxLength={219}
                rows={2}
                placeholder="Enter copyright owner, digital asset ID, or identification string..."
                className="w-full bg-slate-900/90 border border-slate-800 rounded-lg p-3 text-xs text-slate-100 font-mono focus:outline-none focus:border-brand-cyan transition-colors resize-none"
              />
            </div>

            {/* Secret Key Input */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 font-mono">
                3. Secret Watermark Key
              </label>
              <div className="relative">
                <input
                  type={showKey ? "text" : "password"}
                  value={secretKey}
                  onChange={(e) => setSecretKey(e.target.value)}
                  placeholder="Confidential passphrase for HMAC block permutation..."
                  className="w-full bg-slate-900/90 border border-slate-800 rounded-lg py-2.5 pl-3 pr-10 text-xs text-slate-100 font-mono focus:outline-none focus:border-brand-cyan transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowKey(!showKey)}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                >
                  {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              <p className="text-[11px] text-slate-500 mt-1">
                Zero-Knowledge: Secret key is never saved, logged, or included in manifest.
              </p>
            </div>

            {/* Strength Profile & Repetition Factor */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 font-mono">
                  Strength Profile
                </label>
                <select
                  value={strengthProfile}
                  onChange={(e) => setStrengthProfile(e.target.value)}
                  className="w-full bg-slate-900/90 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-100 font-mono focus:outline-none focus:border-brand-cyan"
                >
                  <option value="high_quality">High Quality (Δ=10)</option>
                  <option value="balanced">Balanced (Δ=14)</option>
                  <option value="high_robustness">High Robustness (Δ=22)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 font-mono">
                  Repetition (R)
                </label>
                <select
                  value={repetitionFactor}
                  onChange={(e) => setRepetitionFactor(Number(e.target.value))}
                  className="w-full bg-slate-900/90 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-100 font-mono focus:outline-none focus:border-brand-cyan"
                >
                  <option value={3}>3x (Higher Capacity)</option>
                  <option value={5}>5x (Standard Voting)</option>
                  <option value={7}>7x (Maximum Voting)</option>
                </select>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-start gap-2">
                <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading || !file || (capacity && !capacity.is_feasible)}
              className={`w-full py-3 rounded-xl font-mono text-xs font-bold uppercase tracking-wider transition-all flex items-center justify-center gap-2 ${
                loading
                  ? "bg-slate-800 text-slate-500 cursor-not-allowed"
                  : "bg-gradient-to-r from-sky-500 to-cyan-500 text-slate-950 shadow-lg shadow-sky-500/20 hover:shadow-sky-500/40 hover:opacity-95"
              }`}
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-slate-500 border-t-white rounded-full animate-spin"></div>
                  <span>Computing DCT-SVD-QIM Embedding...</span>
                </>
              ) : (
                <>
                  <Lock className="w-4 h-4" />
                  <span>Execute Watermark Embedding</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Right Column: Interactive Results & Visual Inspection (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {!result ? (
            <div className="glass-card p-12 text-center border border-slate-800 flex flex-col items-center justify-center gap-3">
              <div className="w-14 h-14 rounded-2xl bg-slate-800/60 border border-slate-700/80 flex items-center justify-center text-slate-400">
                <Layers className="w-7 h-7 text-brand-cyan" />
              </div>
              <h3 className="text-base font-bold text-white font-mono">Awaiting Image & Parameters</h3>
              <p className="text-xs text-slate-400 max-w-md">
                Upload your asset on the left and click "Execute Watermark Embedding".
                Real-time PSNR, SSIM, execution latency, and interactive before/after visual sliders will appear here.
              </p>
            </div>
          ) : (
            <div className="space-y-6 animate-fadeIn">
              {/* Performance Metrics Bar */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="glass-card p-3.5 border-slate-800">
                  <span className="text-[10px] uppercase font-mono text-slate-400">PSNR Fidelity</span>
                  <p className="text-xl font-bold font-mono text-emerald-400 mt-0.5">
                    {result.metrics.psnr_db} dB
                  </p>
                  <span className="text-[10px] text-slate-500">Target &gt;= 38 dB</span>
                </div>

                <div className="glass-card p-3.5 border-slate-800">
                  <span className="text-[10px] uppercase font-mono text-slate-400">SSIM Index</span>
                  <p className="text-xl font-bold font-mono text-emerald-400 mt-0.5">
                    {result.metrics.ssim}
                  </p>
                  <span className="text-[10px] text-slate-500">Target &gt;= 0.98</span>
                </div>

                <div className="glass-card p-3.5 border-slate-800">
                  <span className="text-[10px] uppercase font-mono text-slate-400">Processing Latency</span>
                  <p className="text-xl font-bold font-mono text-brand-cyan mt-0.5">
                    {result.metrics.execution_time_seconds} s
                  </p>
                  <span className="text-[10px] text-slate-500">Fast Vectorized</span>
                </div>

                <div className="glass-card p-3.5 border-slate-800">
                  <span className="text-[10px] uppercase font-mono text-slate-400">Block Utilization</span>
                  <p className="text-xl font-bold font-mono text-brand-indigo mt-0.5">
                    {result.metrics.utilization_percentage}%
                  </p>
                  <span className="text-[10px] text-slate-500">
                    {result.metrics.utilized_blocks}/{result.metrics.total_blocks}
                  </span>
                </div>
              </div>

              {/* Before / After Inspection Slider */}
              {previewUrl && (
                <ImageCompareSlider
                  originalUrl={previewUrl}
                  watermarkedUrl={result.watermarked_image_url}
                  originalLabel="Original Host Asset"
                  watermarkedLabel="Watermarked Asset (DCT-SVD-QIM)"
                />
              )}

              {/* Action Buttons: Downloads & Downstream Dispatch */}
              <div className="glass-card p-5 space-y-4 border border-slate-800">
                <h4 className="text-xs font-bold text-slate-200 uppercase tracking-wider font-mono">
                  Export & Forensic Handoff
                </h4>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <a
                    href={result.watermarked_image_url}
                    download={`spectramark_watermarked_${result.job_id.slice(0, 8)}.png`}
                    className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-sky-500/10 hover:bg-sky-500/20 text-brand-cyan border border-sky-500/30 text-xs font-mono font-medium transition-all"
                  >
                    <Download className="w-3.5 h-3.5" />
                    Download PNG
                  </a>

                  <button
                    onClick={downloadManifest}
                    className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-mono font-medium transition-all"
                  >
                    <FileJson className="w-3.5 h-3.5 text-brand-amber" />
                    Save Manifest
                  </button>

                  <a
                    href={`/api/v1/reports/${result.job_id}/download`}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-mono font-medium transition-all"
                  >
                    <FileText className="w-3.5 h-3.5 text-brand-emerald" />
                    Audit PDF
                  </a>
                </div>

                {/* Workflow Hand-off Buttons */}
                <div className="pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3 text-xs">
                  <span className="text-slate-500 font-mono">Downstream testing:</span>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => onSendToExtract && onSendToExtract(result.watermarked_image_url, result.recovery_manifest)}
                      className="px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-300 hover:text-brand-cyan hover:border-slate-700 transition-colors font-mono"
                    >
                      Test in Extraction →
                    </button>
                    <button
                      onClick={() => onSendToLab && onSendToLab(result.watermarked_image_url, result.recovery_manifest)}
                      className="px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-slate-300 hover:text-brand-indigo hover:border-slate-700 transition-colors font-mono"
                    >
                      Stress Test in Lab →
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
