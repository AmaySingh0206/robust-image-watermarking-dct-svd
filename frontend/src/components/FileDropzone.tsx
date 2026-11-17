import React, { useRef, useState } from "react";
import { UploadCloud, Image as ImageIcon, X, AlertCircle } from "lucide-react";

interface FileDropzoneProps {
  onFileSelect: (file: File, previewUrl: string, dims: [number, number]) => void;
  selectedFile: File | null;
  onClear: () => void;
  label?: string;
  accept?: string;
}

export const FileDropzone: React.FC<FileDropzoneProps> = ({
  onFileSelect,
  selectedFile,
  onClear,
  label = "Upload Image (PNG, JPEG, WebP, TIFF)",
  accept = "image/png,image/jpeg,image/webp,image/tiff",
}) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const [dims, setDims] = useState<[number, number] | null>(null);

  const processFile = (file: File) => {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      const dimensions: [number, number] = [img.naturalWidth, img.naturalHeight];
      setPreview(url);
      setDims(dimensions);
      onFileSelect(file, url, dimensions);
    };
    img.src = url;
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    setPreview(null);
    setDims(null);
    if (inputRef.current) inputRef.current.value = "";
    onClear();
  };

  return (
    <div className="w-full">
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        onChange={handleChange}
        className="hidden"
      />

      {!selectedFile || !preview ? (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all flex flex-col items-center justify-center gap-3 ${
            isDragging
              ? "border-brand-cyan bg-sky-500/10 shadow-lg shadow-sky-500/10"
              : "border-slate-800 hover:border-slate-700 bg-navy-900/60 hover:bg-navy-900"
          }`}
        >
          <div className="w-12 h-12 rounded-xl bg-slate-800/80 flex items-center justify-center text-slate-300">
            <UploadCloud className="w-6 h-6 text-brand-cyan" />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-200">{label}</p>
            <p className="text-xs text-slate-500 mt-1">Drag and drop or click to browse</p>
          </div>
          <div className="flex items-center gap-2 text-[11px] text-slate-400 font-mono">
            <span>PNG</span> • <span>JPEG</span> • <span>WebP</span> • <span>Max 25MB</span>
          </div>
        </div>
      ) : (
        <div className="glass-card p-4 relative flex items-center gap-4 border border-slate-800">
          <div className="w-20 h-20 rounded-lg overflow-hidden bg-slate-900 border border-slate-700/80 flex-shrink-0 relative group">
            <img src={preview} alt="Upload preview" className="w-full h-full object-cover" />
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="font-medium text-sm text-slate-200 truncate">{selectedFile.name}</span>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-sky-500/10 text-brand-cyan border border-sky-500/20">
                {selectedFile.type.split("/")[1] || "image"}
              </span>
            </div>

            <div className="flex items-center gap-4 text-xs text-slate-400 mt-1 font-mono">
              {dims && (
                <span>
                  {dims[0]} × {dims[1]} px
                </span>
              )}
              <span>{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</span>
            </div>

            {dims && (dims[0] < 200 || dims[1] < 200) && (
              <p className="text-[11px] text-amber-400 flex items-center gap-1 mt-1">
                <AlertCircle className="w-3.5 h-3.5" />
                Small dimension may restrict watermark capacity.
              </p>
            )}
          </div>

          <button
            onClick={handleClear}
            className="p-2 rounded-lg bg-slate-800 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 transition-all"
            title="Remove file"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
};

