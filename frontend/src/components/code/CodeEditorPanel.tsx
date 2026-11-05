import React, { useState } from 'react';
import Editor from '@monaco-editor/react';
import { Copy, Check, Play, Code2, ShieldCheck, AlertCircle } from 'lucide-react';
import { Theme } from '../../hooks/useTheme';

interface CodeEditorPanelProps {
  code: string;
  theme: Theme;
  onExecuteCode?: (editedCode: string) => void;
  isExecuting?: boolean;
  error?: string | null;
}

export const CodeEditorPanel: React.FC<CodeEditorPanelProps> = ({
  code,
  theme,
  onExecuteCode,
  isExecuting = false,
  error,
}) => {
  const [currentCode, setCurrentCode] = useState(code);
  const [copied, setCopied] = useState(false);
  const [isEditable, setIsEditable] = useState(false);

  React.useEffect(() => {
    setCurrentCode(code);
  }, [code]);

  const handleCopy = () => {
    navigator.clipboard.writeText(currentCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex flex-col h-full bg-google-bg dark:bg-google-dark-bg border border-google-border dark:border-google-dark-border rounded-xl overflow-hidden shadow-subtle">
      {/* Editor Header */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-google-secondary dark:bg-google-dark-secondary border-b border-google-border dark:border-google-dark-border select-none">
        <div className="flex items-center gap-2">
          <Code2 size={15} className="text-google-blue" />
          <span className="text-xs font-semibold text-google-text dark:text-google-dark-text">
            Synthesized Python Script
          </span>
          <span className="inline-flex items-center gap-1 text-[10px] text-google-muted dark:text-google-dark-muted bg-google-surface dark:bg-google-dark-surface px-2 py-0.5 rounded font-mono">
            <ShieldCheck size={11} className="text-google-green" /> AST Guarded
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsEditable(!isEditable)}
            className={`text-[11px] px-2 py-1 rounded border transition-colors ${
              isEditable
                ? 'bg-google-blue-subtle text-google-blue border-google-blue'
                : 'bg-google-bg dark:bg-google-dark-bg text-google-muted border-google-border dark:border-google-dark-border'
            }`}
          >
            {isEditable ? 'Editing Mode' : 'Read Only'}
          </button>

          <button
            onClick={handleCopy}
            className="flex items-center gap-1 px-2 py-1 text-[11px] rounded bg-google-bg dark:bg-google-dark-bg border border-google-border dark:border-google-dark-border text-google-text dark:text-google-dark-text hover:bg-google-surface transition-colors"
            title="Copy code to clipboard"
          >
            {copied ? <Check size={12} className="text-google-green" /> : <Copy size={12} />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>

          {isEditable && onExecuteCode && (
            <button
              onClick={() => onExecuteCode(currentCode)}
              disabled={isExecuting}
              className="flex items-center gap-1 px-2.5 py-1 text-[11px] font-medium rounded bg-google-blue text-white hover:bg-google-blue-hover transition-colors shadow-subtle"
            >
              <Play size={11} />
              <span>Run Script</span>
            </button>
          )}
        </div>
      </div>

      {/* Editor Body */}
      <div className="flex-1 min-h-[300px]">
        <Editor
          height="100%"
          defaultLanguage="python"
          language="python"
          value={currentCode}
          theme={theme === 'dark' ? 'vs-dark' : 'light'}
          options={{
            readOnly: !isEditable,
            minimap: { enabled: false },
            fontSize: 12.5,
            fontFamily: '"Roboto Mono", "JetBrains Mono", Consolas, monospace',
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            wordWrap: 'on',
            automaticLayout: true,
            padding: { top: 12, bottom: 12 },
          }}
          onChange={(val) => setCurrentCode(val || '')}
        />
      </div>

      {/* Traceback error display if any */}
      {error && (
        <div className="p-3 bg-google-red-subtle/50 dark:bg-google-red/10 border-t border-google-red/30 text-google-red text-xs font-mono max-h-36 overflow-auto">
          <div className="flex items-center gap-1.5 font-semibold font-sans mb-1">
            <AlertCircle size={14} />
            <span>Execution Traceback</span>
          </div>
          <pre className="whitespace-pre-wrap">{error}</pre>
        </div>
      )}
    </div>
  );
};

