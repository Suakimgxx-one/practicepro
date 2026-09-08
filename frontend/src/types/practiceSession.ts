export interface PracticeSession {
  id: string;
  user_id: string;
  piece_id: string;
  focus_section: string | null;
  session_goal: string | null;
  target_tempo_bpm: number | null;
  started_at: string;
  ended_at: string | null;
  duration_seconds: number | null;
  reflection_notes: string | null;
  self_rating: number | null;
  created_at: string;
}
