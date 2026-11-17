import React, { useState } from "react";
import { Navbar } from "./components/Navbar";
import { Dashboard } from "./pages/Dashboard";
import { EmbeddingStudio } from "./pages/EmbeddingStudio";
import { ExtractionStudio } from "./pages/ExtractionStudio";
import { RobustnessLab } from "./pages/RobustnessLab";
import { Analytics } from "./pages/Analytics";
import { ReportGenerator } from "./pages/ReportGenerator";
import { Login } from "./pages/Login";
import { api } from "./services/api";

export const App: React.FC = () => {
  const [currentUser, setCurrentUser] = useState<any | null>(api.getCurrentUser());
  const [currentTab, setCurrentTab] = useState("dashboard");

  // Handoff states between studios
  const [handoffImage, setHandoffImage] = useState<string | null>(null);
  const [handoffManifest, setHandoffManifest] = useState<any | null>(null);

  const handleSendToExtract = (imgUrl: string, manifest: any) => {
    setHandoffImage(imgUrl);
    setHandoffManifest(manifest);
    setCurrentTab("extract");
  };

  const handleSendToLab = (imgUrl: string, manifest: any) => {
    setHandoffImage(imgUrl);
    setHandoffManifest(manifest);
    setCurrentTab("lab");
  };

  const handleLogout = () => {
    api.logout();
    setCurrentUser(null);
  };

  // If not logged in, render the login page
  if (!currentUser) {
    return <Login onLoginSuccess={(user) => setCurrentUser(user)} />;
  }

  return (
    <div className="min-h-screen bg-[#070A11] text-slate-100 flex flex-col font-sans selection:bg-brand-cyan/20 selection:text-brand-cyan">
      <Navbar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        user={currentUser}
        onLogout={handleLogout}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-8">
        {currentTab === "dashboard" && <Dashboard onNavigate={(tab) => setCurrentTab(tab)} />}
        {currentTab === "embed" && (
          <EmbeddingStudio
            onSendToExtract={handleSendToExtract}
            onSendToLab={handleSendToLab}
          />
        )}
        {currentTab === "extract" && (
          <ExtractionStudio
            initialImageUrl={handoffImage}
            initialManifest={handoffManifest}
          />
        )}
        {currentTab === "lab" && (
          <RobustnessLab
            initialImageUrl={handoffImage}
            initialManifest={handoffManifest}
          />
        )}
        {currentTab === "analytics" && <Analytics />}
        {currentTab === "reports" && <ReportGenerator />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-navy-950/80 px-6 py-6 text-xs font-mono text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-300">SPECTRAMARK v1.0</span>
            <span>•</span>
            <span>Classical Digital Image Processing Platform</span>
            <span>•</span>
            <span className="text-brand-cyan">DCT-SVD-QIM</span>
          </div>
          <div>
            Blind Extraction • HMAC Permutation • Reed-Solomon FEC • Zero Secret Persistence
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
