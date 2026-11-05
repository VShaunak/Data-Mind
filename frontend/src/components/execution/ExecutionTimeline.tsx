import React from 'react';
import {
  CheckCircle2,
  Circle,
  Loader2,
  AlertCircle,
  RotateCcw,
  Square,
} from 'lucide-react';
import { ExecutionEvent } from '../../types';

interface ExecutionTimelineProps {
  currentStage: string;
  isExecuting: boolean;
  events: ExecutionEvent[];
  correctionAttempts: number;
  error?: string | null;
  onCancelTask?: () => void;
}

interface StepDef {
  id: string;
  label: string;
  aliases: string[];
}

const STAGES: StepDef[] = [
  { id: 'UNDERSTANDING_REQUEST', label: 'Understanding request', aliases: ['STARTING_ENGINE', 'UNDERSTANDING_REQUEST'] },
  { id: 'SCHEMA_INTROSPECTION', label: 'Inspecting dataset', aliases: ['DATASET_VALIDATION', 'SCHEMA_INTROSPECTION', 'PROFILING_DATASET'] },
  { id: 'ANALYSIS_PLANNING', label: 'Planning analysis', aliases: ['ANALYSIS_PLANNING'] },
  { id: 'CODE_GENERATION', label: 'Generating Python code', aliases: ['CODE_GENERATION'] },
  { id: 'CODE_VALIDATION', label: 'Validating code & guardrails', aliases: ['CODE_VALIDATION'] },
  { id: 'SANDBOX_EXECUTION', label: 'Executing sandbox container', aliases: ['SANDBOX_EXECUTION', 'EXECUTION_EVALUATION'] },
  { id: 'VISUALIZATION_GENERATION', label: 'Creating visualizations', aliases: ['VISUALIZATION_GENERATION', 'GENERATING_CHART'] },
  { id: 'ANALYTICAL_SUMMARY', label: 'Preparing report & metrics', aliases: ['ANALYTICAL_SUMMARY', 'OUTPUT_VALIDATION', 'PERSIST_RESULTS'] },
  { id: 'COMPLETED', label: 'Completed', aliases: ['COMPLETED'] },
];

export const ExecutionTimeline: React.FC<ExecutionTimelineProps> = ({
  currentStage,
  isExecuting,
  events,
  correctionAttempts,
  error,
  onCancelTask,
}) => {
  // Find current active step index
  const getCurrentStepIndex = (): number => {
    if (!currentStage) return -1;
    for (let i = 0; i < STAGES.length; i++) {
      if (STAGES[i].aliases.includes(currentStage)) {
        return i;
      }
    }
    return -1;
  };

  const activeIndex = getCurrentStepIndex();
  const isFailed = currentStage === 'FAILED' || Boolean(error);
  const isDone = currentStage === 'COMPLETED';

  return (
    <div className="w-full bg-google-bg dark:bg-google-dark-bg border-b border-google-border dark:border-google-dark-border px-6 py-3.5 select-none transition-all">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-google-text dark:text-google-dark-text">
            Agent Execution Timeline
          </span>
          {isExecuting && (
            <div className="flex items-center gap-1.5">
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-google-blue-subtle text-google-blue">
                <Loader2 size={10} className="animate-spin" />
                Active
              </span>
              {onCancelTask && (
                <button
                  onClick={onCancelTask}
                  className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-medium text-google-red border border-google-red/40 hover:bg-google-red-subtle/50 transition-colors cursor-pointer"
                  title="Kill / Cancel this task"
                >
                  <Square size={8} fill="currentColor" />
                  <span>Kill Task</span>
                </button>
              )}
            </div>
          )}
          {isDone && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-google-green-subtle text-google-green">
              <CheckCircle2 size={10} />
              Completed
            </span>
          )}
          {correctionAttempts > 1 && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-google-amber-subtle text-google-amber">
              <RotateCcw size={10} />
              Self-Correction Attempt #{correctionAttempts}
            </span>
          )}
        </div>

        {/* Latest Event Message */}
        {events.length > 0 && (
          <div className="text-[11px] text-google-muted dark:text-google-dark-muted truncate max-w-md">
            {events[events.length - 1].message}
          </div>
        )}
      </div>

      {/* Steps Progression Bar */}
      <div className="flex items-center justify-between gap-1 overflow-x-auto pb-1">
        {STAGES.map((step, idx) => {
          const isCurrent = idx === activeIndex && isExecuting;
          const isPassed = activeIndex > idx || isDone;
          const isStepFailed = isFailed && idx === activeIndex;

          return (
            <div key={step.id} className="flex items-center gap-1 shrink-0">
              <div className="flex items-center gap-1.5">
                {isPassed ? (
                  <CheckCircle2 size={14} className="text-google-green shrink-0" />
                ) : isCurrent ? (
                  <Loader2 size={14} className="text-google-blue animate-spin shrink-0" />
                ) : isStepFailed ? (
                  <AlertCircle size={14} className="text-google-red shrink-0" />
                ) : (
                  <Circle size={14} className="text-google-border dark:text-google-dark-border shrink-0" />
                )}

                <span
                  className={`text-[11px] whitespace-nowrap transition-colors ${
                    isCurrent
                      ? 'font-semibold text-google-blue'
                      : isPassed
                      ? 'font-medium text-google-text dark:text-google-dark-text'
                      : isStepFailed
                      ? 'font-medium text-google-red'
                      : 'text-google-muted/70 dark:text-google-dark-muted/70'
                  }`}
                >
                  {step.label}
                </span>
              </div>

              {idx < STAGES.length - 1 && (
                <div
                  className={`w-4 h-[1px] mx-1 transition-colors ${
                    isPassed ? 'bg-google-green/60' : 'bg-google-border dark:bg-google-dark-border'
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

