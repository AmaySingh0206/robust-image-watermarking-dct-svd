import React, { useState } from "react";
import { SlidersHorizontal, Columns, Eye } from "lucide-react";

interface ImageCompareSliderProps {
  originalUrl: string;
  watermarkedUrl: string;
  originalLabel?: string;
  watermarkedLabel?: string;
}

export const ImageCompareSlider: React.FC<ImageCompareSliderProps> = ({
  originalUrl,
  watermarkedUrl,
  originalLabel = "Original Host Asset",
  watermarkedLabel = "Watermarked Asset (DCT-SVD)",
}) => {
  const [sliderPosition, setSliderPosition] = useState(50);
  const [viewMode, setViewMode] = useState<"slider" | "side_by_side">("slider");

  return (
    <div className="w-full flex flex-col gap-3">
      {/* View controls */}
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
          Visual Fidelity Inspection
        </span>

        <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 rounded-lg p-1 text-xs">
          <button
            onClick={() => setViewMode("slider")}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs transition-all ${
              viewMode === "slider"
                ? "bg-sky-600 text-white font-medium"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <SlidersHorizontal className="w-3.5 h-3.5" />
            Split Slider
          </button>
          <button
            onClick={() => setViewMode("side_by_side")}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs transition-all ${
              viewMode === "side_by_side"
                ? "bg-sky-600 text-white font-medium"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Columns className="w-3.5 h-3.5" />
            Side-by-Side
          </button>
        </div>
      </div>

      {viewMode === "slider" ? (
        <div className="relative w-full aspect-video max-h-[460px] rounded-xl overflow-hidden select-none border border-slate-800 glass-card">
          {/* Watermarked Image (Bottom layer) */}
          <img
            src={watermarkedUrl}
            alt="Watermarked"
            className="absolute inset-0 w-full h-full object-contain pointer-events-none bg-slate-950/80"
          />
          <div className="absolute bottom-3 right-3 bg-slate-900/90 border border-slate-700/80 px-2.5 py-1 rounded-md text-[11px] font-mono text-brand-cyan">
            {watermarkedLabel}
          </div>

          {/* Original Image (Top layer clipped by slider) */}
          <div
            className="absolute inset-0 overflow-hidden pointer-events-none"
            style={{ width: `${sliderPosition}%` }}
          >
            <img
              src={originalUrl}
              alt="Original"
              className="absolute inset-0 w-full h-full object-contain bg-slate-950/80"
              style={{ width: "100%", maxWidth: "none" }}
            />
            <div className="absolute bottom-3 left-3 bg-slate-900/90 border border-slate-700/80 px-2.5 py-1 rounded-md text-[11px] font-mono text-slate-300">
              {originalLabel}
            </div>
          </div>

          {/* Vertical Divider line */}
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-brand-cyan shadow-[0_0_10px_#38bdf8] pointer-events-none"
            style={{ left: `${sliderPosition}%` }}
          >
            <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-7 h-7 rounded-full bg-slate-900 border-2 border-brand-cyan flex items-center justify-center shadow-lg text-brand-cyan text-[10px]">
              ↔
            </div>
          </div>

          {/* Invisible Range Input Slider */}
          <input
            type="range"
            min="0"
            max="100"
            value={sliderPosition}
            onChange={(e) => setSliderPosition(Number(e.target.value))}
            className="absolute inset-0 w-full h-full opacity-0 cursor-ew-resize z-20"
          />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="glass-card p-3 flex flex-col gap-2">
            <div className="text-xs text-slate-400 font-mono flex items-center justify-between">
              <span>{originalLabel}</span>
              <span className="text-[10px] text-slate-500">Host Reference</span>
            </div>
            <div className="aspect-video rounded-lg overflow-hidden bg-slate-950/80 border border-slate-800">
              <img src={originalUrl} alt="Original" className="w-full h-full object-contain" />
            </div>
          </div>

          <div className="glass-card p-3 flex flex-col gap-2">
            <div className="text-xs text-brand-cyan font-mono flex items-center justify-between">
              <span>{watermarkedLabel}</span>
              <span className="text-[10px] text-brand-cyan/80">Embedded</span>
            </div>
            <div className="aspect-video rounded-lg overflow-hidden bg-slate-950/80 border border-slate-800">
              <img src={watermarkedUrl} alt="Watermarked" className="w-full h-full object-contain" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

