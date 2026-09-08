import type { AnalysisCategory, Feedback } from "@/types/analysis";
import { formatTime } from "@/lib/formatTime";

const CATEGORY_LABELS: Record<AnalysisCategory, string> = {
  pitch: "Pitch",
  rhythm: "Rhythm",
  tempo: "Tempo",
  dynamics: "Dynamics",
};

export function FeedbackList({ feedback }: { feedback: Feedback[] }) {
  if (feedback.length === 0) {
    return <p className="text-sm text-ink-500">No coaching feedback was generated for this session.</p>;
  }
  const grouped = feedback.reduce<Record<string, Feedback[]>>((acc, item) => {
    (acc[item.category] ??= []).push(item);
    return acc;
  }, {});
  return (
    <div className="space-y-5">
      {(Object.keys(grouped) as AnalysisCategory[]).map((category) => (
        <div key={category}>
          <h4 className="text-sm font-medium text-ink-100 mb-2">{CATEGORY_LABELS[category]}</h4>
          <ul className="space-y-2.5">
            {grouped[category].map((item) => (
              <li key={item.id} className="text-sm text-ink-300 leading-relaxed pl-3 border-l-2 border-accent-500/30">
                {item.timestamp_reference !== null && (
                  <span className="text-ink-500 tabular-nums mr-1.5">{formatTime(item.timestamp_reference)}</span>
                )}
                {item.text}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
