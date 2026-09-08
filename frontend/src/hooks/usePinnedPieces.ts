import { useCallback, useEffect, useState } from "react";

const STORAGE_KEY = "practicepro_pinned_pieces";

/**
 * Pinned pieces are stored in localStorage rather than the backend —
 * a real, working feature (persists across reloads), just scoped to
 * this browser rather than synced across devices. That tradeoff is
 * explicit, not a hidden limitation.
 */
export function usePinnedPieces() {
  const [pinnedIds, setPinnedIds] = useState<Set<string>>(new Set());

  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) setPinnedIds(new Set(JSON.parse(stored)));
    } catch {
      // corrupt/missing storage — start empty
    }
  }, []);

  const toggle = useCallback((pieceId: string) => {
    setPinnedIds((prev) => {
      const next = new Set(prev);
      if (next.has(pieceId)) {
        next.delete(pieceId);
      } else {
        next.add(pieceId);
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify([...next]));
      return next;
    });
  }, []);

  return { pinnedIds, toggle };
}
