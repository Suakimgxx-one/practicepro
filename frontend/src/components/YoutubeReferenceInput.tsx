import { useEffect, useRef, useState } from "react";
import { createRecording } from "@/api/client";
import { useRecordingPolling } from "@/hooks/useRecordingPolling";
import { StatusBadge } from "@/components/StatusBadge";

interface YoutubeReferenceInputProps {
  userId: string;
  onReady: (recordingId: string) => void;
}

export function YoutubeReferenceInput({ userId, onReady }: YoutubeReferenceInputProps) {
  const [url, setUrl] = useState("");
  const [recordingId, setRecordingId] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const { recording, error: pollError } = useRecordingPolling(recordingId);
  const hasNotifiedReady = useRef(false);

  // Fires exactly once, the moment polling reports the recording is
  // ready. Calling onReady() directly in the render body (rather than
  // in an effect) would run on every render and call a parent state
  // setter during this component's render — React explicitly
  // discourages that outside specific derived-state patterns.
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
      });
      // Creation already auto-enqueues the Celery ingestion job — see
      // app/services/recording_service.py — so all the UI needs to do
      // from here is start polling.
      setRecordingId(created.id);
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "Failed to submit URL");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <div className="flex items-center justify-between mb-3">
        <h2 className="font-medium">Reference performance</h2>
        {recording && <StatusBadge status={recording.status} />}
      </div>

      {!recordingId ? (
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="url"
            required
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://youtube.com/watch?v=..."
            className="flex-1 rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-sm outline-none focus:border-slate-500"
          />
          <button
            type="submit"
            disabled={submitting}
            className="rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 px-4 py-2 text-sm font-medium transition-colors"
          >
            {submitting ? "Submitting…" : "Submit"}
          </button>
        </form>
      ) : (
        <p className="text-sm text-slate-400 truncate">{url}</p>
      )}

      {submitError && <p className="text-red-400 text-sm mt-2">{submitError}</p>}
      {pollError && <p className="text-red-400 text-sm mt-2">{pollError}</p>}
      {recording?.status === "failed" && (
        <p className="text-red-400 text-sm mt-2">
          Couldn't process this video — it may be unavailable, or the URL might be invalid.
        </p>
      )}
    </div>
  );
}
