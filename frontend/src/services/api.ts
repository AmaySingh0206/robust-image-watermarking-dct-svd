import { CapacityInfo, EmbedResult, ExtractResult, AttackResult, JobRecord } from "../types";

export const api = {
  async getHealth() {
    const res = await fetch("/health/live");
    return res.json();
  },

  async checkCapacity(width: number, height: number, repetitionFactor: number = 5): Promise<CapacityInfo> {
    const res = await fetch("/api/v1/watermarks/capacity", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        width,
        height,
        repetition_factor: repetitionFactor,
        parity_bytes: 32,
      }),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  async embedWatermark(formData: FormData): Promise<EmbedResult> {
    const res = await fetch("/api/v1/watermarks/embed", {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Watermark embedding failed");
    }
    return res.json();
  },

  async extractWatermark(formData: FormData): Promise<ExtractResult> {
    const res = await fetch("/api/v1/watermarks/extract", {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Watermark extraction failed");
    }
    return res.json();
  },

  async runAttack(formData: FormData): Promise<AttackResult> {
    const res = await fetch("/api/v1/experiments/run", {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Attack execution failed");
    }
    return res.json();
  },

  async runBenchmark(imageType: string = "natural_texture"): Promise<any> {
    const formData = new FormData();
    formData.append("image_type", imageType);
    const res = await fetch("/api/v1/experiments/benchmark", {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  async getJobs(limit: number = 15): Promise<JobRecord[]> {
    const res = await fetch(`/api/v1/jobs?limit=${limit}`);
    if (!res.ok) return [];
    return res.json();
  },

  async getJob(jobId: string): Promise<any> {
    const res = await fetch(`/api/v1/jobs/${jobId}`);
    if (!res.ok) throw new Error("Job not found");
    return res.json();
  },

  async getReport(jobId: string): Promise<any> {
    const res = await fetch(`/api/v1/reports/${jobId}`);
    if (!res.ok) throw new Error("Report not found");
    return res.json();
  },

  async login(username: string, password: string): Promise<any> {
    const res = await fetch("/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Login failed" }));
      throw new Error(err.detail || "Authentication failed");
    }
    const data = await res.json();
    localStorage.setItem("spectramark_token", data.token);
    localStorage.setItem("spectramark_user", JSON.stringify(data.user));
    return data;
  },

  getCurrentUser(): any {
    try {
      const u = localStorage.getItem("spectramark_user");
      return u ? JSON.parse(u) : null;
    } catch {
      return null;
    }
  },

  logout(): void {
    localStorage.removeItem("spectramark_token");
    localStorage.removeItem("spectramark_user");
  },
};

