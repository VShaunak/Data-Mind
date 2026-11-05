import React, { useState } from 'react';
import { X, Table, Hash, Calendar, Type, AlertCircle } from 'lucide-react';
import { DatasetProfile } from '../../types';

interface DatasetPreviewModalProps {
  profile: DatasetProfile | null;
  isOpen: boolean;
  onClose: () => void;
}

export const DatasetPreviewModal: React.FC<DatasetPreviewModalProps> = ({ profile, isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<'sample' | 'schema' | 'stats'>('sample');

  if (!isOpen || !profile) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4 animate-in fade-in duration-150">
      <div className="bg-google-bg dark:bg-google-dark-bg border border-google-border dark:border-google-dark-border w-full max-w-4xl max-h-[85vh] rounded-xl shadow-modal flex flex-col overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-google-border dark:border-google-dark-border">
          <div>
            <h3 className="text-sm font-semibold text-google-text dark:text-google-dark-text">
              Dataset Profile: {profile.file_name}
            </h3>
            <p className="text-xs text-google-muted dark:text-google-dark-muted mt-0.5">
              {profile.row_count} rows • {profile.column_count} columns • {profile.memory_usage} • {profile.duplicate_rows} duplicate rows
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-google-muted hover:text-google-text dark:hover:text-google-dark-text hover:bg-google-surface dark:hover:bg-google-dark-surface transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Tab Controls */}
        <div className="flex border-b border-google-border dark:border-google-dark-border px-6 gap-6 text-xs font-medium">
          <button
            onClick={() => setActiveTab('sample')}
            className={`py-2.5 border-b-2 transition-colors ${
              activeTab === 'sample'
                ? 'border-google-blue text-google-blue font-semibold'
                : 'border-transparent text-google-muted hover:text-google-text dark:hover:text-google-dark-text'
            }`}
          >
            Sample Rows ({profile.sample_data?.length || 0})
          </button>
          <button
            onClick={() => setActiveTab('schema')}
            className={`py-2.5 border-b-2 transition-colors ${
              activeTab === 'schema'
                ? 'border-google-blue text-google-blue font-semibold'
                : 'border-transparent text-google-muted hover:text-google-text dark:hover:text-google-dark-text'
            }`}
          >
            Columns & Data Types ({profile.columns?.length || 0})
          </button>
          <button
            onClick={() => setActiveTab('stats')}
            className={`py-2.5 border-b-2 transition-colors ${
              activeTab === 'stats'
                ? 'border-google-blue text-google-blue font-semibold'
                : 'border-transparent text-google-muted hover:text-google-text dark:hover:text-google-dark-text'
            }`}
          >
            Statistical Summaries
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-auto p-6">
          {activeTab === 'sample' && (
            <div className="border border-google-border dark:border-google-dark-border rounded-lg overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-google-surface dark:bg-google-dark-surface border-b border-google-border dark:border-google-dark-border">
                    {profile.columns.map((col) => (
                      <th key={col.name} className="px-3 py-2 font-medium text-google-text dark:text-google-dark-text whitespace-nowrap">
                        {col.name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-google-border dark:divide-google-dark-border">
                  {profile.sample_data.map((row, idx) => (
                    <tr key={idx} className="hover:bg-google-surface/50 dark:hover:bg-google-dark-surface/50">
                      {profile.columns.map((col) => (
                        <td key={col.name} className="px-3 py-2 text-google-text dark:text-google-dark-text font-mono text-[11px] whitespace-nowrap">
                          {row[col.name] !== undefined && row[col.name] !== null ? String(row[col.name]) : <span className="text-google-muted italic">null</span>}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'schema' && (
            <div className="space-y-2">
              <div className="grid grid-cols-4 px-3 py-2 text-[11px] font-medium text-google-muted uppercase border-b border-google-border dark:border-google-dark-border">
                <span>Column Name</span>
                <span>Type Category</span>
                <span>Data Type</span>
                <span>Nulls / Missing</span>
              </div>
              {profile.columns.map((col) => (
                <div key={col.name} className="grid grid-cols-4 px-3 py-2 rounded-lg text-xs items-center hover:bg-google-surface dark:hover:bg-google-dark-surface">
                  <span className="font-medium text-google-text dark:text-google-dark-text truncate">{col.name}</span>
                  <span className="capitalize text-google-blue font-mono text-[11px]">{col.type_category || 'General'}</span>
                  <span className="font-mono text-[11px] text-google-muted dark:text-google-dark-muted">{col.dtype}</span>
                  <span className="text-google-text dark:text-google-dark-text font-mono text-[11px]">
                    {col.null_count} ({col.null_percentage}%)
                  </span>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'stats' && (
            <div className="space-y-4">
              <h4 className="text-xs font-semibold text-google-text dark:text-google-dark-text">Numerical Metrics</h4>
              <div className="border border-google-border dark:border-google-dark-border rounded-lg overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-google-surface dark:bg-google-dark-surface border-b border-google-border dark:border-google-dark-border">
                      <th className="px-3 py-2 font-medium">Metric</th>
                      <th className="px-3 py-2 font-medium">Mean</th>
                      <th className="px-3 py-2 font-medium">Std</th>
                      <th className="px-3 py-2 font-medium">Min</th>
                      <th className="px-3 py-2 font-medium">50% (Median)</th>
                      <th className="px-3 py-2 font-medium">Max</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-google-border dark:divide-google-dark-border font-mono text-[11px]">
                    {Object.entries(profile.numerical_summaries).map(([col, s]) => (
                      <tr key={col}>
                        <td className="px-3 py-2 font-medium font-sans">{col}</td>
                        <td className="px-3 py-2">{s.mean ?? '-'}</td>
                        <td className="px-3 py-2">{s.std ?? '-'}</td>
                        <td className="px-3 py-2">{s.min ?? '-'}</td>
                        <td className="px-3 py-2">{s['50%'] ?? '-'}</td>
                        <td className="px-3 py-2">{s.max ?? '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

