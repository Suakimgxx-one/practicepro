import { useCallback, useEffect, useState } from "react";
import { listPieces } from "@/api/client";
import type { Piece } from "@/types/piece";

export function usePieces(userId: string | null) {
  const [pieces, setPieces] = useState<Piece[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(async () => {
    if (!userId) return;
    setLoading(true);
    try {
      const result = await listPieces(userId);
      setPieces(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load pieces");
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { pieces, loading, error, refetch };
}
