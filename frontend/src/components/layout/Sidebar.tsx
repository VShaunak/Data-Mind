import React from 'react';
import {
  Plus,
  MessageSquare,
  Database,
  FileText,
  Cpu,
  Activity,
  Trash2,
  ChevronLeft,
  ChevronRight,
  FolderArchive,
  Power,
} from 'lucide-react';
import { Session } from '../../types';

interface SidebarProps {
  sessions: Session[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewSession: () => void;
  onDeleteSession: (id: string) => void;
  onOpenModelSettings: () => void;
  onOpenDiagnostics: () => void;
  onExitApplication?: () => void;
  activeProvider?: string;
  activeModel?: string;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewSession,
  onDeleteSession,
  onOpenModelSettings,
  onOpenDiagnostics,
  onExitApplication,
  activeProvider = 'ollama',
  activeModel = 'llama3:8b',
  isCollapsed,
  onToggleCollapse,
}) => {
  return (
    <aside
      className={`h-screen flex flex-col border-r transition-all duration-200 select-none bg-google-secondary dark:bg-google-dark-secondary border-google-border dark:border-google-dark-border ${
        isCollapsed ? 'w-16' : 'w-72'
      }`}
    >
      {/* App Identity Header */}
      <div className="flex items-center justify-between p-4 border-b border-google-border dark:border-google-dark-border">
        {!isCollapsed && (
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="w-8 h-8 rounded-lg bg-google-blue flex items-center justify-center text-white font-semibold text-sm shadow-subtle shrink-0">
              DM
            </div>
            <div className="truncate">
              <h1 className="text-sm font-semibold tracking-tight text-google-text dark:text-google-dark-text">
                Data Mind
              </h1>
              <p className="text-[11px] text-google-muted dark:text-google-dark-muted truncate">
                Think Data. Discover Intelligence.
              </p>
            </div>
          </div>
        )}

        {isCollapsed && (
          <div className="mx-auto w-8 h-8 rounded-lg bg-google-blue flex items-center justify-center text-white font-semibold text-sm shadow-subtle">
            DM
          </div>
        )}

        <button
          onClick={onToggleCollapse}
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          className="p-1 rounded-md text-google-muted hover:text-google-text hover:bg-google-surface dark:text-google-dark-muted dark:hover:text-google-dark-text dark:hover:bg-google-dark-surface transition-colors"
        >
          {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>

      {/* New Analysis Action */}
      <div className="p-3">
        <button
          onClick={onNewSession}
          className={`w-full flex items-center justify-center gap-2 py-2 px-3 rounded-full bg-google-bg dark:bg-google-dark-surface text-google-blue border border-google-border dark:border-google-dark-border hover:border-google-blue hover:shadow-subtle transition-all text-xs font-medium ${
            isCollapsed ? 'px-0' : ''
          }`}
          title="New Analysis"
        >
          <Plus size={16} className="text-google-blue" />
          {!isCollapsed && <span>New Analysis</span>}
        </button>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto px-2 py-1 space-y-0.5">
        {!isCollapsed && (
          <div className="px-2 py-1.5 text-[11px] font-medium text-google-subtle dark:text-google-dark-muted uppercase tracking-wider">
            Recent Analyses
          </div>
        )}

        {sessions.length === 0 && !isCollapsed && (
          <div className="px-3 py-6 text-center text-xs text-google-muted dark:text-google-dark-muted">
            No previous sessions. Start by creating a new analysis!
          </div>
        )}

        {sessions.map((sess) => {
          const isActive = sess.id === activeSessionId;
          return (
            <div
              key={sess.id}
              onClick={() => onSelectSession(sess.id)}
              className={`group flex items-center justify-between px-2.5 py-2 rounded-lg cursor-pointer text-xs transition-colors ${
                isActive
                  ? 'bg-google-blue-subtle text-google-blue dark:bg-google-blue-darkSubtle dark:text-google-blue font-medium'
                  : 'text-google-text dark:text-google-dark-text hover:bg-google-surface dark:hover:bg-google-dark-surface'
              }`}
              title={sess.title}
            >
              <div className="flex items-center gap-2 truncate">
                <MessageSquare size={14} className="shrink-0 opacity-70" />
                {!isCollapsed && (
                  <span className="truncate">{sess.title || 'Untitled Analysis'}</span>
                )}
              </div>

              {!isCollapsed && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(sess.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 rounded hover:text-google-red transition-opacity"
                  title="Delete session"
                >
                  <Trash2 size={13} />
                </button>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer Navigation: Model Settings & Diagnostics */}
      <div className="p-2 border-t border-google-border dark:border-google-dark-border space-y-0.5">
        <button
          onClick={onOpenModelSettings}
          className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-xs text-google-text dark:text-google-dark-text hover:bg-google-surface dark:hover:bg-google-dark-surface transition-colors"
          title="Local Model Settings"
        >
          <Cpu size={15} className="text-google-muted dark:text-google-dark-muted shrink-0" />
          {!isCollapsed && (
            <div className="truncate text-left">
              <div className="font-medium">Model Settings</div>
              <div className="text-[10px] text-google-muted dark:text-google-dark-muted truncate">
                {activeProvider} / {activeModel}
              </div>
            </div>
          )}
        </button>

        <button
          onClick={onOpenDiagnostics}
          className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-xs text-google-text dark:text-google-dark-text hover:bg-google-surface dark:hover:bg-google-dark-surface transition-colors"
          title="Diagnostics & Sandbox"
        >
          <Activity size={15} className="text-google-muted dark:text-google-dark-muted shrink-0" />
          {!isCollapsed && <span>System Diagnostics</span>}
        </button>

        {onExitApplication && (
          <button
            onClick={onExitApplication}
            className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-xs text-google-red hover:bg-google-red-subtle/50 dark:hover:bg-google-red/10 transition-colors"
            title="Exit Data Mind and shutdown"
          >
            <Power size={15} className="shrink-0 text-google-red" />
            {!isCollapsed && <span className="font-medium">Exit Application</span>}
          </button>
        )}
      </div>
    </aside>
  );
};

