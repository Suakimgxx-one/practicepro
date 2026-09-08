import { useEffect, useState } from "react";
import { listPieces, listPracticeSessionsForUser } from "@/api/client";
import type { Piece } from "@/types/piece";
import type { PracticeSession } from "@/types/practiceSession";

export interface DashboardData {
  pieces: Piece[];
  sessions: PracticeSession[];
  minutesToday: number;
  minutesThisWeek: number;
  streakDays: number;
  weeklyActivity: { day: string; minutes: number }[];
  recentlyPracticedPieceIds: string[];
  piecesNeedingAttention: Piece[];
}

function isSameDay(a: Date, b: Date): boolean {
  return a.toDateString() === b.toDateString();
}

function startOfWeek(date: Date): Date {
  const d = new Date(date);
  const day = d.getDay();
  d.setDate(d.getDate() - day);
  d.setHours(0, 0, 0, 0);
  return d;
}

export function useDashboardData(userId: string | null) {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!userId) return;
    let cancelled = false;

    (async () => {
      setLoading(true);
      const [pieces, sessions] = await Promise.all([
        listPieces(userId),
        listPracticeSessionsForUser(userId),
      ]);
      if (cancelled) return;

      const finished = sessions.filter((s) => s.ended_at !== null && s.duration_seconds !== null);
      const now = new Date();
      const weekStart = startOfWeek(now);

      const minutesToday = Math.round(
        finished
          .filter((s) => isSameDay(new Date(s.started_at), now))
          .reduce((sum, s) => sum + (s.duration_seconds ?? 0), 0) / 60
      );

      const minutesThisWeek = Math.round(
        finished
          .filter((s) => new Date(s.started_at) >= weekStart)
          .reduce((sum, s) => sum + (s.duration_seconds ?? 0), 0) / 60
      );

      const practiceDays = new Set(finished.map((s) => new Date(s.started_at).toDateString()));
      let streakDays = 0;
      const cursor = new Date(now);
      while (practiceDays.has(cursor.toDateString())) {
        streakDays += 1;
        cursor.setDate(cursor.getDate() - 1);
      }

      const weeklyActivity: { day: string; minutes: number }[] = [];
      for (let i = 6; i >= 0; i--) {
        const d = new Date(now);
        d.setDate(d.getDate() - i);
        const minutes = Math.round(
          finished
            .filter((s) => isSameDay(new Date(s.started_at), d))
            .reduce((sum, s) => sum + (s.duration_seconds ?? 0), 0) / 60
        );
        weeklyActivity.push({ day: d.toLocaleDateString(undefined, { weekday: "short" }), minutes });
      }

      const recentlyPracticedPieceIds = [
        ...new Set(
          finished
            .sort((a, b) => new Date(b.started_at).getTime() - new Date(a.started_at).getTime())
            .map((s) => s.piece_id)
        ),
      ].slice(0, 5);

      const practicedPieceIds = new Set(finished.map((s) => s.piece_id));
      const piecesNeedingAttention = pieces.filter((p) => !practicedPieceIds.has(p.id));

      if (!cancelled) {
        setData({
          pieces,
          sessions: finished,
          minutesToday,
          minutesThisWeek,
          streakDays,
          weeklyActivity,
          recentlyPracticedPieceIds,
          piecesNeedingAttention,
        });
        setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [userId]);

  return { data, loading };
}
