import { useCallback, useEffect, useRef, useState } from "react";
import { finishPracticeSession, startPracticeSession } from "@/api/client";
import type { PracticeSession } from "@/types/practiceSession";

/**
 * The displayed clock is purely for feedback while a session is
 * running — the actual duration saved to the database is always
 * computed server-side from started_at to ended_at (see
 * app/services/practice_session_service.py), never from this client
 * timer. That's deliberate: a client-reported duration could be
 * tampered with or drift if the tab is backgrounded, so the server
 * stays the source of truth.
 *
 * There's no pause/resume here — the schema only tracks a single
 * started_at/ended_at pair. Rather than fake a pause that doesn't
 * actually stop the server-side clock, this only offers Start/Finish.
 */
export function usePracticeTimer(userId: string, pieceId: string) {
  const [session, setSession] = useState<PracticeSession | null>(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [starting, setStarting] = useState(false);
  const [finishing, setFinishing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  const start = useCallback(
    async (opts?: { focus_section?: string; session_goal?: string; target_tempo_bpm?: number }) => {
      setError(null);
      setStarting(true);
      try {
        const created = await startPracticeSession({ user_id: userId, piece_id: pieceId, ...opts });
        setSession(created);
        setElapsedSeconds(0);
        const startedAtMs = new Date(created.started_at).getTime();
        intervalRef.current = setInterval(() => {
          setElapsedSeconds(Math.floor((Date.now() - startedAtMs) / 1000));
        }, 1000);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to start session");
      } finally {
        setStarting(false);
      }
    },
    [userId, pieceId]
  );

  const finish = useCallback(
    async (opts?: { reflection_notes?: string; self_rating?: number }) => {
      if (!session) return null;
      setFinishing(true);
      setError(null);
      try {
        const finished = await finishPracticeSession(session.id, opts ?? {});
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
        setSession(null);
        return finished;
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to finish session");
        return null;
      } finally {
        setFinishing(false);
      }
    },
    [session]
  );

  return { session, elapsedSeconds, starting, finishing, error, start, finish };
}
