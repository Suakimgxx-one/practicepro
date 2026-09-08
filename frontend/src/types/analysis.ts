export type AnalysisCategory = "pitch" | "rhythm" | "tempo" | "dynamics";
export type SessionStatus = "pending" | "aligning" | "analyzing" | "complete" | "failed";

// These shapes are deliberately kept in exact sync with the dicts built
// in backend/worker/tasks/analyze.py's results_payload — that's the one
// and only place this JSON is produced, so these types should change
// only if that function's output changes.

export interface FlaggedRegion {
  start: number;
  end: number;
}

export interface LabeledFlaggedRegion extends FlaggedRegion {
  label: string;
}

export interface PitchResultData {
  mean_absolute_cents_deviation: number;
  flagged_regions: FlaggedRegion[];
  points: { reference_time: number; cents_deviation: number }[];
}

export interface RhythmResultData {
  mean_absolute_timing_offset_seconds: number;
  unmatched_reference_onsets: number;
  unmatched_student_onsets: number;
  flagged_regions: FlaggedRegion[];
}

export interface TempoResultData {
  mean_tempo_ratio: number;
  reference_average_bpm: number | null;
  student_average_bpm: number | null;
  flagged_regions: LabeledFlaggedRegion[];
  points: { reference_time: number; local_tempo_ratio: number }[];
}

export interface DynamicsResultData {
  mean_absolute_loudness_difference_db: number;
  flagged_regions: LabeledFlaggedRegion[];
}

export interface AnalysisResult {
  id: string;
  session_id: string;
  category: AnalysisCategory;
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
