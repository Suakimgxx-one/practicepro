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
        <h2 className="text-sm font-medium text-ink-300">Reference performance</h2>
        {recording && <StatusBadge status={recording.status} />}
      </div>
      {!recordingId ? (
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="url"
            required
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste a YouTube link"
            className="flex-1 bg-surface-900 border border-border-subtle focus:border-accent-500 rounded-lg px-3.5 py-2.5 text-sm outline-none transition-colors"
          />
          <button
            type="submit"
            disabled={submitting}
            className="bg-surface-800 hover:bg-surface-700 disabled:opacity-50 text-sm font-medium px-4 py-2.5 rounded-lg transition-colors whitespace-nowrap"
          >
            {submitting ? "Submitting" : "Add"}
          </button>
        </form>
      ) : (
        <p className="text-sm text-ink-500 truncate">{url}</p>
      )}
      {submitError && <p className="text-danger text-sm mt-2">{submitError}</p>}
      {pollError && <p className="text-danger text-sm mt-2">{pollError}</p>}
      {recording?.status === "failed" && (
        <p className="text-danger text-sm mt-2">
          Couldn't process this video — it may be unavailable, or the link might be invalid.
        </p>
      )}
    </div>
  );
}
