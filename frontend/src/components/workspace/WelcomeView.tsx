import React from 'react';
import { Sparkles, TrendingUp, BarChart3, Binary, Layers } from 'lucide-react';
import { DatasetUploader } from './DatasetUploader';
import { DatasetProfile } from '../../types';

interface WelcomeViewProps {
  sessionId?: string;
  onDatasetUploaded: (fileName: string, storedPath: string, profile: DatasetProfile) => void;
  onSelectPrompt: (prompt: string) => void;
}

export const WelcomeView: React.FC<WelcomeViewProps> = ({
  sessionId,
  onDatasetUploaded,
  onSelectPrompt,
}) => {
  const examplePrompts = [
    {
      title: 'Descriptive & Distribution Analysis',
      prompt: 'Profile the distribution of numeric columns, check skewness, and highlight key statistical properties.',
      icon: <BarChart3 size={15} className="text-google-blue" />,
    },
    {
      title: 'Correlation & Multicollinearity Matrix',
      prompt: 'Calculate Pearson and Spearman correlation matrices between all numerical variables and display a correlation heatmap.',
      icon: <Binary size={15} className="text-google-green" />,
    },
    {
      title: 'Segment Comparison & Grouping',
      prompt: 'Group by the primary category and compare averages, medians, and interquartile ranges using a clean box plot.',
      icon: <Layers size={15} className="text-google-amber" />,
    },
    {
      title: 'Anomaly & Outlier Detection',
      prompt: 'Apply IQR and Z-score statistical tests to identify outliers, and report observations with mathematical grounds.',
      icon: <TrendingUp size={15} className="text-google-red" />,
    },
  ];

  return (
    <div className="flex-1 overflow-y-auto flex flex-col items-center justify-center p-8 max-w-4xl mx-auto w-full select-none">
      {/* Title & Tagline */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs bg-google-surface dark:bg-google-dark-surface border border-google-border dark:border-google-dark-border text-google-muted dark:text-google-dark-muted mb-4 font-medium">
          <Sparkles size={13} className="text-google-blue" />
          <span>Local Open-Source AI Data Workstation</span>
        </div>
        <h2 className="text-2xl font-semibold tracking-tight text-google-text dark:text-google-dark-text">
          Think Data. Discover Intelligence.
        </h2>
        <p className="text-xs text-google-muted dark:text-google-dark-muted mt-2 max-w-lg mx-auto">
          Attach a dataset and describe your analytical question in natural language. Data Mind will autonomously inspect the schema, formulate an execution plan, generate Python code, execute securely, and deliver mathematical findings.
        </p>
      </div>

      {/* Dataset Dropzone */}
      <div className="w-full max-w-2xl mb-8">
        <DatasetUploader sessionId={sessionId} onUploaded={onDatasetUploaded} />
      </div>

      {/* Suggested Analysis Starters */}
      <div className="w-full max-w-2xl">
        <h4 className="text-xs font-semibold text-google-muted uppercase tracking-wider mb-3">
          Suggested Analytical Workflows
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
          {examplePrompts.map((item, idx) => (
            <button
              key={idx}
              onClick={() => onSelectPrompt(item.prompt)}
              className="text-left p-3.5 rounded-xl border border-google-border dark:border-google-dark-border bg-google-bg dark:bg-google-dark-surface hover:border-google-blue hover:shadow-subtle transition-all flex flex-col justify-between group"
            >
              <div className="flex items-center gap-2 mb-1.5">
                {item.icon}
                <span className="text-xs font-semibold text-google-text dark:text-google-dark-text group-hover:text-google-blue transition-colors">
                  {item.title}
                </span>
              </div>
              <p className="text-[11px] text-google-muted dark:text-google-dark-muted line-clamp-2">
                {item.prompt}
              </p>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

