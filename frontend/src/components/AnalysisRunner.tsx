import { useEffect, useRef, useState } from "react";
import { createAnalysisSession } from "@/api/client";
import { useAnalysisPolling } from "@/hooks/useAnalysisPolling";
import { AnalysisResults } from "@/components/AnalysisResults";
import type { AnalysisSession, SessionStatus } from "@/types/analysis";

interface AnalysisRunnerProps {
  userId: string;
  referenceRecordingId: string;
  studentRecordingId: string;
  onComplete?: (session: AnalysisSession) => void;
}

const PROGRESS_LABELS: Record<SessionStatus, string> = {
  pending: "Queued",
  aligning: "Aligning performances",
  analyzing: "Comparing pitch, rhythm, tempo, and dynamics",
  complete: "Complete",
  failed: "Failed",
};

export function AnalysisRunner({ userId, referenceRecordingId, studentRecordingId, onComplete }: AnalysisRunnerProps) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);
  const [startError, setStartError] = useState<string | null>(null);
  const { session, error: pollError } = useAnalysisPolling(sessionId);
  const hasNotifiedComplete = useRef(false);

  useEffect(() => {
    if (session?.status === "complete" && !hasNotifiedComplete.current) {
      hasNotifiedComplete.current = true;
      onComplete?.(session);
    }
  }, [session, onComplete]);

  const handleCompare = async () => {
    setStartError(null);
    setStarting(true);
    try {
      const created = await createAnalysisSession({ user_id: userId, reference_recording_id: referenceRecordingId, student_recording_id: studentRecordingId });
      setSessionId(created.id);
    } catch (err) {
      setStartError(err instanceof Error ? err.message : "Failed to start analysis");
    } finally {
      setStarting(false);
    }
  };

  if (!sessionId) {
    return (
      <div className="pt-6 border-t border-border-subtle">
        <button onClick={handleCompare} disabled={starting} className="bg-accent-500 hover:bg-accent-400 disabled:opacity-50 text-white text-sm font-medium px-5 py-2.5 rounded-lg shadow-glow transition-colors">
          {starting ? "Starting" : "Compare this attempt"}
        </button>
        {startError && <p className="text-danger text-sm mt-2">{startError}</p>}
      </div>
    );
  }

  if (session?.status === "failed") {
    return (
      <div className="pt-6 border-t border-border-subtle">
        <p className="text-sm text-danger">
          Analysis failed. This can happen if the recordings don't share enough overlapping content for alignment to work, or if a step in the pipeline hit an error.
        </p>
      </div>
    );
  }

  if (!session || session.status !== "complete") {
    const status = session?.status ?? "pending";
    return (
      <div className="pt-6 border-t border-border-subtle">
        <div className="flex items-center gap-2 text-sm text-ink-300">
          <span className="w-1.5 h-1.5 rounded-full bg-accent-500 animate-pulse" />
          {PROGRESS_LABELS[status]}
        </div>
        {pollError && <p className="text-danger text-sm mt-2">{pollError}</p>}
      </div>
    );
  }

  return (
    <div className="pt-2 border-t border-border-subtle">
      <AnalysisResults session={session} />
    </div>
  );
}
