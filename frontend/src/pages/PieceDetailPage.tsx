import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useUser } from "@/hooks/useUser";
import { usePieceDetail } from "@/hooks/usePieceDetail";
import { AppShell } from "@/components/AppShell";
import { EmailGate } from "@/components/EmailGate";
import { YoutubeReferenceInput } from "@/components/YoutubeReferenceInput";
import { RecordingUploader } from "@/components/RecordingUploader";
import { AnalysisRunner } from "@/components/AnalysisRunner";
import { ProgressChart } from "@/components/ProgressChart";
import { PracticeTimerWidget } from "@/components/PracticeTimerWidget";
import { formatDuration } from "@/lib/formatDuration";

export function PieceDetailPage() {
  const { pieceId } = useParams<{ pieceId: string }>();
  const { user, loading: userLoading, signIn } = useUser();
  const { piece, loading: pieceLoading, error, refetch } = usePieceDetail(pieceId ?? null);
  const [activeAttemptId, setActiveAttemptId] = useState<string | null>(null);

  if (userLoading || pieceLoading) {
    return (
      <div className="min-h-screen bg-surface-950 flex items-center justify-center">
        <p className="text-ink-500 text-sm">Loading</p>
      </div>
    );
  }
  if (!user) return <EmailGate onSubmit={signIn} />;

  if (error || !piece) {
    return (
      <AppShell user={user}>
        <div className="px-8 py-8 max-w-2xl">
          <Link to="/pieces" className="text-sm text-ink-500 hover:text-ink-300 transition-colors">← Your pieces</Link>
          <p className="text-danger text-sm mt-6">{error ?? "Piece not found."}</p>
        </div>
      </AppShell>
    );
  }

  const hasReference = piece.reference_recording !== null && piece.reference_recording.status === "ready";

  return (
    <AppShell user={user}>
      <div className="px-8 py-8 max-w-2xl">
        <Link to="/pieces" className="text-sm text-ink-500 hover:text-ink-300 transition-colors">← Your pieces</Link>

        <div className="flex items-baseline justify-between mt-4 mb-1">
          <h1 className="text-3xl font-semibold tracking-tight">{piece.title}</h1>
        </div>
        <div className="flex items-center gap-3 text-sm text-ink-500 mb-8">
          {piece.composer && <span>{piece.composer}</span>}
          {piece.total_practice_seconds > 0 && (
            <span>· {formatDuration(piece.total_practice_seconds)} practiced total</span>
          )}
        </div>

        {!hasReference ? (
          <div className="pb-8 border-b border-border-subtle">
            <p className="text-sm text-ink-500 mb-4">Add a reference performance to compare your practice against.</p>
            <YoutubeReferenceInput userId={user.id} pieceId={piece.id} onReady={() => refetch()} />
          </div>
        ) : (
          <>
            <div className="pb-8 border-b border-border-subtle">
              <PracticeTimerWidget userId={user.id} pieceId={piece.id} onSessionFinished={() => refetch()} />
            </div>

            <div className="py-8 border-b border-border-subtle">
              <RecordingUploader
                userId={user.id}
                pieceId={piece.id}
                label="Compare a new recording"
                onReady={setActiveAttemptId}
              />
              {activeAttemptId && piece.reference_recording && (
                <div className="mt-4">
                  <AnalysisRunner
                    userId={user.id}
                    referenceRecordingId={piece.reference_recording.id}
                    studentRecordingId={activeAttemptId}
                    onComplete={() => refetch()}
                  />
                </div>
              )}
            </div>

            <div className="py-8 border-b border-border-subtle">
              <div className="flex items-baseline justify-between mb-3">
                <h2 className="text-sm font-medium text-ink-300">Progress</h2>
                <span className="text-xs text-ink-500">
                  {piece.attempts.length} attempt{piece.attempts.length === 1 ? "" : "s"} logged
                </span>
              </div>
              <ProgressChart progress={piece.progress} />
            </div>

            {piece.practice_sessions.length > 0 && (
              <div className="py-8">
                <h2 className="text-sm font-medium text-ink-300 mb-3">Practice history</h2>
                <ul className="divide-y divide-border-subtle">
                  {piece.practice_sessions
                    .filter((s) => s.ended_at !== null)
                    .map((s) => (
                      <li key={s.id} className="py-3 text-sm">
                        <div className="flex items-center justify-between">
                          <span className="text-ink-300">
                            {new Date(s.started_at).toLocaleDateString(undefined, { month: "short", day: "numeric" })}
                          </span>
                          <span className="text-ink-500 tabular-nums">{formatDuration(s.duration_seconds ?? 0)}</span>
                        </div>
                        {s.session_goal && <p className="text-ink-500 text-xs mt-1">{s.session_goal}</p>}
                        {s.reflection_notes && <p className="text-ink-400 text-xs mt-1">{s.reflection_notes}</p>}
                      </li>
                    ))}
                </ul>
              </div>
            )}
          </>
        )}
      </div>
    </AppShell>
  );
}
