import type { RecordingStatus } from "@/types/recording";

const STATUS_STYLES: Record<RecordingStatus, string> = {
  pending: "bg-slate-700 text-slate-300",
  processing: "bg-amber-500/20 text-amber-400",
  ready: "bg-emerald-500/20 text-emerald-400",
  failed: "bg-red-500/20 text-red-400",
};

const STATUS_LABELS: Record<RecordingStatus, string> = {
  pending: "Pending",
  processing: "Processing…",
  ready: "Ready",
  failed: "Failed",
};

export function StatusBadge({ status }: { status: RecordingStatus }) {
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${STATUS_STYLES[status]}`}
    >
      {STATUS_LABELS[status]}
    </span>
  );
}
