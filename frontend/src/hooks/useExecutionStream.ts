import { useState, useEffect, useRef } from 'react';
import { ExecutionEvent } from '../types';

export function useExecutionStream(sessionId: string | null, onTaskComplete?: () => void) {
  const [events, setEvents] = useState<ExecutionEvent[]>([]);
  const [currentStage, setCurrentStage] = useState<string>('');
  const [isExecuting, setIsExecuting] = useState<boolean>(false);
  const [latestCode, setLatestCode] = useState<string>('');
  const [latestError, setLatestError] = useState<string | null>(null);
  const [correctionAttempts, setCorrectionAttempts] = useState<number>(1);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!sessionId) {
      setEvents([]);
      setCurrentStage('');
      setIsExecuting(false);
      return;
    }

    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const es = new EventSource(`/api/events/stream/${sessionId}`);
    eventSourceRef.current = es;

    es.addEventListener('agent_event', (e: MessageEvent) => {
      try {
        const ev: ExecutionEvent = JSON.parse(e.data);
        setEvents(prev => [...prev, ev]);
        setCurrentStage(ev.stage);

        if (ev.status === 'running') {
          setIsExecuting(true);
        }

        if (ev.stage === 'CODE_GENERATION' && ev.metadata?.code) {
          setLatestCode(ev.metadata.code);
        }

        if (ev.stage === 'ERROR_RECOVERY' && ev.metadata?.attempt) {
          setCorrectionAttempts(ev.metadata.attempt);
        }

        if (ev.status === 'failed') {
          setLatestError(ev.message || 'Execution error');
        }

        if (ev.stage === 'COMPLETED' || (ev.stage === 'FAILED' && ev.status !== 'running')) {
          setIsExecuting(false);
          if (onTaskComplete) {
            onTaskComplete();
          }
        }
      } catch (err) {
        console.error('Failed to parse SSE event', err);
      }
    });

    es.onerror = () => {
      // EventSource will automatically retry in case of disconnect
    };

    return () => {
      es.close();
    };
  }, [sessionId]);

  const clearStream = () => {
    setEvents([]);
    setCurrentStage('');
    setIsExecuting(false);
    setLatestError(null);
  };

  return {
    events,
    currentStage,
    isExecuting,
    latestCode,
    latestError,
    correctionAttempts,
    clearStream,
  };
}

