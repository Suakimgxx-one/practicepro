import type { Recording, User } from "@/types/recording";

// Vite exposes env vars prefixed with VITE_ via import.meta.env.
// Falls back to localhost:8000 for local dev, matching docker-compose.
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
    // Our FastAPI exception handlers all return {"detail": "..."} —
    // see app/main.py's registered exception_handlers. Pydantic
    // validation errors (422) return a slightly different shape
    // ({"detail": [...]}), so we fall back gracefully either way.
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail =
        typeof body.detail === "string"
          ? body.detail
          : JSON.stringify(body.detail ?? body);
    } catch {
      // response wasn't JSON — keep statusText
    }
    throw new ApiError(response.status, detail);
  }

  return response.json() as Promise<T>;
}

export async function createUser(email: string): Promise<User> {
  return request<User>("/api/v1/users", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
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
  return request<Recording>("/api/v1/recordings", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getRecording(recordingId: string): Promise<Recording> {
  return request<Recording>(`/api/v1/recordings/${recordingId}`);
}

export async function listRecordings(userId: string): Promise<Recording[]> {
  return request<Recording[]>(`/api/v1/recordings?user_id=${userId}`);
}

export async function uploadRecordingAudio(
  recordingId: string,
  file: File
): Promise<Recording> {
  const formData = new FormData();
  formData.append("file", file);

  return request<Recording>(`/api/v1/recordings/${recordingId}/upload`, {
    method: "POST",
    body: formData,
  });
}
