import React from "react";
import { Shield, Lock, Search, Cpu, BarChart3, FileText, CheckCircle2, LogOut, User } from "lucide-react";

interface NavbarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  user?: any;
  onLogout?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentTab, setCurrentTab, user, onLogout }) => {
  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: BarChart3 },
    { id: "embed", label: "Embedding Studio", icon: Lock },
    { id: "extract", label: "Extraction Studio", icon: Search },
    { id: "lab", label: "Robustness Lab", icon: Cpu },
    { id: "analytics", label: "Analytics", icon: BarChart3 },
    { id: "reports", label: "Forensic Reports", icon: FileText },
  ];

  return (
    <header className="sticky top-0 z-50 bg-[#070A11]/90 backdrop-blur-md border-b border-slate-800/80 px-6 py-3.5">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand identity */}
        <div 
          onClick={() => setCurrentTab("dashboard")} 
          className="flex items-center gap-3 cursor-pointer group select-none"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-blue to-brand-cyan flex items-center justify-center shadow-lg shadow-sky-500/20 group-hover:shadow-sky-500/40 transition-all">
            <Shield className="w-5 h-5 text-slate-950 font-bold" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold tracking-wider text-lg text-white font-mono">SPECTRAMARK</span>
              <span className="text-[10px] font-semibold uppercase tracking-widest px-2 py-0.5 rounded-full bg-sky-500/10 text-brand-cyan border border-sky-500/30">
                DCT-SVD
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">Protect. Embed. Verify.</p>
          </div>
        </div>

        {/* Navigation tabs */}
        <nav className="hidden md:flex items-center gap-1 bg-navy-900/90 p-1.5 rounded-xl border border-slate-800">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentTab(item.id)}
                className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  active
                    ? "bg-gradient-to-r from-sky-600 to-cyan-600 text-white shadow-md shadow-sky-600/30 font-semibold"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${active ? "text-white" : "text-slate-400"}`} />
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* Status pill & User profile */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="font-medium">DCT-SVD Active</span>
          </div>

          {user && (
            <div className="flex items-center gap-2.5 pl-3 border-l border-slate-800">
              <div className="hidden lg:block text-right">
                <div className="text-xs font-semibold text-slate-200 font-mono leading-tight">{user.full_name || user.username}</div>
                <div className="text-[10px] text-brand-cyan font-mono leading-tight">{user.role || "Analyst"}</div>
              </div>
              <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 font-bold text-xs font-mono">
                {(user.username || "A").slice(0, 1).toUpperCase()}
              </div>
              {onLogout && (
                <button
                  onClick={onLogout}
                  title="Sign out"
                  className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-rose-400 hover:border-rose-500/30 transition-all"
                >
                  <LogOut className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

