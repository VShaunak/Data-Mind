import React from 'react';
import { Sun, Moon, Database, Cpu, CheckCircle2, AlertCircle } from 'lucide-react';
import { Theme } from '../../hooks/useTheme';
import { DatasetProfile } from '../../types';

interface HeaderProps {
  sessionTitle: string;
  datasetName?: string;
  datasetProfile?: DatasetProfile;
  onOpenDatasetPreview?: () => void;
  activeProvider: string;
  activeModel: string;
  onOpenModelSettings: () => void;
  theme: Theme;
  onToggleTheme: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  sessionTitle,
  datasetName,
  datasetProfile,
  onOpenDatasetPreview,
  activeProvider,
  activeModel,
  onOpenModelSettings,
  theme,
  onToggleTheme,
}) => {
  return (
    <header className="h-14 border-b px-6 flex items-center justify-between select-none bg-google-bg dark:bg-google-dark-bg border-google-border dark:border-google-dark-border">
      {/* Session Title & Dataset Chip */}
      <div className="flex items-center gap-3">
        <h2 className="text-sm font-semibold text-google-text dark:text-google-dark-text max-w-sm truncate">
          {sessionTitle || 'New Analysis Session'}
        </h2>

        {datasetName && (
          <button
            onClick={onOpenDatasetPreview}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs bg-google-surface dark:bg-google-dark-surface border border-google-border dark:border-google-dark-border hover:border-google-blue transition-colors text-google-text dark:text-google-dark-text"
            title="Inspect dataset schema & sample rows"
          >
            <Database size={13} className="text-google-blue shrink-0" />
            <span className="truncate max-w-[140px] font-medium">{datasetName}</span>
            {datasetProfile && (
              <span className="text-[10px] text-google-muted dark:text-google-dark-muted">
                ({datasetProfile.row_count} rows, {datasetProfile.column_count} cols)
              </span>
            )}
          </button>
        )}
      </div>

      {/* Right Action Icons: Active Model & Theme Toggle */}
      <div className="flex items-center gap-2.5">
        {/* Model Badge */}
        <button
          onClick={onOpenModelSettings}
          className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs bg-google-surface dark:bg-google-dark-surface border border-google-border dark:border-google-dark-border hover:border-google-blue transition-colors text-google-text dark:text-google-dark-text"
          title="Current local model configuration"
        >
          <Cpu size={13} className="text-google-muted dark:text-google-dark-muted shrink-0" />
          <span className="text-[11px] font-medium text-google-muted dark:text-google-dark-muted uppercase">
            {activeProvider}:
          </span>
          <span className="font-medium truncate max-w-[120px]">{activeModel}</span>
        </button>

        {/* Theme Toggle */}
        <button
          onClick={onToggleTheme}
          className="p-2 rounded-lg text-google-muted hover:text-google-text hover:bg-google-surface dark:text-google-dark-muted dark:hover:text-google-dark-text dark:hover:bg-google-dark-surface transition-colors"
          title={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
        >
          {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
        </button>
      </div>
    </header>
  );
};

