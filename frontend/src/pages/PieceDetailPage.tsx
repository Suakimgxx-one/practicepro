import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useUser } from "@/hooks/useUser";
import { usePieceDetail } from "@/hooks/usePieceDetail";
import { EmailGate } from "@/components/EmailGate";
import { YoutubeReferenceInput } from "@/components/YoutubeReferenceInput";
import { RecordingUploader } from "@/components/RecordingUploader";
import { AnalysisRunner } from "@/components/AnalysisRunner";
import { ProgressChart } from "@/components/ProgressChart";

export function PieceDetailPage() {
  const { pieceId } = useParams<{ pieceId: string }>();
  const { user, loading: userLoading, signIn } = useUser();
  const { piece, loading: pieceLoading, error, refetch } = usePieceDetail(pieceId ?? null);
  const [activeAttemptId, setActiveAttemptId] = useState<string | null>(null);

  if (userLoading || pieceLoading) {
    return (
      <div className="min-h-screen bg-paper flex items-center justify-center">
        <p className="text-ink-faint text-sm">Loading</p>
      </div>
    );
  }

  if (!user) {
    return <EmailGate onSubmit={signIn} />;
  }

  if (error || !piece) {
    return (
      <div className="min-h-screen bg-paper text-ink px-6 py-14">
        <div className="max-w-xl mx-auto">
          <Link to="/" className="text-sm text-ink-soft hover:text-brass-dark transition-colors">
            ← Your pieces
          </Link>
          <p className="text-brick text-sm mt-6">{error ?? "Piece not found."}</p>
        </div>
      </div>
    );
  }

  const hasReference = piece.reference_recording !== null && piece.reference_recording.status === "ready";

  return (
    <div className="min-h-screen bg-paper text-ink px-6 py-14">
      <div className="max-w-xl mx-auto">
        <Link to="/" className="text-sm text-ink-soft hover:text-brass-dark transition-colors">
          ← Your pieces
        </Link>

        <h1 className="font-serif text-4xl mt-4 mb-8">{piece.title}</h1>

        {!hasReference ? (
          <div className="pb-8 border-b border-line">
            <p className="text-sm text-ink-soft mb-4">
              Add a reference performance to compare your practice against.
            </p>
            <YoutubeReferenceInput userId={user.id} pieceId={piece.id} onReady={() => refetch()} />
          </div>
        ) : (
          <>
            <div className="pb-8 border-b border-line">
              <RecordingUploader
                userId={user.id}
                pieceId={piece.id}
                label="Log a new practice attempt"
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

            <div className="py-8">
              <div className="flex items-baseline justify-between mb-3">
                <h2 className="text-sm font-medium text-ink-soft">Progress</h2>
                <span className="text-xs text-ink-faint">
                  {piece.attempts.length} attempt{piece.attempts.length === 1 ? "" : "s"} logged
                </span>
              </div>
              <ProgressChart progress={piece.progress} />
            </div>
          </>
        )}
      </div>
    </div>
  );
}
