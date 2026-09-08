import { useEffect, useRef, useState } from "react";
import { createRecording } from "@/api/client";
import { useRecordingPolling } from "@/hooks/useRecordingPolling";
import { StatusBadge } from "@/components/StatusBadge";

interface YoutubeReferenceInputProps {
  userId: string;
  pieceId?: string;
  onReady: (recordingId: string) => void;
}

export function YoutubeReferenceInput({ userId, pieceId, onReady }: YoutubeReferenceInputProps) {
  const [url, setUrl] = useState("");
  const [recordingId, setRecordingId] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const { recording, error: pollError } = useRecordingPolling(recordingId);
  const hasNotifiedReady = useRef(false);

  useEffect(() => {
    if (recording?.status === "ready" && recordingId && !hasNotifiedReady.current) {
      hasNotifiedReady.current = true;
      onReady(recordingId);
    }
  }, [recording?.status, recordingId, onReady]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError(null);
    setSubmitting(true);
    try {
      const created = await createRecording({
        user_id: userId,
        type: "reference",
        source: "youtube",
        source_url: url,
        piece_id: pieceId,
      });
      setRecordingId(created.id);
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "Failed to submit URL");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <div className="flex items-baseline justify-between mb-3">
        <h2 className="text-sm font-medium text-ink-soft">Reference performance</h2>
        {recording && <StatusBadge status={recording.status} />}
      </div>
      {!recordingId ? (
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            type="url"
            required
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste a YouTube link"
            className="flex-1 bg-transparent border-b border-line pb-2 text-sm outline-none focus:border-brass transition-colors"
          />
          <button
            type="submit"
            disabled={submitting}
            className="text-sm font-medium text-ink hover:text-brass-dark disabled:opacity-50 transition-colors whitespace-nowrap"
          >
            {submitting ? "Submitting" : "Add"}
          </button>
        </form>
      ) : (
        <p className="text-sm text-ink-soft truncate">{url}</p>
      )}
      {submitError && <p className="text-brick text-sm mt-2">{submitError}</p>}
      {pollError && <p className="text-brick text-sm mt-2">{pollError}</p>}
      {recording?.status === "failed" && (
        <p className="text-brick text-sm mt-2">
          Couldn't process this video — it may be unavailable, or the link might be invalid.
        </p>
      )}
    </div>
  );
}
