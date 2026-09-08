import { useCallback, useEffect, useState } from "react";
import { createFolder, deleteFolder, listFolders, updateFolder } from "@/api/client";
import type { Folder } from "@/types/folder";

export function useFolders(userId: string | null) {
  const [folders, setFolders] = useState<Folder[]>([]);
  const [loading, setLoading] = useState(true);

  const refetch = useCallback(async () => {
    if (!userId) return;
    setLoading(true);
    try {
      const result = await listFolders(userId);
      setFolders(result);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  const create = useCallback(
    async (name: string, color: string) => {
      if (!userId) return;
      await createFolder({ user_id: userId, name, color });
      await refetch();
    },
    [userId, refetch]
  );

  const rename = useCallback(
    async (folderId: string, name: string) => {
      await updateFolder(folderId, { name });
      await refetch();
    },
    [refetch]
  );

  const remove = useCallback(
    async (folderId: string) => {
      await deleteFolder(folderId);
      await refetch();
    },
    [refetch]
  );

  return { folders, loading, refetch, create, rename, remove };
}
