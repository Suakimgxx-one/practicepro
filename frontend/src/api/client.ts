import type { Recording, User } from "@/types/recording";
import type { AnalysisSession } from "@/types/analysis";
import type { Piece, PieceDetail } from "@/types/piece";
import type { Folder } from "@/types/folder";
import type { PracticeSession } from "@/types/practiceSession";

const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      ...(init?.body && !(init.body instanceof FormData)
        ? { "Content-Type": "application/json" }
        : {}),
      ...init?.headers,
    },
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail ?? body);
    } catch {
      // not JSON — keep statusText
    }
    throw new ApiError(response.status, detail);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

// --- Users ---
export async function createUser(email: string): Promise<User> {
  return request<User>("/api/v1/users", { method: "POST", body: JSON.stringify({ email }) });
}

export async function getUser(userId: string): Promise<User> {
  return request<User>(`/api/v1/users/${userId}`);
}

// --- Recordings ---
export async function createRecording(payload: {
  user_id: string;
  type: "reference" | "student";
  source: "youtube" | "upload";
  source_url?: string;
  piece_id?: string;
}): Promise<Recording> {
  return request<Recording>("/api/v1/recordings", { method: "POST", body: JSON.stringify(payload) });
}

export async function getRecording(recordingId: string): Promise<Recording> {
  return request<Recording>(`/api/v1/recordings/${recordingId}`);
}

export async function listRecordings(userId: string): Promise<Recording[]> {
  return request<Recording[]>(`/api/v1/recordings?user_id=${userId}`);
}

export async function uploadRecordingAudio(recordingId: string, file: File): Promise<Recording> {
  const formData = new FormData();
  formData.append("file", file);
  return request<Recording>(`/api/v1/recordings/${recordingId}/upload`, {
    method: "POST",
    body: formData,
  });
}

// --- Analysis sessions ---
export async function createAnalysisSession(payload: {
  user_id: string;
  reference_recording_id: string;
  student_recording_id: string;
}): Promise<AnalysisSession> {
  return request<AnalysisSession>("/api/v1/analysis-sessions", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getAnalysisSession(sessionId: string): Promise<AnalysisSession> {
  return request<AnalysisSession>(`/api/v1/analysis-sessions/${sessionId}`);
}

// --- Pieces ---
export async function createPiece(payload: {
  user_id: string;
  title: string;
  composer?: string;
  instrument?: string;
  folder_id?: string;
}): Promise<Piece> {
  return request<Piece>("/api/v1/pieces", { method: "POST", body: JSON.stringify(payload) });
}

export async function listPieces(userId: string): Promise<Piece[]> {
  return request<Piece[]>(`/api/v1/pieces?user_id=${userId}`);
}

export async function getPiece(pieceId: string): Promise<PieceDetail> {
  return request<PieceDetail>(`/api/v1/pieces/${pieceId}`);
}

export async function updatePiece(
  pieceId: string,
  payload: Partial<{ title: string; composer: string | null; instrument: string | null; folder_id: string | null }>
): Promise<Piece> {
  return request<Piece>(`/api/v1/pieces/${pieceId}`, { method: "PATCH", body: JSON.stringify(payload) });
}

// --- Folders ---
export async function createFolder(payload: { user_id: string; name: string; color?: string }): Promise<Folder> {
  return request<Folder>("/api/v1/folders", { method: "POST", body: JSON.stringify(payload) });
}

export async function listFolders(userId: string): Promise<Folder[]> {
  return request<Folder[]>(`/api/v1/folders?user_id=${userId}`);
}

export async function updateFolder(
  folderId: string,
  payload: Partial<{ name: string; color: string }>
): Promise<Folder> {
  return request<Folder>(`/api/v1/folders/${folderId}`, { method: "PATCH", body: JSON.stringify(payload) });
}

export async function deleteFolder(folderId: string): Promise<void> {
  return request<void>(`/api/v1/folders/${folderId}`, { method: "DELETE" });
}

// --- Practice sessions ---
export async function startPracticeSession(payload: {
  user_id: string;
  piece_id: string;
  focus_section?: string;
  session_goal?: string;
  target_tempo_bpm?: number;
}): Promise<PracticeSession> {
  return request<PracticeSession>("/api/v1/practice-sessions", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function finishPracticeSession(
  sessionId: string,
  payload: { reflection_notes?: string; self_rating?: number }
): Promise<PracticeSession> {
  return request<PracticeSession>(`/api/v1/practice-sessions/${sessionId}/finish`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function listPracticeSessionsForUser(userId: string): Promise<PracticeSession[]> {
  return request<PracticeSession[]>(`/api/v1/practice-sessions?user_id=${userId}`);
}
