import { useCallback, useEffect, useState } from "react";
import { getPiece } from "@/api/client";
import type { PieceDetail } from "@/types/piece";

export function usePieceDetail(pieceId: string | null) {
  const [piece, setPiece] = useState<PieceDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(async () => {
    if (!pieceId) return;
    try {
      const result = await getPiece(pieceId);
      setPiece(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load piece");
    } finally {
      setLoading(false);
    }
  }, [pieceId]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { piece, loading, error, refetch };
}
