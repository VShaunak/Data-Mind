import { Session, Task, DatasetProfile, Artifact, DiagnosticsData, ProviderStatus } from '../types';

const API_BASE = '/api';

export const api = {
  // Sessions
  async createSession(title?: string, provider?: string, model?: string): Promise<Session> {
    const res = await fetch(`${API_BASE}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, selected_provider: provider, selected_model: model }),
    });
    if (!res.ok) throw new Error('Failed to create session');
    return res.json();
  },

  async listSessions(): Promise<Session[]> {
    const res = await fetch(`${API_BASE}/sessions`);
    if (!res.ok) throw new Error('Failed to list sessions');
    return res.json();
  },

  async getSession(sessionId: string): Promise<{ session: Session; tasks: Task[]; artifacts: Artifact[] }> {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}`);
    if (!res.ok) throw new Error('Failed to get session');
    return res.json();
  },

  async deleteSession(sessionId: string): Promise<boolean> {
    const res = await fetch(`${API_BASE}/sessions/${sessionId}`, { method: 'DELETE' });
    return res.ok;
  },

  // Datasets
  async uploadDataset(file: File, sessionId?: string, sheetName?: string): Promise<{
    file_name: string;
    stored_path: string;
    profile: DatasetProfile;
  }> {
    const formData = new FormData();
    formData.append('file', file);
    if (sessionId) formData.append('session_id', sessionId);
    if (sheetName) formData.append('sheet_name', sheetName);

    const res = await fetch(`${API_BASE}/datasets/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
  },

  async previewDataset(path: string, sheetName?: string, limit = 50): Promise<{
    columns: { name: string; type: string }[];
    data: Record<string, any>[];
    total_rows: number;
  }> {
    const params = new URLSearchParams({ path, limit: limit.toString() });
    if (sheetName) params.append('sheet_name', sheetName);
    const res = await fetch(`${API_BASE}/datasets/preview?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to preview dataset');
    return res.json();
  },

  // Analysis
  async startAnalysis(params: {
    sessionId: string;
    prompt: string;
    datasetPath?: string;
    provider?: string;
    model?: string;
  }): Promise<{ task_id: string; session_id: string; status: string }> {
    const res = await fetch(`${API_BASE}/analysis/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: params.sessionId,
        prompt: params.prompt,
        dataset_path: params.datasetPath,
        provider: params.provider,
        model: params.model,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Analysis start failed' }));
      throw new Error(err.detail || 'Failed to start analysis');
    }
    return res.json();
  },

  async cancelAnalysis(sessionId: string, taskId?: string): Promise<{ success: boolean; message: string }> {
    const res = await fetch(`${API_BASE}/analysis/cancel`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, task_id: taskId }),
    });
    return res.json();
  },

  async shutdown(): Promise<{ success: boolean; message: string }> {
    const res = await fetch(`${API_BASE}/shutdown`, { method: 'POST' });
    return res.json();
  },

  // Models & Providers
  async getProviders(): Promise<{
    providers: Record<string, ProviderStatus>;
    default_provider: string;
    default_model: string;
    temperature: number;
    top_p: number;
    max_tokens: number;
  }> {
    const res = await fetch(`${API_BASE}/models/providers`);
    if (!res.ok) throw new Error('Failed to load providers');
    return res.json();
  },

  async testConnection(provider: string, model: string): Promise<any> {
    const res = await fetch(`${API_BASE}/models/test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider, model }),
    });
    return res.json();
  },

  async updateModelConfig(config: {
    provider: string;
    base_url: string;
    model?: string;
    temperature?: number;
    top_p?: number;
    max_tokens?: number;
  }): Promise<any> {
    const res = await fetch(`${API_BASE}/models/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });
    return res.json();
  },

  // Diagnostics
  async getDiagnostics(): Promise<DiagnosticsData> {
    const res = await fetch(`${API_BASE}/diagnostics`);
    if (!res.ok) throw new Error('Failed to fetch diagnostics');
    return res.json();
  },
};

