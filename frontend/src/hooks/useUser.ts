import { useCallback, useEffect, useState } from "react";
import { createUser, getUser } from "@/api/client";
import type { User } from "@/types/recording";

const STORAGE_KEY = "practicepro_user_id";

/**
 * Stands in for real authentication, which this project deliberately
 * doesn't have yet (see app/schemas/recording.py's RecordingCreate —
 * user_id is passed explicitly in every request because there's no
 * session/auth layer). This hook just persists whichever user_id was
 * last created in localStorage so a returning visitor doesn't have to
 * re-enter their email every time.
 */
export function useUser() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedId = localStorage.getItem(STORAGE_KEY);
    if (!storedId) {
      setLoading(false);
      return;
    }

    getUser(storedId)
      .then(setUser)
      .catch(() => {
        // Stored id no longer resolves (e.g. DB was reset locally) —
        // clear it so the user is prompted to re-enter their email
        // instead of getting stuck.
        localStorage.removeItem(STORAGE_KEY);
      })
      .finally(() => setLoading(false));
  }, []);

  const signIn = useCallback(async (email: string) => {
    const created = await createUser(email);
    localStorage.setItem(STORAGE_KEY, created.id);
    setUser(created);
    return created;
  }, []);

  return { user, loading, signIn };
}
