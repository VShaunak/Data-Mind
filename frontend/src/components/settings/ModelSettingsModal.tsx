import React, { useState, useEffect } from 'react';
import { X, Cpu, CheckCircle2, AlertCircle, Loader2, RefreshCw } from 'lucide-react';
import { api } from '../../api/client';
import { ProviderStatus } from '../../types';

interface ModelSettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  activeProvider: string;
  activeModel: string;
  onSaveConfig: (provider: string, model: string) => void;
}

export const ModelSettingsModal: React.FC<ModelSettingsModalProps> = ({
  isOpen,
  onClose,
  activeProvider,
  activeModel,
  onSaveConfig,
}) => {
  const [providers, setProviders] = useState<Record<string, ProviderStatus>>({});
  const [selectedProvider, setSelectedProvider] = useState(activeProvider);
  const [selectedModel, setSelectedModel] = useState(activeModel);
  const [baseUrl, setBaseUrl] = useState('');
  const [temperature, setTemperature] = useState(0.1);
  const [topP, setTopP] = useState(0.95);
  const [maxTokens, setMaxTokens] = useState(4096);
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchProviders = async () => {
    setIsLoading(true);
    try {
      const data = await api.getProviders();
      setProviders(data.providers);
      setTemperature(data.temperature);
      setTopP(data.top_p);
      setMaxTokens(data.max_tokens);
      if (data.providers[selectedProvider]) {
        setBaseUrl(data.providers[selectedProvider].base_url);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchProviders();
    }
  }, [isOpen]);

  useEffect(() => {
    if (providers[selectedProvider]) {
      setBaseUrl(providers[selectedProvider].base_url);
      const models = providers[selectedProvider].models || [];
      if (models.length > 0 && !models.some(m => m.id === selectedModel)) {
        setSelectedModel(models[0].id);
      }
    }
  }, [selectedProvider, providers]);

  const handleTestConnection = async () => {
    setIsTesting(true);
    setTestResult(null);
    try {
      const res = await api.testConnection(selectedProvider, selectedModel);
      if (res.success) {
        setTestResult({
          success: true,
          message: `Connected successfully! Latency: ${Math.round(res.latency_ms)}ms`,
        });
      } else {
        setTestResult({
          success: false,
          message: res.error || 'Failed to connect to local model endpoint.',
        });
      }
    } catch (err: any) {
      setTestResult({ success: false, message: err.message });
    } finally {
      setIsTesting(false);
    }
  };

  const handleSave = async () => {
    try {
      await api.updateModelConfig({
        provider: selectedProvider,
        base_url: baseUrl,
        model: selectedModel,
        temperature,
        top_p: topP,
        max_tokens: maxTokens,
      });
      onSaveConfig(selectedProvider, selectedModel);
      onClose();
    } catch (err) {
      console.error(err);
    }
  };

  if (!isOpen) return null;

  const currentProviderInfo = providers[selectedProvider];
  const availableModels = currentProviderInfo?.models || [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4 animate-in fade-in duration-150">
      <div className="bg-google-bg dark:bg-google-dark-bg border border-google-border dark:border-google-dark-border w-full max-w-xl rounded-xl shadow-modal overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-google-border dark:border-google-dark-border">
          <div className="flex items-center gap-2">
            <Cpu size={16} className="text-google-blue" />
            <h3 className="text-sm font-semibold text-google-text dark:text-google-dark-text">
              Local LLM Provider & Model Settings
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
          {/* Provider Selection */}
          <div>
            <label className="block text-xs font-medium text-google-text dark:text-google-dark-text mb-2">
              Inference Provider
            </label>
            <div className="grid grid-cols-4 gap-2">
              {[
                { id: 'ollama', name: 'Ollama' },
                { id: 'lm_studio', name: 'LM Studio' },
                { id: 'llamacpp', name: 'llama.cpp' },
                { id: 'openai_compatible', name: 'Generic API' },
              ].map((p) => (
                <button
                  key={p.id}
                  onClick={() => setSelectedProvider(p.id)}
                  className={`py-2 px-3 rounded-lg text-xs font-medium border text-center transition-all ${
                    selectedProvider === p.id
                      ? 'border-google-blue bg-google-blue-subtle text-google-blue dark:bg-google-blue-darkSubtle'
                      : 'border-google-border dark:border-google-dark-border text-google-text dark:text-google-dark-text hover:bg-google-surface'
                  }`}
                >
                  {p.name}
                </button>
              ))}
            </div>
          </div>

          {/* Base URL */}
          <div>
            <label className="block text-xs font-medium text-google-text dark:text-google-dark-text mb-1.5">
              Provider Endpoint URL
            </label>
            <input
              type="text"
              value={baseUrl}
              onChange={(e) => setBaseUrl(e.target.value)}
              placeholder="http://127.0.0.1:11434"
              className="w-full text-xs font-mono px-3 py-2 rounded-lg bg-google-surface dark:bg-google-dark-surface border border-google-border dark:border-google-dark-border outline-none focus:border-google-blue text-google-text dark:text-google-dark-text"
            />
          </div>

          {/* Model Name */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-xs font-medium text-google-text dark:text-google-dark-text">
                Active Model
              </label>
              <button
                onClick={fetchProviders}
                disabled={isLoading}
                className="flex items-center gap-1 text-[11px] text-google-blue hover:underline"
              >
                <RefreshCw size={11} className={isLoading ? 'animate-spin' : ''} />
                <span>Refresh Models</span>
              </button>
            </div>

            {availableModels.length > 0 ? (
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="w-full text-xs px-3 py-2 rounded-lg bg-google-surface dark:bg-google-dark-surface border border-google-border dark:border-google-dark-border outline-none focus:border-google-blue text-google-text dark:text-google-dark-text"
              >
                {availableModels.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.name} {m.size ? `(${m.size})` : ''}
                  </option>
                ))}
              </select>
            ) : (
              <input
                type="text"
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                placeholder="e.g. llama3:8b, mistral, qwen2.5-coder"
                className="w-full text-xs px-3 py-2 rounded-lg bg-google-surface dark:bg-google-dark-surface border border-google-border dark:border-google-dark-border outline-none focus:border-google-blue text-google-text dark:text-google-dark-text"
              />
            )}
          </div>

          {/* Hyperparameters */}
          <div className="grid grid-cols-2 gap-4 pt-2 border-t border-google-border dark:border-google-dark-border">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-google-muted dark:text-google-dark-muted">Temperature</span>
                <span className="font-mono">{temperature}</span>
              </div>
              <input
                type="range"
                min="0.0"
                max="1.0"
                step="0.05"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                className="w-full accent-google-blue"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-google-muted dark:text-google-dark-muted">Top P</span>
                <span className="font-mono">{topP}</span>
              </div>
              <input
                type="range"
                min="0.1"
                max="1.0"
                step="0.05"
                value={topP}
                onChange={(e) => setTopP(parseFloat(e.target.value))}
                className="w-full accent-google-blue"
              />
            </div>
          </div>

          {/* Test Connection Result */}
          {testResult && (
            <div
              className={`p-3 rounded-lg text-xs flex items-center gap-2 ${
                testResult.success
                  ? 'bg-google-green-subtle text-google-green'
                  : 'bg-google-red-subtle text-google-red'
              }`}
            >
              {testResult.success ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
              <span>{testResult.message}</span>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-3.5 bg-google-secondary dark:bg-google-dark-secondary border-t border-google-border dark:border-google-dark-border">
          <button
            onClick={handleTestConnection}
            disabled={isTesting}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-google-border dark:border-google-dark-border text-xs text-google-text dark:text-google-dark-text hover:bg-google-surface transition-colors font-medium"
          >
            {isTesting && <Loader2 size={13} className="animate-spin text-google-blue" />}
            <span>Test Connection</span>
          </button>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-3 py-1.5 rounded-lg text-xs text-google-muted hover:text-google-text transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-1.5 rounded-lg bg-google-blue text-white text-xs font-medium hover:bg-google-blue-hover shadow-subtle transition-colors"
            >
              Save Configuration
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

