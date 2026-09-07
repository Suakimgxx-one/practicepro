import { useEffect, useRef, useState } from "react";
import { createRecording, uploadRecordingAudio } from "@/api/client";
import { useRecordingPolling } from "@/hooks/useRecordingPolling";
import { StatusBadge } from "@/components/StatusBadge";

interface RecordingUploaderProps {
  userId: string;
  onReady: (recordingId: string) => void;
}

export function RecordingUploader({ userId, onReady }: RecordingUploaderProps) {
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
      const created = await createRecording({ user_id: userId, type: "student", source: "upload" });
      setRecordingId(created.id);
      await uploadRecordingAudio(created.id, file);
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
      <div className="flex items-center justify-between mb-3">
        <h2 className="font-medium">Your recording</h2>
        {recording && <StatusBadge status={recording.status} />}
      </div>
      {!recordingId ? (
        <label className="flex flex-col items-center justify-center gap-1 rounded-lg border border-dashed border-slate-700 py-6 cursor-pointer hover:border-slate-500 transition-colors">
          <span className="text-sm text-slate-400">{uploading ? "Uploading…" : "Click to choose an audio file"}</span>
          <span className="text-xs text-slate-600">.wav, .mp3, .m4a, .flac, .ogg</span>
          <input type="file" accept=".wav,.mp3,.m4a,.flac,.ogg" onChange={handleFileChange} disabled={uploading} className="hidden" />
        </label>
      ) : (
        <p className="text-sm text-slate-400 truncate">{fileName}</p>
      )}
      {uploadError && <p className="text-red-400 text-sm mt-2">{uploadError}</p>}
      {pollError && <p className="text-red-400 text-sm mt-2">{pollError}</p>}
      {recording?.status === "failed" && <p className="text-red-400 text-sm mt-2">This file couldn't be processed — it may not be valid audio.</p>}
    </div>
  );
}
