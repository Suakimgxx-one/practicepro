import type { Recording } from "@/types/recording";

export interface Piece {
  id: string;
  user_id: string;
  title: string;
  reference_recording_id: string | null;
  created_at: string;
}

export interface PieceProgressPoint {
  session_id: string;
  student_recording_id: string;
  created_at: string;
  mean_absolute_cents_deviation: number | null;
  mean_absolute_timing_offset_seconds: number | null;
  mean_tempo_ratio: number | null;
  mean_absolute_loudness_difference_db: number | null;
}

export interface PieceDetail extends Piece {
  reference_recording: Recording | null;
  attempts: Recording[];
  progress: PieceProgressPoint[];
}
