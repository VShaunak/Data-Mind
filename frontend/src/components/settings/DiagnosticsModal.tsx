import React, { useState, useEffect } from 'react';
import { X, Activity, CheckCircle2, AlertCircle, RefreshCw, Server, HardDrive, Terminal } from 'lucide-react';
import { api } from '../../api/client';
import { DiagnosticsData } from '../../types';

interface DiagnosticsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const DiagnosticsModal: React.FC<DiagnosticsModalProps> = ({ isOpen, onClose }) => {
  const [data, setData] = useState<DiagnosticsData | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchDiagnostics = async () => {
    setIsLoading(true);
    try {
      const res = await api.getDiagnostics();
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchDiagnostics();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4 animate-in fade-in duration-150">
      <div className="bg-google-bg dark:bg-google-dark-bg border border-google-border dark:border-google-dark-border w-full max-w-xl rounded-xl shadow-modal overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-google-border dark:border-google-dark-border">
          <div className="flex items-center gap-2">
            <Activity size={16} className="text-google-blue" />
            <h3 className="text-sm font-semibold text-google-text dark:text-google-dark-text">
              System Diagnostics & Runtime Environment
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-google-muted hover:text-google-text dark:hover:text-google-dark-text hover:bg-google-surface transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-5 overflow-y-auto max-h-[75vh]">
          {isLoading || !data ? (
            <div className="flex items-center justify-center py-12 text-google-muted text-xs">
              <RefreshCw size={16} className="animate-spin mr-2 text-google-blue" />
              <span>Inspecting system runtimes and sandboxes...</span>
            </div>
          ) : (
            <>
              {/* Host Platform */}
              <div className="border border-google-border dark:border-google-dark-border rounded-xl p-4 bg-google-secondary dark:bg-google-dark-secondary">
                <div className="flex items-center gap-2 text-xs font-semibold text-google-text dark:text-google-dark-text mb-2">
                  <Terminal size={15} className="text-google-blue" />
                  <span>Windows Operating System & Python Runtime</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs text-google-text dark:text-google-dark-text">
                  <div>
                    <span className="text-google-muted dark:text-google-dark-muted">OS: </span>
                    <span className="font-medium">{data.os_info.platform} {data.os_info.platform_release} ({data.os_info.architecture})</span>
                  </div>
                  <div>
                    <span className="text-google-muted dark:text-google-dark-muted">Python: </span>
                    <span className="font-mono">{data.os_info.python_version}</span>
                  </div>
                </div>
              </div>

              {/* Docker Desktop & Sandbox Boundary */}
              <div className="border border-google-border dark:border-google-dark-border rounded-xl p-4 bg-google-secondary dark:bg-google-dark-secondary">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2 text-xs font-semibold text-google-text dark:text-google-dark-text">
                    <Server size={15} className="text-google-blue" />
                    <span>Container Sandbox Execution Engine</span>
                  </div>
                  <span
                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium ${
                      data.docker.docker_available
                        ? 'bg-google-green-subtle text-google-green'
                        : 'bg-google-amber-subtle text-google-amber'
                    }`}
                  >
                    {data.docker.docker_available ? <CheckCircle2 size={11} /> : <AlertCircle size={11} />}
                    {data.docker.sandbox_mode}
                  </span>
                </div>
                <p className="text-xs text-google-muted dark:text-google-dark-muted">
                  {data.docker.docker_available
                    ? 'Docker Desktop is active. Python execution is isolated inside unprivileged containers with read-only root and network disabled.'
                    : 'Docker Desktop is currently stopped. Code is securely validated with AST import and function allowlists, and executed inside an isolated temporary sandbox.'}
                </p>
                {data.docker.wsl2_installed && (
                  <div className="mt-2 text-[11px] text-google-subtle">
                    WSL2 subsystem is installed and available.
                  </div>
                )}
              </div>

              {/* User Storage & Database */}
              <div className="border border-google-border dark:border-google-dark-border rounded-xl p-4 bg-google-secondary dark:bg-google-dark-secondary">
                <div className="flex items-center gap-2 text-xs font-semibold text-google-text dark:text-google-dark-text mb-2">
                  <HardDrive size={15} className="text-google-blue" />
                  <span>Storage & SQLite Persistence</span>
                </div>
                <div className="space-y-1 text-xs text-google-text dark:text-google-dark-text">
                  <div className="truncate">
                    <span className="text-google-muted dark:text-google-dark-muted">User Data: </span>
                    <span className="font-mono text-[11px]">{data.storage.home_path}</span>
                  </div>
                  <div className="flex justify-between text-xs pt-1">
                    <span>
                      Writable: {data.storage.writable ? <span className="text-google-green font-medium">Yes</span> : <span className="text-google-red font-medium">No</span>}
                    </span>
                    <span>Free Space: <span className="font-medium">{data.storage.free_disk_gb} GB</span></span>
                  </div>
                </div>
              </div>

              {/* Detected Providers */}
              <div>
                <h4 className="text-xs font-semibold text-google-text dark:text-google-dark-text mb-2">
                  Local Inference Providers
                </h4>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(data.providers).map(([pName, pStatus]) => (
                    <div
                      key={pName}
                      className="border border-google-border dark:border-google-dark-border rounded-lg p-2.5 flex items-center justify-between text-xs"
                    >
                      <div>
                        <div className="font-medium capitalize">{pName.replace('_', ' ')}</div>
                        <div className="text-[10px] text-google-muted truncate max-w-[130px] font-mono">
                          {pStatus.base_url}
                        </div>
                      </div>
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${
                          pStatus.available
                            ? 'bg-google-green-subtle text-google-green'
                            : 'bg-google-surface text-google-muted'
                        }`}
                      >
                        {pStatus.available ? 'Ready' : 'Offline'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-3.5 bg-google-secondary dark:bg-google-dark-secondary border-t border-google-border dark:border-google-dark-border">
          <button
            onClick={fetchDiagnostics}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-google-border dark:border-google-dark-border text-xs text-google-text dark:text-google-dark-text hover:bg-google-surface transition-colors font-medium"
          >
            <RefreshCw size={12} className={isLoading ? 'animate-spin' : ''} />
            <span>Recheck Systems</span>
          </button>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-google-blue text-white text-xs font-medium hover:bg-google-blue-hover shadow-subtle transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

