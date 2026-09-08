import { useEffect, useRef, useState } from "react";
import { createRecording, uploadRecordingAudio } from "@/api/client";
import { useRecordingPolling } from "@/hooks/useRecordingPolling";
import { StatusBadge } from "@/components/StatusBadge";

interface RecordingUploaderProps {
  userId: string;
  pieceId?: string;
  label?: string;
  onReady: (recordingId: string) => void;
}

export function RecordingUploader({
  userId,
  pieceId,
  label = "Your recording",
  onReady,
}: RecordingUploaderProps) {
  const [recordingId, setRecordingId] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const { recording, error: pollError } = useRecordingPolling(recordingId);
  const hasNotifiedReady = useRef(false);

  useEffect(() => {
    if (recording?.status === "ready" && recordingId && !hasNotifiedReady.current) {
      hasNotifiedReady.current = true;
      onReady(recordingId);
    }
  }, [recording?.status, recordingId, onReady]);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setFileName(file.name);
    setUploadError(null);
    setUploading(true);
    try {
      const created = await createRecording({ user_id: userId, type: "student", source: "upload", piece_id: pieceId });
      setRecordingId(created.id);
      await uploadRecordingAudio(created.id, file);
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <div className="flex items-baseline justify-between mb-3">
        <h2 className="text-sm font-medium text-ink-300">{label}</h2>
        {recording && <StatusBadge status={recording.status} />}
      </div>
      {!recordingId ? (
        <label className="flex items-center gap-3 border border-dashed border-border-subtle hover:border-accent-500 rounded-lg px-4 py-3 cursor-pointer transition-colors">
          <span className="text-sm text-ink-300">{uploading ? "Uploading…" : "Choose an audio file"}</span>
          <span className="text-ink-500 text-xs">wav, mp3, m4a, flac, ogg</span>
          <input
            type="file"
            accept=".wav,.mp3,.m4a,.flac,.ogg"
            onChange={handleFileChange}
            disabled={uploading}
            className="hidden"
          />
        </label>
      ) : (
        <p className="text-sm text-ink-500 truncate">{fileName}</p>
      )}
      {uploadError && <p className="text-danger text-sm mt-2">{uploadError}</p>}
      {pollError && <p className="text-danger text-sm mt-2">{pollError}</p>}
      {recording?.status === "failed" && (
        <p className="text-danger text-sm mt-2">This file couldn't be processed — it may not be valid audio.</p>
      )}
    </div>
  );
}
