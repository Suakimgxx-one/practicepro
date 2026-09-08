export type RecordingType = "reference" | "student";
export type RecordingSource = "youtube" | "upload";
export type RecordingStatus = "pending" | "processing" | "ready" | "failed";

export interface Recording {
  id: string;
  user_id: string;
  piece_id: string | null;
  type: RecordingType;
  source: RecordingSource;
  source_url: string | null;
  storage_path: string | null;
  duration_seconds: number | null;
  status: RecordingStatus;
  created_at: string;
}

export interface User {
  id: string;
  email: string;
  created_at: string;
}
