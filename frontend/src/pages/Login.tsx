import React, { useState } from "react";
import { Shield, Lock, User, AlertCircle, ArrowRight, Sparkles, KeyRound } from "lucide-react";
import { api } from "../services/api";

interface LoginProps {
  onLoginSuccess: (user: any) => void;
}

export const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("spectramark2026");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      setError("Please provide username and password.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await api.login(username, password);
      onLoginSuccess(data.user);
    } catch (err: any) {
      setError(err.message || "Invalid credentials.");
    } finally {
      setLoading(false);
    }
  };

  const handleQuickDemo = async () => {
    setUsername("admin");
    setPassword("spectramark2026");
    setLoading(true);
    setError(null);
    try {
      const data = await api.login("admin", "spectramark2026");
      onLoginSuccess(data.user);
    } catch (err: any) {
      setError(err.message || "Login failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#070A11] text-slate-100 flex items-center justify-center p-4 relative overflow-hidden font-sans">
      {/* Background ambient lighting */}
      <div className="absolute -top-40 -left-40 w-96 h-96 rounded-full bg-sky-500/10 blur-3xl pointer-events-none"></div>
      <div className="absolute -bottom-40 -right-40 w-96 h-96 rounded-full bg-indigo-500/10 blur-3xl pointer-events-none"></div>

      <div className="w-full max-w-md relative z-10 space-y-6">
        {/* Brand Header */}
        <div className="text-center space-y-3">
          <div className="inline-flex w-16 h-16 rounded-2xl bg-gradient-to-tr from-brand-blue to-brand-cyan items-center justify-center shadow-xl shadow-sky-500/20 border border-sky-400/30 mb-2">
            <Shield className="w-8 h-8 text-slate-950 font-bold" />
          </div>
          <h1 className="text-3xl font-extrabold tracking-wider font-mono text-white">SPECTRAMARK</h1>
          <p className="text-xs text-slate-400 font-medium">
            Digital Image Watermarking, Copyright Protection & Forensic Verification
          </p>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-[11px] text-brand-cyan font-mono">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Classical DIP • DCT-SVD-QIM Engine</span>
          </div>
        </div>

        {/* Card */}
        <div className="glass-card p-8 border border-slate-800/80 shadow-2xl space-y-6">
          <div className="border-b border-slate-800/80 pb-4">
            <h2 className="text-sm font-bold font-mono text-white uppercase tracking-wider">
              Forensic Analyst Access
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">Enter authorized investigator credentials</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 font-mono">
                Username
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="admin"
                  className="w-full bg-slate-900/90 border border-slate-800 rounded-lg py-2.5 pl-9 pr-3 text-xs text-slate-100 font-mono focus:outline-none focus:border-brand-cyan transition-colors"
                />
                <User className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5 font-mono">
                Password
              </label>
              <div className="relative">
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full bg-slate-900/90 border border-slate-800 rounded-lg py-2.5 pl-9 pr-3 text-xs text-slate-100 font-mono focus:outline-none focus:border-brand-cyan transition-colors"
                />
                <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              </div>
            </div>

            {error && (
              <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className={`w-full py-3 rounded-xl font-mono text-xs font-bold uppercase tracking-wider transition-all flex items-center justify-center gap-2 ${
                loading
                  ? "bg-slate-800 text-slate-500 cursor-not-allowed"
                  : "bg-gradient-to-r from-sky-500 to-cyan-500 text-slate-950 shadow-lg shadow-sky-500/25 hover:shadow-sky-500/40 hover:opacity-95"
              }`}
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-slate-500 border-t-white rounded-full animate-spin"></div>
                  <span>Authenticating...</span>
                </>
              ) : (
                <>
                  <span>Sign In to Forensic Suite</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Quick Demo Credentials Banner */}
          <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-2.5 text-xs font-mono">
            <div className="flex items-center justify-between text-slate-400">
              <span className="flex items-center gap-1.5 font-semibold text-slate-300">
                <KeyRound className="w-3.5 h-3.5 text-brand-amber" />
                Demo Credentials:
              </span>
              <button
                type="button"
                onClick={handleQuickDemo}
                className="text-[11px] text-brand-cyan hover:underline font-bold"
              >
                1-Click Sign In
              </button>
            </div>
            <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-800">
              <span>Username: <b className="text-slate-200">admin</b></span>
              <span>Password: <b className="text-slate-200">spectramark2026</b></span>
            </div>
          </div>
        </div>

        <p className="text-center text-[11px] font-mono text-slate-500">
          SPECTRAMARK v1.0 • Classical DIP Architecture • Zero Secret Persistence
        </p>
      </div>
    </div>
  );
};

