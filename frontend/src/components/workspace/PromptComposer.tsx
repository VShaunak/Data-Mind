import React, { useState, useRef, useEffect } from 'react';
import { ArrowUp, Database, Sparkles, Loader2, Square } from 'lucide-react';
import { DatasetProfile } from '../../types';

interface PromptComposerProps {
  datasetName?: string;
  datasetProfile?: DatasetProfile;
  onOpenDatasetModal?: () => void;
  onSubmit: (prompt: string) => void;
  onCancelTask?: () => void;
  isExecuting: boolean;
}

export const PromptComposer: React.FC<PromptComposerProps> = ({
  datasetName,
  datasetProfile,
  onOpenDatasetModal,
  onSubmit,
  onCancelTask,
  isExecuting,
}) => {
  const [prompt, setPrompt] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [prompt]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!prompt.trim() || isExecuting) return;
    onSubmit(prompt.trim());
    setPrompt('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <form
        onSubmit={handleSubmit}
        className="relative bg-google-bg dark:bg-google-dark-bg border border-google-border dark:border-google-dark-border rounded-2xl shadow-subtle focus-within:border-google-blue focus-within:ring-1 focus-within:ring-google-blue transition-all p-3"
      >
        {/* Attached Dataset Tag if any */}
        {datasetName && (
          <div className="flex items-center gap-1.5 mb-2">
            <button
              type="button"
              onClick={onOpenDatasetModal}
              className="flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] bg-google-surface dark:bg-google-dark-surface border border-google-border dark:border-google-dark-border hover:border-google-blue transition-colors text-google-text dark:text-google-dark-text"
            >
              <Database size={11} className="text-google-blue shrink-0" />
              <span className="font-medium truncate max-w-[180px]">{datasetName}</span>
              {datasetProfile && (
                <span className="text-google-muted dark:text-google-dark-muted">
                  • {datasetProfile.row_count} rows
                </span>
              )}
            </button>
          </div>
        )}

        {/* Input Area */}
        <textarea
          ref={textareaRef}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            datasetName
              ? `Describe the analysis, question, or visualization for ${datasetName}...`
              : 'Attach a dataset above or describe an analytical task...'
          }
          rows={1}
          disabled={isExecuting}
          className="w-full resize-none outline-none text-sm bg-transparent text-google-text dark:text-google-dark-text placeholder:text-google-muted/70 min-h-[44px] max-h-[180px] py-1"
        />

        {/* Bottom Actions */}
        <div className="flex items-center justify-between mt-2 pt-1 border-t border-google-border/50 dark:border-google-dark-border/50">
          <div className="text-[11px] text-google-subtle dark:text-google-dark-muted flex items-center gap-1">
            <Sparkles size={12} className="text-google-blue" />
            <span>Autonomous agent with self-correction & AST guardrails</span>
          </div>

          <div className="flex items-center gap-2">
            {isExecuting && onCancelTask && (
              <button
                type="button"
                onClick={onCancelTask}
                className="px-2.5 py-1 rounded-full text-xs font-medium bg-red-50 text-red-600 border border-red-200 dark:bg-red-950/40 dark:text-red-400 dark:border-red-800 hover:bg-red-100 dark:hover:bg-red-900/50 flex items-center gap-1.5 transition-colors"
                title="Stop / Kill currently executing analysis task"
              >
                <Square size={10} fill="currentColor" />
                <span>Stop Task</span>
              </button>
            )}

            <button
              type="submit"
              disabled={!prompt.trim() || isExecuting}
              className={`w-8 h-8 rounded-full flex items-center justify-center transition-all ${
                prompt.trim() && !isExecuting
                  ? 'bg-google-blue text-white hover:bg-google-blue-hover shadow-subtle'
                  : 'bg-google-surface dark:bg-google-dark-surface text-google-muted cursor-not-allowed'
              }`}
              title="Execute analysis (Enter)"
            >
              {isExecuting ? (
                <Loader2 size={16} className="animate-spin text-google-blue" />
              ) : (
                <ArrowUp size={16} strokeWidth={2.5} />
              )}
            </button>
          </div>
        </div>
      </form>

      <p className="text-center text-[11px] text-google-subtle dark:text-google-dark-muted mt-2">
        Data Mind synthesizes Python, verifies AST guardrails, executes in container sandbox, and checks results.
      </p>
    </div>
  );
};

