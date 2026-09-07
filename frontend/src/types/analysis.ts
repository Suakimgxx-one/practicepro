export type AnalysisCategory = "pitch" | "rhythm" | "tempo" | "dynamics";
export type SessionStatus = "pending" | "aligning" | "analyzing" | "complete" | "failed";

export interface AnalysisResult {
  id: string;
  session_id: string;
  category: AnalysisCategory;
  // Shape varies by category — see worker/tasks/analyze.py's
  // results_payload for the exact structure each category writes.
  // Charting components (Milestone 12) narrow this per-category.
  data: Record<string, unknown>;
  created_at: string;
}

export interface Feedback {
  id: string;
  session_id: string;
  category: AnalysisCategory;
  text: string;
  timestamp_reference: number | null;
  created_at: string;
}

export interface AnalysisSession {
  id: string;
  user_id: string;
  reference_recording_id: string;
  student_recording_id: string;
  status: SessionStatus;
  created_at: string;
  results: AnalysisResult[];
  feedback: Feedback[];
}
