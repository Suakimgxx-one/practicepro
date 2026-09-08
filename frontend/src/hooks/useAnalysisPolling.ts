import { useEffect, useRef, useState } from "react";
import { getAnalysisSession } from "@/api/client";
import type { AnalysisSession } from "@/types/analysis";

const POLL_INTERVAL_MS = 2000;
const TERMINAL_STATUSES = new Set(["complete", "failed"]);

/**
 * Polls GET /analysis-sessions/{id} until the session reaches a
 * terminal status. The pipeline (worker/tasks/analyze.py) moves the
 * session through pending -> aligning -> analyzing -> complete/failed
 * — this surfaces that progression in the UI the same way
 * useRecordingPolling surfaces YouTube ingestion progress.
 */
export function useAnalysisPolling(sessionId: string | null) {
  const [session, setSession] = useState<AnalysisSession | null>(null);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!sessionId) {
      setSession(null);
      return;
    }

    let cancelled = false;

    const poll = async () => {
      try {
        const result = await getAnalysisSession(sessionId);
        if (cancelled) return;
        setSession(result);
        setError(null);
        if (TERMINAL_STATUSES.has(result.status) && intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : "Failed to fetch analysis status");
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      }
    };

    poll();
    intervalRef.current = setInterval(poll, POLL_INTERVAL_MS);

    return () => {
      cancelled = true;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [sessionId]);

  const isPolling = session !== null && !TERMINAL_STATUSES.has(session.status) && !error;
  return { session, isPolling, error };
}
