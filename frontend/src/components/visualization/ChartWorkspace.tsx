import React, { useState, useEffect, useRef } from 'react';
import { BarChart, Maximize2, Minimize2, Download, Image as ImageIcon, FileCode2 } from 'lucide-react';
import { Theme } from '../../hooks/useTheme';

interface ChartWorkspaceProps {
  chartJson: any;
  theme: Theme;
}

export const ChartWorkspace: React.FC<ChartWorkspaceProps> = ({ chartJson, theme }) => {
  const [isFullScreen, setIsFullScreen] = useState(false);
  const chartContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let isMounted = true;

    const renderChart = async () => {
      if (!chartContainerRef.current || !chartJson) return;

      try {
        const Plotly = (await import('plotly.js-dist-min')).default;
        if (!isMounted || !chartContainerRef.current) return;

        const data = chartJson.data || [];
        const layout = {
          ...chartJson.layout,
          autosize: true,
          paper_bgcolor: theme === 'dark' ? '#202124' : '#FFFFFF',
          plot_bgcolor: theme === 'dark' ? '#202124' : '#FFFFFF',
          font: {
            family: 'Inter, Roboto, sans-serif',
            color: theme === 'dark' ? '#E8EAED' : '#202124',
            size: 11,
            ...(chartJson.layout?.font || {}),
          },
          margin: chartJson.layout?.margin || { l: 140, r: 50, t: 80, b: 60 },
        };

        const config = {
          responsive: true,
          displayModeBar: true,
          displaylogo: false,
          toImageButtonOptions: {
            format: 'png',
            filename: 'datamind_chart_300dpi',
            height: 900,
            width: 1440,
            scale: 2,
          },
          modeBarButtonsToRemove: ['lasso2d'],
        };

        Plotly.newPlot(chartContainerRef.current, data, layout, config);
      } catch (err) {
        console.error('Failed to render Plotly chart', err);
      }
    };

    renderChart();

    return () => {
      isMounted = false;
    };
  }, [chartJson, theme]);

  const handleDownloadPng = async () => {
    if (!chartContainerRef.current) return;
    try {
      const Plotly = (await import('plotly.js-dist-min')).default;
      Plotly.downloadImage(chartContainerRef.current, {
        format: 'png',
        filename: 'datamind_highres_chart',
        width: 1920,
        height: 1080,
      });
    } catch (err) {
      console.error('Failed to export PNG', err);
    }
  };

  const handleDownloadSvg = async () => {
    if (!chartContainerRef.current) return;
    try {
      const Plotly = (await import('plotly.js-dist-min')).default;
      Plotly.downloadImage(chartContainerRef.current, {
        format: 'svg',
        filename: 'datamind_vector_chart',
        width: 1920,
        height: 1080,
      });
    } catch (err) {
      console.error('Failed to export SVG', err);
    }
  };

  const handleExportJson = () => {
    if (!chartJson) return;
    const blob = new Blob([JSON.stringify(chartJson, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'datamind_chart.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!chartJson) {
    return (
      <div className="flex flex-col items-center justify-center h-full min-h-[350px] bg-google-bg dark:bg-google-dark-bg border border-google-border dark:border-google-dark-border rounded-xl p-8 text-center text-google-muted dark:text-google-dark-muted">
        <BarChart size={36} className="text-google-subtle dark:text-google-dark-muted mb-2 opacity-60" />
        <p className="text-xs font-medium">No visualization generated yet.</p>
        <p className="text-[11px] mt-1">Start an analysis to generate an interactive Plotly chart.</p>
      </div>
    );
  }

  return (
    <div
      className={`flex flex-col bg-google-bg dark:bg-google-dark-bg border border-google-border dark:border-google-dark-border rounded-xl overflow-hidden shadow-subtle ${
        isFullScreen ? 'fixed inset-4 z-50' : 'h-full min-h-[420px]'
      }`}
    >
      {/* Chart Workspace Header */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-google-secondary dark:bg-google-dark-secondary border-b border-google-border dark:border-google-dark-border select-none">
        <div className="flex items-center gap-2">
          <BarChart size={15} className="text-google-blue" />
          <span className="text-xs font-semibold text-google-text dark:text-google-dark-text">
            Publication-Quality Visualization
          </span>
        </div>

        <div className="flex items-center gap-1.5">
          <button
            onClick={handleDownloadPng}
            className="flex items-center gap-1 px-2.5 py-1 text-[11px] font-medium rounded bg-google-bg dark:bg-google-dark-bg border border-google-border dark:border-google-dark-border text-google-text dark:text-google-dark-text hover:border-google-blue hover:text-google-blue transition-colors"
            title="Download 300 DPI high-resolution PNG image"
          >
            <ImageIcon size={12} className="text-google-blue" />
            <span>Download PNG</span>
          </button>

          <button
            onClick={handleDownloadSvg}
            className="flex items-center gap-1 px-2.5 py-1 text-[11px] font-medium rounded bg-google-bg dark:bg-google-dark-bg border border-google-border dark:border-google-dark-border text-google-text dark:text-google-dark-text hover:border-google-blue hover:text-google-blue transition-colors"
            title="Download vector SVG graphic"
          >
            <FileCode2 size={12} className="text-google-green" />
            <span>Download SVG</span>
          </button>

          <button
            onClick={handleExportJson}
            className="flex items-center gap-1 px-2.5 py-1 text-[11px] rounded bg-google-bg dark:bg-google-dark-bg border border-google-border dark:border-google-dark-border text-google-text dark:text-google-dark-text hover:bg-google-surface transition-colors"
            title="Export serialized Plotly JSON"
          >
            <Download size={12} />
            <span>JSON</span>
          </button>

          <button
            onClick={() => setIsFullScreen(!isFullScreen)}
            className="p-1 rounded text-google-muted hover:text-google-text dark:hover:text-google-dark-text hover:bg-google-surface transition-colors ml-1"
            title={isFullScreen ? 'Exit full screen' : 'Full screen view'}
          >
            {isFullScreen ? <Minimize2 size={15} /> : <Maximize2 size={15} />}
          </button>
        </div>
      </div>

      {/* Interactive Chart Canvas */}
      <div ref={chartContainerRef} className="flex-1 w-full min-h-[380px]" />
    </div>
  );
};

