import { useEffect, useRef, useState } from "react";
import { getRecording } from "@/api/client";
import type { Recording } from "@/types/recording";

const POLL_INTERVAL_MS = 2000;
const TERMINAL_STATUSES = new Set(["ready", "failed"]);

/**
 * Polls GET /recordings/{id} on an interval until the recording reaches
 * a terminal status (ready or failed), then stops. This is what makes
 * the YouTube ingestion job (which runs asynchronously on the Celery
 * worker — see worker/tasks/ingest.py) visible in the UI: the backend
 * doesn't push updates, so the frontend has to ask.
 */
export function useRecordingPolling(recordingId: string | null) {
  const [recording, setRecording] = useState<Recording | null>(null);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!recordingId) {
      setRecording(null);
      return;
    }

    let cancelled = false;

    const poll = async () => {
      try {
        const result = await getRecording(recordingId);
        if (cancelled) return;

        setRecording(result);
        setError(null);

        if (TERMINAL_STATUSES.has(result.status) && intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : "Failed to fetch recording status");
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      }
    };

    poll(); // fetch immediately, don't wait for the first interval tick
    intervalRef.current = setInterval(poll, POLL_INTERVAL_MS);

    return () => {
      cancelled = true;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [recordingId]);

  const isPolling =
    recording !== null && !TERMINAL_STATUSES.has(recording.status) && !error;

  return { recording, isPolling, error };
}
