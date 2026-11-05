import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { WelcomeView } from './components/workspace/WelcomeView';
import { PromptComposer } from './components/workspace/PromptComposer';
import { ExecutionTimeline } from './components/execution/ExecutionTimeline';
import { ChartWorkspace } from './components/visualization/ChartWorkspace';
import { CodeEditorPanel } from './components/code/CodeEditorPanel';
import { AnalyticalReportPanel } from './components/report/AnalyticalReportPanel';
import { DatasetPreviewModal } from './components/workspace/DatasetPreviewModal';
import { ModelSettingsModal } from './components/settings/ModelSettingsModal';
import { DiagnosticsModal } from './components/settings/DiagnosticsModal';
import { useTheme } from './hooks/useTheme';
import { useExecutionStream } from './hooks/useExecutionStream';
import { api } from './api/client';
import { Session, Task, DatasetProfile, Artifact } from './types';
import { BarChart3, Code2, FileText, Sparkles } from 'lucide-react';

export function App() {
  const { theme, toggleTheme } = useTheme();

  // App State
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [activeSession, setActiveSession] = useState<Session | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [activeTab, setActiveTab] = useState<'visualization' | 'code' | 'report'>('visualization');
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  // Modals
  const [isDatasetModalOpen, setIsDatasetModalOpen] = useState(false);
  const [isModelSettingsOpen, setIsModelSettingsOpen] = useState(false);
  const [isDiagnosticsOpen, setIsDiagnosticsOpen] = useState(false);

  // Active Model
  const [activeProvider, setActiveProvider] = useState<string>('ollama');
  const [activeModel, setActiveModel] = useState<string>('llama3:8b');

  // Load sessions on mount
  const loadSessions = async () => {
    try {
      const data = await api.listSessions();
      setSessions(data);
      if (data.length > 0 && !activeSessionId) {
        selectSession(data[0].id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadSessions();
  }, []);

  const selectSession = async (id: string) => {
    setActiveSessionId(id);
    try {
      const detail = await api.getSession(id);
      setActiveSession(detail.session);
      setTasks(detail.tasks);
      setArtifacts(detail.artifacts);
      if (detail.session.selected_provider) setActiveProvider(detail.session.selected_provider);
      if (detail.session.selected_model) setActiveModel(detail.session.selected_model);
    } catch (err) {
      console.error(err);
    }
  };

  // SSE Stream
  const {
    events,
    currentStage,
    isExecuting,
    latestCode,
    latestError,
    correctionAttempts,
    clearStream,
  } = useExecutionStream(activeSessionId, () => {
    // Refresh session on task completion
    if (activeSessionId) {
      selectSession(activeSessionId);
    }
  });

  const handleNewSession = async () => {
    try {
      const newSess = await api.createSession('New Analysis', activeProvider, activeModel);
      setSessions(prev => [newSess, ...prev]);
      setActiveSessionId(newSess.id);
      setActiveSession(newSess);
      setTasks([]);
      setArtifacts([]);
      clearStream();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteSession = async (id: string) => {
    try {
      await api.deleteSession(id);
      setSessions(prev => prev.filter(s => s.id !== id));
      if (activeSessionId === id) {
        const remaining = sessions.filter(s => s.id !== id);
        if (remaining.length > 0) {
          selectSession(remaining[0].id);
        } else {
          setActiveSessionId(null);
          setActiveSession(null);
          setTasks([]);
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleDatasetUploaded = async (fileName: string, storedPath: string, profile: DatasetProfile) => {
    if (activeSession) {
      const updated = {
        ...activeSession,
        dataset_name: fileName,
        dataset_path: storedPath,
        dataset_profile: profile,
      };
      setActiveSession(updated);
    } else {
      try {
        const newSess = await api.createSession(`Analysis: ${fileName}`, activeProvider, activeModel);
        setActiveSessionId(newSess.id);
        const updated = {
          ...newSess,
          dataset_name: fileName,
          dataset_path: storedPath,
          dataset_profile: profile,
        };
        setActiveSession(updated);
        setSessions(prev => [updated, ...prev]);
      } catch (e) {
        console.error('Failed to create session on upload', e);
      }
    }
    loadSessions();
  };

  const handleSubmitPrompt = async (prompt: string) => {
    let sessId = activeSessionId;
    let currSess = activeSession;
    if (!sessId || !currSess) {
      const newSess = await api.createSession(prompt.slice(0, 30), activeProvider, activeModel);
      sessId = newSess.id;
      currSess = newSess;
      setActiveSessionId(sessId);
      setActiveSession(newSess);
      setSessions(prev => [newSess, ...prev]);
    }

    try {
      await api.startAnalysis({
        sessionId: sessId,
        prompt,
        datasetPath: currSess?.dataset_path,
        provider: activeProvider,
        model: activeModel,
      });
    } catch (err: any) {
      alert(err.message || 'Failed to start analysis');
    }
  };

  const handleCancelTask = async () => {
    try {
      if (activeSessionId) {
        await api.cancelAnalysis(activeSessionId, latestTask?.id);
      }
    } catch (err) {
      console.error('Failed to cancel task', err);
    }
  };

  const handleExitApplication = async () => {
    const confirmed = window.confirm('Are you sure you want to exit Data Mind and terminate the backend server?');
    if (!confirmed) return;
    try {
      await api.shutdown();
    } catch (err) {
      // Backend may exit before sending full response
    } finally {
      window.close();
      document.body.innerHTML = `
        <div style="display:flex;height:100vh;align-items:center;justify-content:center;font-family:sans-serif;background:#202124;color:#e8eaed;flex-direction:column;gap:12px;">
          <h2 style="font-size:20px;font-weight:500;">Data Mind has shut down.</h2>
          <p style="color:#9aa0a6;font-size:14px;">The backend engine process was cleanly terminated. You may close this tab or window.</p>
        </div>
      `;
    }
  };

  // Latest task data
  const latestTask = tasks.length > 0 ? tasks[tasks.length - 1] : null;
  const currentChartJson = latestTask?.chart_json;
  const currentReportMarkdown = latestTask?.report_json?.report_markdown;
  const currentCode = latestCode || latestTask?.code || '';
  const currentError = latestError || latestTask?.traceback;

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-google-bg dark:bg-google-dark-bg text-google-text dark:text-google-dark-text antialiased">
      {/* Sidebar */}
      <Sidebar
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={selectSession}
        onNewSession={handleNewSession}
        onDeleteSession={handleDeleteSession}
        onOpenModelSettings={() => setIsModelSettingsOpen(true)}
        onOpenDiagnostics={() => setIsDiagnosticsOpen(true)}
        onExitApplication={handleExitApplication}
        activeProvider={activeProvider}
        activeModel={activeModel}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
      />

      {/* Main Container */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Header */}
        <Header
          sessionTitle={activeSession?.title || 'Data Mind'}
          datasetName={activeSession?.dataset_name}
          datasetProfile={activeSession?.dataset_profile}
          onOpenDatasetPreview={() => setIsDatasetModalOpen(true)}
          activeProvider={activeProvider}
          activeModel={activeModel}
          onOpenModelSettings={() => setIsModelSettingsOpen(true)}
          theme={theme}
          onToggleTheme={toggleTheme}
        />

        {/* Live Agent Execution Timeline if task started */}
        {(isExecuting || events.length > 0 || latestTask) && (
          <ExecutionTimeline
            currentStage={currentStage || latestTask?.status || ''}
            isExecuting={isExecuting}
            events={events}
            correctionAttempts={correctionAttempts}
            error={currentError}
            onCancelTask={handleCancelTask}
          />
        )}

        {/* Center Workspace */}
        <div className="flex-1 flex flex-col overflow-hidden relative">
          {/* If no analysis executed yet and no dataset uploaded, show Welcome View */}
          {!latestTask && !isExecuting ? (
            <WelcomeView
              sessionId={activeSessionId || undefined}
              onDatasetUploaded={handleDatasetUploaded}
              onSelectPrompt={handleSubmitPrompt}
            />
          ) : (
            /* Analysis Active / Results View */
            <div className="flex-1 flex flex-col overflow-hidden p-4">
              {/* Output Tab Switcher */}
              <div className="flex items-center justify-between pb-3 select-none">
                <div className="flex items-center gap-1 bg-google-surface dark:bg-google-dark-surface p-1 rounded-lg border border-google-border dark:border-google-dark-border text-xs font-medium">
                  <button
                    onClick={() => setActiveTab('visualization')}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all ${
                      activeTab === 'visualization'
                        ? 'bg-google-bg dark:bg-google-dark-bg text-google-blue shadow-subtle font-semibold'
                        : 'text-google-muted dark:text-google-dark-muted hover:text-google-text'
                    }`}
                  >
                    <BarChart3 size={14} />
                    <span>Visualization</span>
                  </button>

                  <button
                    onClick={() => setActiveTab('code')}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all ${
                      activeTab === 'code'
                        ? 'bg-google-bg dark:bg-google-dark-bg text-google-blue shadow-subtle font-semibold'
                        : 'text-google-muted dark:text-google-dark-muted hover:text-google-text'
                    }`}
                  >
                    <Code2 size={14} />
                    <span>Python Code</span>
                  </button>

                  <button
                    onClick={() => setActiveTab('report')}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md transition-all ${
                      activeTab === 'report'
                        ? 'bg-google-bg dark:bg-google-dark-bg text-google-blue shadow-subtle font-semibold'
                        : 'text-google-muted dark:text-google-dark-muted hover:text-google-text'
                    }`}
                  >
                    <FileText size={14} />
                    <span>Analytical Report</span>
                  </button>
                </div>
              </div>

              {/* Tab Content Panes */}
              <div className="flex-1 overflow-hidden">
                {activeTab === 'visualization' && (
                  <ChartWorkspace chartJson={currentChartJson} theme={theme} />
                )}
                {activeTab === 'code' && (
                  <CodeEditorPanel
                    code={currentCode}
                    theme={theme}
                    error={currentError}
                    isExecuting={isExecuting}
                  />
                )}
                {activeTab === 'report' && (
                  <AnalyticalReportPanel
                    reportMarkdown={currentReportMarkdown}
                    metrics={latestTask?.report_json?.metrics}
                  />
                )}
              </div>
            </div>
          )}

          {/* Bottom Prompt Composer Bar */}
          <div className="p-4 bg-google-bg/95 dark:bg-google-dark-bg/95 border-t border-google-border dark:border-google-dark-border">
            <PromptComposer
              datasetName={activeSession?.dataset_name}
              datasetProfile={activeSession?.dataset_profile}
              onOpenDatasetModal={() => setIsDatasetModalOpen(true)}
              onSubmit={handleSubmitPrompt}
              onCancelTask={handleCancelTask}
              isExecuting={isExecuting}
            />
          </div>
        </div>
      </div>

      {/* Dataset Preview Modal */}
      <DatasetPreviewModal
        isOpen={isDatasetModalOpen}
        onClose={() => setIsDatasetModalOpen(false)}
        profile={activeSession?.dataset_profile || null}
      />

      {/* Model Settings Modal */}
      <ModelSettingsModal
        isOpen={isModelSettingsOpen}
        onClose={() => setIsModelSettingsOpen(false)}
        activeProvider={activeProvider}
        activeModel={activeModel}
        onSaveConfig={(prov, mdl) => {
          setActiveProvider(prov);
          setActiveModel(mdl);
        }}
      />

      {/* System Diagnostics Modal */}
      <DiagnosticsModal
        isOpen={isDiagnosticsOpen}
        onClose={() => setIsDiagnosticsOpen(false)}
      />
    </div>
  );
}

export default App;

