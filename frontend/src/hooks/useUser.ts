import { useCallback, useEffect, useState } from "react";
import { createUser, getUser } from "@/api/client";
import type { User } from "@/types/recording";

const STORAGE_KEY = "practicepro_user_id";

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
