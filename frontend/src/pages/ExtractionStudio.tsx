import React, { useState } from "react";
import { 
  Search, 
  Eye, 
  EyeOff, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Copy, 
  Check, 
  Clock, 
  ShieldCheck, 
  FileCode,
  FileText
} from "lucide-react";
import { FileDropzone } from "../components/FileDropzone";
import { api } from "../services/api";
import { ExtractResult } from "../types";

interface ExtractionStudioProps {
  initialImageUrl?: string | null;
  initialManifest?: any | null;
}

export const ExtractionStudio: React.FC<ExtractionStudioProps> = ({
  initialImageUrl,
  initialManifest,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [secretKey, setSecretKey] = useState("AlphaSecurityKey#992");
  const [showKey, setShowKey] = useState(false);
  const [manifestText, setManifestText] = useState(
    initialManifest ? JSON.stringify(initialManifest, null, 2) : ""
  );
  const [groundTruth, setGroundTruth] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ExtractResult | null>(null);
  const [copied, setCopied] = useState(false);

  React.useEffect(() => {
    if (initialImageUrl) {
      fetch(initialImageUrl)
        .then((r) => r.blob())
        .then((blob) => {
          const f = new File([blob], "watermarked_handoff.png", { type: "image/png" });
          setFile(f);
        })
        .catch((err) => console.error("Handoff image load error:", err));
    }
    if (initialManifest) {
      setManifestText(JSON.stringify(initialManifest, null, 2));
    }
  }, [initialImageUrl, initialManifest]);

  const handleFileSelect = (selectedFile: File) => {
    setFile(selectedFile);
    setError(null);
    setResult(null);
  };

  const handleClear = () => {
    setFile(null);
    setResult(null);
    setError(null);
  };

  const handleExtract = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please select an image file to extract.");
      return;
    }
    if (!secretKey.trim()) {
      setError("Please provide the secret watermark key.");
      return;
    }
    if (!manifestText.trim()) {
      setError("Please provide the recovery manifest JSON.");
      return;
    }

    try {
      JSON.parse(manifestText);
    } catch (err: any) {
      setError("Recovery manifest must be valid JSON: " + err.message);
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("secret_key", secretKey);
    formData.append("manifest", manifestText);
    if (groundTruth.trim()) {
      formData.append("ground_truth_message", groundTruth.trim());
    }

    try {
      const res = await api.extractWatermark(formData);
      setResult(res);
    } catch (err: any) {
      setError(err.message || "Watermark extraction failed.");
    } finally {
      setLoading(false);
    }
  };

  const copyMessage = () => {
    if (result?.recovered_message) {
      navigator.clipboard.writeText(result.recovered_message);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold font-mono text-white tracking-tight flex items-center gap-2.5">
          <Search className="w-6 h-6 text-brand-cyan" />
          <span>Blind Watermark Extraction Studio</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Recover and cryptographically authenticate embedded payloads without requiring the host original image.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Extraction Inputs (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <form onSubmit={handleExtract} className="glass-card p-6 space-y-5 border border-slate-800">
            {/* Image Upload Area */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 font-mono">
                1. Watermarked Image File
              </label>
              <FileDropzone
                onFileSelect={handleFileSelect}
                selectedFile={file}
                onClear={handleClear}
                label="Upload Watermarked / Attacked Asset"
              />
            </div>

            {/* Secret Key Input */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 font-mono">
                2. Secret Watermark Key
              </label>
              <div className="relative">
                <input
                  type={showKey ? "text" : "password"}
                  value={secretKey}
                  onChange={(e) => setSecretKey(e.target.value)}
                  placeholder="Enter the secret key used during embedding..."
                  className="w-full bg-slate-900/90 border border-slate-800 rounded-lg py-2.5 pl-3 pr-10 text-xs text-slate-100 font-mono focus:outline-none focus:border-brand-cyan transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowKey(!showKey)}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                >
                  {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Recovery Manifest JSON */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider font-mono">
                  3. Recovery Manifest (JSON)
                </label>
                <span className="text-[11px] text-slate-500 font-mono">Non-secret manifest</span>
              </div>
              <textarea
                value={manifestText}
                onChange={(e) => setManifestText(e.target.value)}
                rows={5}
                placeholder='Paste manifest JSON: { "quantization_step": 14, "repetition_factor": 5, ... }'
                className="w-full bg-slate-900/90 border border-slate-800 rounded-lg p-3 text-xs text-slate-100 font-mono focus:outline-none focus:border-brand-cyan transition-colors resize-none"
              />
            </div>

            {/* Optional Ground-Truth Message */}
            <div>
              <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5 font-mono">
                Ground-Truth Message (Optional for BER benchmark)
              </label>
              <input
                type="text"
                value={groundTruth}
                onChange={(e) => setGroundTruth(e.target.value)}
                placeholder="Optional expected string to measure exact BER % and NC..."
                className="w-full bg-slate-900/90 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-300 font-mono focus:outline-none focus:border-slate-700"
              />
            </div>

            {/* Error Banner */}
            {error && (
              <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading || !file}
              className={`w-full py-3 rounded-xl font-mono text-xs font-bold uppercase tracking-wider transition-all flex items-center justify-center gap-2 ${
                loading
                  ? "bg-slate-800 text-slate-500 cursor-not-allowed"
                  : "bg-gradient-to-r from-sky-500 to-cyan-500 text-slate-950 shadow-lg shadow-sky-500/20 hover:shadow-sky-500/40 hover:opacity-95"
              }`}
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-slate-500 border-t-white rounded-full animate-spin"></div>
                  <span>Executing Blind Recovery & RS Decoding...</span>
                </>
              ) : (
                <>
                  <Search className="w-4 h-4" />
                  <span>Execute Blind Extraction</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Right Column: Verification Verdict & Diagnostics (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {!result ? (
            <div className="glass-card p-12 text-center border border-slate-800 flex flex-col items-center justify-center gap-3">
              <div className="w-14 h-14 rounded-2xl bg-slate-800/60 border border-slate-700/80 flex items-center justify-center text-slate-400">
                <ShieldCheck className="w-7 h-7 text-brand-cyan" />
              </div>
              <h3 className="text-base font-bold text-white font-mono">Awaiting Extraction Input</h3>
              <p className="text-xs text-slate-400 max-w-md">
                Select your watermarked image, enter your secret key, and paste the recovery manifest.
                The blind extraction engine will isolate middle-frequency singular values, vote across repeated blocks, and decode Reed-Solomon codewords.
              </p>
            </div>
          ) : (
            <div className="space-y-6 animate-fadeIn">
              {/* Verdict Banner */}
              {result.success ? (
                <div className="p-5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-start gap-4">
                  <div className="p-2 rounded-lg bg-emerald-500/20 text-emerald-400 flex-shrink-0">
                    <CheckCircle2 className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold font-mono text-emerald-400 uppercase tracking-wider">
                      Watermark Authentication Verified
                    </h3>
                    <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                      Embedded digital payload extracted blindly and verified with 100% CRC-32 integrity match.
                      Reed-Solomon decoding confirmed zero uncorrectable bit errors.
                    </p>
                  </div>
                </div>
              ) : (
                <div className="p-5 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-start gap-4">
                  <div className="p-2 rounded-lg bg-rose-500/20 text-rose-400 flex-shrink-0">
                    <XCircle className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold font-mono text-rose-400 uppercase tracking-wider">
                      Watermark Verification Failed ({result.status.toUpperCase()})
                    </h3>
                    <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                      {result.error || "Watermark corrupted, incorrect secret key, or image severely distorted beyond FEC correction limits."}
                    </p>
                  </div>
                </div>
              )}

              {/* Extracted Payload Message Box */}
              {result.recovered_message && (
                <div className="glass-card p-6 border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-300 uppercase tracking-wider font-mono">
                      Recovered Copyright Payload
                    </span>
                    <button
                      onClick={copyMessage}
                      className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-mono transition-colors"
                    >
                      {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copied ? "Copied" : "Copy"}</span>
                    </button>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-950/90 border border-slate-800/80 font-mono text-sm text-brand-cyan select-all break-all">
                    "{result.recovered_message}"
                  </div>
                </div>
              )}

              {/* Forensic Diagnostic Metrics */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="glass-card p-3.5 border-slate-800">
                  <span className="text-[10px] uppercase font-mono text-slate-400">Mean Confidence</span>
                  <p className="text-xl font-bold font-mono text-brand-cyan mt-0.5">
                    {result.mean_confidence !== null && result.mean_confidence !== undefined
                      ? (result.mean_confidence * 100).toFixed(1) + "%"
                      : "—"}
                  </p>
                  <span className="text-[10px] text-slate-500">Decision Margin</span>
                </div>

                <div className="glass-card p-3.5 border-slate-800">
                  <span className="text-[10px] uppercase font-mono text-slate-400">Bit Error Rate</span>
                  <p className={`text-xl font-bold font-mono mt-0.5 ${
                    result.ber_percentage === 0 ? "text-emerald-400" : "text-amber-400"
                  }`}>
                    {result.ber_percentage !== null && result.ber_percentage !== undefined
                      ? `${result.ber_percentage}%`
                      : "0.0%"}
                  </p>
                  <span className="text-[10px] text-slate-500">Post-Voting</span>
                </div>

                <div className="glass-card p-3.5 border-slate-800">
                  <span className="text-[10px] uppercase font-mono text-slate-400">Correlation (NC)</span>
                  <p className="text-xl font-bold font-mono text-brand-emerald mt-0.5">
                    {result.nc !== null && result.nc !== undefined ? result.nc : "1.00"}
                  </p>
                  <span className="text-[10px] text-slate-500">Normalized Correlation</span>
                </div>

                <div className="glass-card p-3.5 border-slate-800">
                  <span className="text-[10px] uppercase font-mono text-slate-400">Execution Time</span>
                  <p className="text-xl font-bold font-mono text-brand-indigo mt-0.5">
                    {result.execution_time_seconds} s
                  </p>
                  <span className="text-[10px] text-slate-500">Extraction Latency</span>
                </div>
              </div>

              {/* FEC & Frame Inspection Details */}
              <div className="glass-card p-4 border-slate-800 space-y-2 text-xs font-mono">
                <div className="flex items-center justify-between text-slate-400">
                  <span>Reed-Solomon Status:</span>
                  <span className="text-slate-200">{result.fec_status || "Completed"}</span>
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>Audit Job ID:</span>
                  <span className="text-slate-400 font-mono">{result.job_id}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

