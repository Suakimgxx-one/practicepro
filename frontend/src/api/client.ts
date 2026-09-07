import type { Recording, User } from "@/types/recording";
import type { AnalysisSession } from "@/types/analysis";

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
      ...(init?.body && !(init.body instanceof FormData) ? { "Content-Type": "application/json" } : {}),
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

  return response.json() as Promise<T>;
}

export async function createUser(email: string): Promise<User> {
  return request<User>("/api/v1/users", { method: "POST", body: JSON.stringify({ email }) });
}

export async function getUser(userId: string): Promise<User> {
  return request<User>(`/api/v1/users/${userId}`);
}

export async function createRecording(payload: {
  user_id: string;
  type: "reference" | "student";
  source: "youtube" | "upload";
  source_url?: string;
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
  return request<Recording>(`/api/v1/recordings/${recordingId}/upload`, { method: "POST", body: formData });
}

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
