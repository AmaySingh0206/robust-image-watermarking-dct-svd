import React, { useState } from "react";
import { 
  Cpu, 
  Play, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  Sliders, 
  BarChart2, 
  Zap, 
  History,
  TrendingDown,
  Layers
} from "lucide-react";
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  Cell,
  Legend
} from "recharts";
import { FileDropzone } from "../components/FileDropzone";
import { api } from "../services/api";
import { AttackResult } from "../types";

interface RobustnessLabProps {
  initialImageUrl?: string | null;
  initialManifest?: any | null;
}

export const RobustnessLab: React.FC<RobustnessLabProps> = ({
  initialImageUrl,
  initialManifest,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(initialImageUrl || null);
  const [secretKey, setSecretKey] = useState("AlphaSecurityKey#992");
  const [manifestText, setManifestText] = useState(
    initialManifest
      ? JSON.stringify(initialManifest, null, 2)
      : JSON.stringify({
          quantization_step: 14.0,
          repetition_factor: 5,
          codeword_bits_count: 528,
          total_embedded_bits: 2640,
          parity_bytes: 32
        }, null, 2)
  );
  const [groundTruth, setGroundTruth] = useState("SPECTRAMARK (C) 2026 Asset ID: SM-77402");

  React.useEffect(() => {
    if (initialImageUrl) {
      setPreviewUrl(initialImageUrl);
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

  // Attack selection & parameters
  const [selectedAttack, setSelectedAttack] = useState("jpeg");
  const [jpegQuality, setJpegQuality] = useState(85);
  const [noiseStd, setNoiseStd] = useState(5.0);
  const [saltPepperDensity, setSaltPepperDensity] = useState(0.01);
  const [blurRadius, setBlurRadius] = useState(0.3);
  const [medianKernel, setMedianKernel] = useState(3);
  const [resizeFactor, setResizeFactor] = useState(0.75);
  const [cropPercentage, setCropPercentage] = useState(10.0);
  const [rotationAngle, setRotationAngle] = useState(1.0);
  const [brightnessFactor, setBrightnessFactor] = useState(1.1);
  const [contrastFactor, setContrastFactor] = useState(1.1);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentResult, setCurrentResult] = useState<AttackResult | null>(null);
  const [history, setHistory] = useState<AttackResult[]>([]);

  const handleFileSelect = (selectedFile: File, url: string) => {
    setFile(selectedFile);
    setPreviewUrl(url);
    setError(null);
  };

  const getAttackParams = (): Record<string, any> => {
    switch (selectedAttack) {
      case "jpeg":
        return { quality: jpegQuality };
      case "gaussian_noise":
        return { std_dev: noiseStd };
      case "salt_and_pepper":
        return { density: saltPepperDensity };
      case "gaussian_blur":
        return { radius: blurRadius };
      case "median_filter":
        return { size: medianKernel };
      case "resizing":
        return { scale_factor: resizeFactor, restore_dimensions: true };
      case "cropping":
        return { crop_percentage: cropPercentage, zero_fill: true };
      case "rotation":
        return { angle_degrees: rotationAngle, counter_rotate: true };
      case "brightness":
        return { factor: brightnessFactor };
      case "contrast":
        return { factor: contrastFactor };
      default:
        return {};
    }
  };

  const handleRunAttack = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please upload a watermarked image to test.");
      return;
    }
    if (!secretKey.trim()) {
      setError("Secret key is required for blind extraction verification.");
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

    const params = getAttackParams();
    const formData = new FormData();
    formData.append("file", file);
    formData.append("attack_name", selectedAttack);
    formData.append("parameters", JSON.stringify(params));
    formData.append("secret_key", secretKey);
    formData.append("manifest", manifestText);
    if (groundTruth.trim()) {
      formData.append("ground_truth_message", groundTruth.trim());
    }

    try {
      const res = await api.runAttack(formData);
      setCurrentResult(res);
      setHistory((prev) => [res, ...prev.slice(0, 9)]);
    } catch (err: any) {
      setError(err.message || "Attack test failed.");
    } finally {
      setLoading(false);
    }
  };

  const attacksList = [
    { id: "jpeg", name: "JPEG Compression", desc: "Quantization loss" },
    { id: "gaussian_noise", name: "Gaussian Noise", desc: "Additive noise" },
    { id: "salt_and_pepper", name: "Salt & Pepper", desc: "Impulse noise" },
    { id: "gaussian_blur", name: "Gaussian Blur", desc: "Low-pass spatial filter" },
    { id: "median_filter", name: "Median Filter", desc: "Non-linear filter" },
    { id: "resizing", name: "Image Resizing", desc: "Downscale & resample" },
    { id: "cropping", name: "Border Cropping", desc: "Center crop & pad" },
    { id: "rotation", name: "Rotation", desc: "Geometric rotation" },
    { id: "brightness", name: "Brightness", desc: "Photometric shift" },
    { id: "contrast", name: "Contrast", desc: "Dynamic range scaling" },
  ];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold font-mono text-white tracking-tight flex items-center gap-2.5">
          <Cpu className="w-6 h-6 text-brand-indigo" />
          <span>Robustness Testing Laboratory</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Apply real-world image processing distortions, measure physical degradation, and test blind watermark recovery resilience.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Attack Setup & Controls (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <form onSubmit={handleRunAttack} className="glass-card p-6 space-y-5 border border-slate-800">
            {/* Upload Area */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 font-mono">
                1. Watermarked Test Asset
              </label>
              <FileDropzone
                onFileSelect={handleFileSelect}
                selectedFile={file}
                onClear={() => { setFile(null); setPreviewUrl(null); }}
                label="Upload Watermarked Asset"
              />
            </div>

            {/* Attack Selector */}
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 font-mono">
                2. Select Distortion Attack
              </label>
              <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto pr-1">
                {attacksList.map((att) => (
                  <button
                    key={att.id}
                    type="button"
                    onClick={() => setSelectedAttack(att.id)}
                    className={`p-2.5 rounded-lg text-left border text-xs transition-all ${
                      selectedAttack === att.id
                        ? "bg-indigo-600/20 border-indigo-500 text-white font-medium"
                        : "bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700"
                    }`}
                  >
                    <div className="font-mono text-xs font-semibold truncate">{att.name}</div>
                    <div className="text-[10px] text-slate-500 truncate">{att.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Dynamic Attack Parameter Sliders */}
            <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-4">
              <div className="flex items-center justify-between text-xs font-mono text-slate-300">
                <span className="flex items-center gap-1.5 font-semibold">
                  <Sliders className="w-3.5 h-3.5 text-brand-indigo" />
                  Parameter Configuration
                </span>
                <span className="text-brand-indigo font-bold">
                  {selectedAttack === "jpeg" && `Quality: ${jpegQuality}`}
                  {selectedAttack === "gaussian_noise" && `σ: ${noiseStd}`}
                  {selectedAttack === "salt_and_pepper" && `Density: ${saltPepperDensity}`}
                  {selectedAttack === "gaussian_blur" && `Radius: ${blurRadius}px`}
                  {selectedAttack === "median_filter" && `Kernel: ${medianKernel}x${medianKernel}`}
                  {selectedAttack === "resizing" && `Scale: ${Math.round(resizeFactor * 100)}%`}
                  {selectedAttack === "cropping" && `Border Crop: ${cropPercentage}%`}
                  {selectedAttack === "rotation" && `Angle: ${rotationAngle}°`}
                  {selectedAttack === "brightness" && `Factor: ${brightnessFactor}x`}
                  {selectedAttack === "contrast" && `Factor: ${contrastFactor}x`}
                </span>
              </div>

              {selectedAttack === "jpeg" && (
                <div>
                  <input
                    type="range"
                    min="30"
                    max="95"
                    step="5"
                    value={jpegQuality}
                    onChange={(e) => setJpegQuality(Number(e.target.value))}
                    className="w-full accent-indigo-500"
                  />
                  <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-1">
                    <span>Q=30 (Aggressive)</span>
                    <span>Q=75 (Standard)</span>
                    <span>Q=95 (Lossless-like)</span>
                  </div>
                </div>
              )}

              {selectedAttack === "gaussian_noise" && (
                <div>
                  <input
                    type="range"
                    min="1"
                    max="25"
                    step="1"
                    value={noiseStd}
                    onChange={(e) => setNoiseStd(Number(e.target.value))}
                    className="w-full accent-indigo-500"
                  />
                  <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-1">
                    <span>σ=1 (Subtle)</span>
                    <span>σ=10 (Moderate)</span>
                    <span>σ=25 (Severe)</span>
                  </div>
                </div>
              )}

              {selectedAttack === "gaussian_blur" && (
                <div>
                  <input
                    type="range"
                    min="0.1"
                    max="1.5"
                    step="0.05"
                    value={blurRadius}
                    onChange={(e) => setBlurRadius(Number(e.target.value))}
                    className="w-full accent-indigo-500"
                  />
                  <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-1">
                    <span>0.1px (Mild)</span>
                    <span>0.5px (Moderate)</span>
                    <span>1.5px (Heavy)</span>
                  </div>
                </div>
              )}

              {selectedAttack === "resizing" && (
                <div>
                  <input
                    type="range"
                    min="0.5"
                    max="1.5"
                    step="0.05"
                    value={resizeFactor}
                    onChange={(e) => setResizeFactor(Number(e.target.value))}
                    className="w-full accent-indigo-500"
                  />
                  <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-1">
                    <span>50% (Downscale)</span>
                    <span>100%</span>
                    <span>150% (Upscale)</span>
                  </div>
                </div>
              )}

              {selectedAttack === "brightness" && (
                <div>
                  <input
                    type="range"
                    min="0.7"
                    max="1.4"
                    step="0.05"
                    value={brightnessFactor}
                    onChange={(e) => setBrightnessFactor(Number(e.target.value))}
                    className="w-full accent-indigo-500"
                  />
                  <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-1">
                    <span>0.7x (Darker)</span>
                    <span>1.0x (Original)</span>
                    <span>1.4x (Brighter)</span>
                  </div>
                </div>
              )}

              {selectedAttack === "contrast" && (
                <div>
                  <input
                    type="range"
                    min="0.7"
                    max="1.4"
                    step="0.05"
                    value={contrastFactor}
                    onChange={(e) => setContrastFactor(Number(e.target.value))}
                    className="w-full accent-indigo-500"
                  />
                  <div className="flex justify-between text-[10px] font-mono text-slate-500 mt-1">
                    <span>0.7x (Lower)</span>
                    <span>1.0x (Original)</span>
                    <span>1.4x (Higher)</span>
                  </div>
                </div>
              )}
            </div>

            {/* Secret Key & Manifest Inputs */}
            <div className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1 font-mono">
                  Secret Key
                </label>
                <input
                  type="text"
                  value={secretKey}
                  onChange={(e) => setSecretKey(e.target.value)}
                  className="w-full bg-slate-900/90 border border-slate-800 rounded-lg p-2 text-xs text-slate-200 font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1 font-mono">
                  Recovery Manifest (JSON)
                </label>
                <textarea
                  value={manifestText}
                  onChange={(e) => setManifestText(e.target.value)}
                  rows={3}
                  className="w-full bg-slate-900/90 border border-slate-800 rounded-lg p-2 text-xs text-slate-300 font-mono resize-none"
                />
              </div>
            </div>

            {error && (
              <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !file}
              className={`w-full py-3 rounded-xl font-mono text-xs font-bold uppercase tracking-wider transition-all flex items-center justify-center gap-2 ${
                loading
                  ? "bg-slate-800 text-slate-500 cursor-not-allowed"
                  : "bg-gradient-to-r from-indigo-500 to-sky-500 text-white shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/40 hover:opacity-95"
              }`}
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-slate-500 border-t-white rounded-full animate-spin"></div>
                  <span>Simulating Attack & Verifying Extraction...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  <span>Execute Attack & Verify Robustness</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Right Column: Visual Inspection & Robustness Analytics (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {!currentResult ? (
            <div className="glass-card p-12 text-center border border-slate-800 flex flex-col items-center justify-center gap-3">
              <div className="w-14 h-14 rounded-2xl bg-slate-800/60 border border-slate-700/80 flex items-center justify-center text-slate-400">
                <Layers className="w-7 h-7 text-brand-indigo" />
              </div>
              <h3 className="text-base font-bold text-white font-mono">Awaiting Attack Experiment</h3>
              <p className="text-xs text-slate-400 max-w-md">
                Select a distortion method, adjust strength parameters on the left, and launch the experiment.
                Degraded images, extraction verdicts, and BER error rates will appear here.
              </p>
            </div>
          ) : (
            <div className="space-y-6 animate-fadeIn">
              {/* Verdict Header */}
              <div className={`p-4 rounded-xl border flex items-center justify-between ${
                currentResult.extraction_success
                  ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                  : "bg-rose-500/10 border-rose-500/30 text-rose-400"
              }`}>
                <div className="flex items-center gap-3">
                  {currentResult.extraction_success ? (
                    <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
                  ) : (
                    <XCircle className="w-5 h-5 flex-shrink-0" />
                  )}
                  <div>
                    <h4 className="text-xs font-bold font-mono uppercase tracking-wider">
                      Attack Result: {currentResult.attack_name.toUpperCase()} (
                      {currentResult.extraction_success ? "SURVIVED" : "CORRUPTED"})
                    </h4>
                    <p className="text-[11px] text-slate-300 mt-0.5">
                      {currentResult.extraction_success
                        ? `Watermark survived ${currentResult.attack_name} distortion with payload intact!`
                        : "Distortion exceeded error correction threshold. Watermark corruption detected."}
                    </p>
                  </div>
                </div>

                <span className="text-xs font-mono font-bold px-2.5 py-1 rounded bg-slate-900 border border-slate-800">
                  {currentResult.extraction_status.toUpperCase()}
                </span>
              </div>

              {/* Side-by-Side Images (Watermarked Host vs Attacked) */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="glass-card p-3 space-y-2">
                  <div className="flex items-center justify-between text-xs font-mono text-slate-400">
                    <span>Input Asset</span>
                    <span className="text-[10px] text-slate-500">Pristine Watermark</span>
                  </div>
                  <div className="aspect-video rounded-lg overflow-hidden bg-slate-950/80 border border-slate-800">
                    {previewUrl && <img src={previewUrl} alt="Watermarked" className="w-full h-full object-contain" />}
                  </div>
                </div>

                <div className="glass-card p-3 space-y-2">
                  <div className="flex items-center justify-between text-xs font-mono text-brand-indigo">
                    <span>Attacked Asset</span>
                    <span className="text-[10px] text-brand-indigo/80">Distorted Output</span>
                  </div>
                  <div className="aspect-video rounded-lg overflow-hidden bg-slate-950/80 border border-slate-800">
                    <img src={currentResult.attacked_image_url} alt="Attacked" className="w-full h-full object-contain" />
                  </div>
                </div>
              </div>

              {/* Forensic Metrics Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="glass-card p-3.5 border-slate-800">
                  <span className="text-[10px] uppercase font-mono text-slate-400">Attacked PSNR</span>
                  <p className="text-xl font-bold font-mono text-brand-cyan mt-0.5">
                    {currentResult.psnr_db} dB
                  </p>
                  <span className="text-[10px] text-slate-500">Image Fidelity</span>
                </div>

                <div className="glass-card p-3.5 border-slate-800">
                  <span className="text-[10px] uppercase font-mono text-slate-400">Attacked SSIM</span>
                  <p className="text-xl font-bold font-mono text-brand-cyan mt-0.5">
                    {currentResult.ssim}
                  </p>
                  <span className="text-[10px] text-slate-500">Structural Sim</span>
                </div>

                <div className="glass-card p-3.5 border-slate-800">
                  <span className="text-[10px] uppercase font-mono text-slate-400">Bit Error (BER)</span>
                  <p className={`text-xl font-bold font-mono mt-0.5 ${
                    currentResult.ber_percentage === 0 ? "text-emerald-400" : "text-amber-400"
                  }`}>
                    {currentResult.ber_percentage !== null && currentResult.ber_percentage !== undefined
                      ? `${currentResult.ber_percentage}%`
                      : "—"}
                  </p>
                  <span className="text-[10px] text-slate-500">Post-Voting BER</span>
                </div>

                <div className="glass-card p-3.5 border-slate-800">
                  <span className="text-[10px] uppercase font-mono text-slate-400">Correlation (NC)</span>
                  <p className="text-xl font-bold font-mono text-brand-emerald mt-0.5">
                    {currentResult.nc !== null && currentResult.nc !== undefined
                      ? currentResult.nc
                      : "1.00"}
                  </p>
                  <span className="text-[10px] text-slate-500">Normalized Corr</span>
                </div>
              </div>

              {/* Extracted Payload if available */}
              {currentResult.recovered_message && (
                <div className="p-3.5 rounded-xl bg-slate-900/90 border border-slate-800 font-mono text-xs flex items-center justify-between">
                  <span className="text-slate-400">Recovered Payload:</span>
                  <span className="text-brand-cyan font-bold truncate max-w-sm">
                    "{currentResult.recovered_message}"
                  </span>
                </div>
              )}

              {/* Experiment History Comparison Chart (Recharts) */}
              {history.length > 1 && (
                <div className="glass-card p-5 border-slate-800 space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white font-mono uppercase tracking-wider">
                      Attack Resilience Comparison
                    </span>
                    <span className="text-[10px] text-slate-500 font-mono">Last {history.length} experiments</span>
                  </div>

                  <div className="h-48 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={history.map((h, i) => ({
                        name: `${h.attack_name.slice(0, 6)} #${history.length - i}`,
                        psnr: h.psnr_db,
                        ber: h.ber_percentage || 0,
                        success: h.extraction_success,
                      }))}>
                        <XAxis dataKey="name" stroke="#64748B" fontSize={10} fontStyle="mono" />
                        <YAxis stroke="#64748B" fontSize={10} fontStyle="mono" />
                        <Tooltip
                          contentStyle={{ backgroundColor: "#0F172A", borderColor: "#1E293B", borderRadius: "8px", fontSize: "11px", color: "#F8FAFC" }}
                        />
                        <Legend wrapperStyle={{ fontSize: "10px" }} />
                        <Bar dataKey="psnr" name="PSNR (dB)" fill="#38BDF8" radius={[4, 4, 0, 0]} />
                        <Bar dataKey="ber" name="BER (%)" fill="#F43F5E" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

