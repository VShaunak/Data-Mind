import React, { useState } from 'react';
import { FileText, Copy, Check, Download } from 'lucide-react';

interface AnalyticalReportPanelProps {
  reportMarkdown?: string;
  metrics?: Record<string, any>;
}

export const AnalyticalReportPanel: React.FC<AnalyticalReportPanelProps> = ({
  reportMarkdown,
  metrics,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (!reportMarkdown) return;
    navigator.clipboard.writeText(reportMarkdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExportMarkdown = () => {
    if (!reportMarkdown) return;
    const blob = new Blob([reportMarkdown], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'datamind_analytical_report.md';
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!reportMarkdown) {
    return (
      <div className="flex flex-col items-center justify-center h-full min-h-[350px] bg-google-bg dark:bg-google-dark-bg border border-google-border dark:border-google-dark-border rounded-xl p-8 text-center text-google-muted dark:text-google-dark-muted">
        <FileText size={36} className="text-google-subtle dark:text-google-dark-muted mb-2 opacity-60" />
        <p className="text-xs font-medium">No analytical report ready yet.</p>
        <p className="text-[11px] mt-1">Mathematical reports with computed statistics appear here once execution completes.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-google-bg dark:bg-google-dark-bg border border-google-border dark:border-google-dark-border rounded-xl overflow-hidden shadow-subtle">
      {/* Report Header */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-google-secondary dark:bg-google-dark-secondary border-b border-google-border dark:border-google-dark-border select-none">
        <div className="flex items-center gap-2">
          <FileText size={15} className="text-google-blue" />
          <span className="text-xs font-semibold text-google-text dark:text-google-dark-text">
            Evidence-Grounded Analytical Report
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 px-2 py-1 text-[11px] rounded bg-google-bg dark:bg-google-dark-bg border border-google-border dark:border-google-dark-border text-google-text dark:text-google-dark-text hover:bg-google-surface transition-colors"
            title="Copy markdown report"
          >
            {copied ? <Check size={12} className="text-google-green" /> : <Copy size={12} />}
            <span>{copied ? 'Copied' : 'Copy'}</span>
          </button>

          <button
            onClick={handleExportMarkdown}
            className="flex items-center gap-1 px-2 py-1 text-[11px] rounded bg-google-bg dark:bg-google-dark-bg border border-google-border dark:border-google-dark-border text-google-text dark:text-google-dark-text hover:bg-google-surface transition-colors"
            title="Download report as Markdown file"
          >
            <Download size={12} />
            <span>Export MD</span>
          </button>
        </div>
      </div>

      {/* Rendered Markdown Body */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 text-xs leading-relaxed text-google-text dark:text-google-dark-text selection:bg-google-blue-subtle">
        {/* Render clean styled markdown */}
        <div className="prose prose-sm dark:prose-invert max-w-none space-y-4">
          {reportMarkdown.split('\n\n').map((block, idx) => {
            if (block.startsWith('# ')) {
              return (
                <h2 key={idx} className="text-base font-semibold text-google-text dark:text-google-dark-text border-b border-google-border dark:border-google-dark-border pb-1.5 mt-6 first:mt-0">
                  {block.replace('# ', '')}
                </h2>
              );
            }
            if (block.startsWith('## ')) {
              return (
                <h3 key={idx} className="text-sm font-semibold text-google-text dark:text-google-dark-text mt-4">
                  {block.replace('## ', '')}
                </h3>
              );
            }
            if (block.startsWith('|')) {
              // Markdown Table rendering
              const rows = block.trim().split('\n');
              const headers = rows[0]?.split('|').filter(c => c.trim().length > 0) || [];
              const bodyRows = rows.slice(2);

              return (
                <div key={idx} className="overflow-x-auto my-3 border border-google-border dark:border-google-dark-border rounded-lg">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="bg-google-surface dark:bg-google-dark-surface border-b border-google-border dark:border-google-dark-border">
                        {headers.map((h, i) => (
                          <th key={i} className="px-3 py-2 font-medium text-google-text dark:text-google-dark-text">
                            {h.trim()}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-google-border dark:divide-google-dark-border font-mono text-[11px]">
                      {bodyRows.map((r, rIdx) => {
                        const cells = r.split('|').filter(c => c.trim().length > 0);
                        return (
                          <tr key={rIdx} className="hover:bg-google-surface/50">
                            {cells.map((cell, cIdx) => (
                              <td key={cIdx} className="px-3 py-1.5">
                                {cell.trim().replace(/`/g, '')}
                              </td>
                            ))}
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              );
            }
            if (block.startsWith('- ')) {
              return (
                <ul key={idx} className="list-disc pl-5 space-y-1">
                  {block.split('\n').map((item, itemIdx) => (
                    <li key={itemIdx} className="text-google-text dark:text-google-dark-text">
                      {item.replace('- ', '')}
                    </li>
                  ))}
                </ul>
              );
            }
            return (
              <p key={idx} className="text-google-text dark:text-google-dark-text">
                {block}
              </p>
            );
          })}
        </div>
      </div>
    </div>
  );
};

