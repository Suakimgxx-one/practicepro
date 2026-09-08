import type { RecordingStatus } from "@/types/recording";

const STATUS_STYLES: Record<RecordingStatus, string> = {
  pending: "text-ink-500",
  processing: "text-accent-400",
  ready: "text-success",
  failed: "text-danger",
};

const STATUS_LABELS: Record<RecordingStatus, string> = {
  pending: "Pending",
  processing: "Processing",
  ready: "Ready",
  failed: "Failed",
};

export function StatusBadge({ status }: { status: RecordingStatus }) {
  return (
    <span className={`inline-flex items-center gap-1.5 text-sm ${STATUS_STYLES[status]}`}>
      <span
        className={`w-1.5 h-1.5 rounded-full ${status === "processing" ? "animate-pulse" : ""}`}
        style={{ backgroundColor: "currentColor" }}
      />
      {STATUS_LABELS[status]}
    </span>
  );
}
