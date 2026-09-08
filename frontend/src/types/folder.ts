export interface Folder {
  id: string;
  user_id: string;
  name: string;
  color: string;
  created_at: string;
  piece_count: number;
}

export const FOLDER_COLORS = ["violet", "emerald", "amber", "rose", "sky"] as const;
export type FolderColor = (typeof FOLDER_COLORS)[number];
