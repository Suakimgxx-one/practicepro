import type {
  AnalysisCategory,
  AnalysisSession,
  DynamicsResultData,
  PitchResultData,
  RhythmResultData,
  TempoResultData,
} from "@/types/analysis";
import { PitchChart } from "@/components/charts/PitchChart";
import { TempoChart } from "@/components/charts/TempoChart";
import { RegionsList } from "@/components/RegionsList";
import { FeedbackList } from "@/components/FeedbackList";

function getResultData<T>(session: AnalysisSession, category: AnalysisCategory): T | undefined {
  const result = session.results.find((r) => r.category === category);
  return result?.data as T | undefined;
}

export function AnalysisResults({ session }: { session: AnalysisSession }) {
  const pitch = getResultData<PitchResultData>(session, "pitch");
  const rhythm = getResultData<RhythmResultData>(session, "rhythm");
  const tempo = getResultData<TempoResultData>(session, "tempo");
  const dynamics = getResultData<DynamicsResultData>(session, "dynamics");

  return (
    <div className="divide-y divide-line">
      {pitch && <div className="py-6 first:pt-0"><PitchChart data={pitch} /></div>}
      {tempo && <div className="py-6"><TempoChart data={tempo} /></div>}

      {rhythm && (
        <div className="py-6">
          <div className="flex items-baseline justify-between">
            <h3 className="text-sm font-medium text-ink-soft">Rhythm</h3>
            <span className="text-xs text-ink-faint">
              {(rhythm.mean_absolute_timing_offset_seconds * 1000).toFixed(0)}ms average offset
              {rhythm.unmatched_reference_onsets > 0 &&
                ` · ${rhythm.unmatched_reference_onsets} note${rhythm.unmatched_reference_onsets === 1 ? "" : "s"} possibly missed`}
            </span>
          </div>
          <RegionsList regions={rhythm.flagged_regions} emptyMessage="No significant timing issues detected." />
        </div>
      )}

      {dynamics && (
        <div className="py-6">
          <div className="flex items-baseline justify-between">
            <h3 className="text-sm font-medium text-ink-soft">Dynamics</h3>
            <span className="text-xs text-ink-faint">
              {dynamics.mean_absolute_loudness_difference_db.toFixed(1)} dB average difference
            </span>
          </div>
          <RegionsList regions={dynamics.flagged_regions} emptyMessage="No significant dynamics issues detected." />
        </div>
      )}

      <div className="py-6 last:pb-0">
        <h3 className="text-sm font-medium text-ink-soft mb-3">Coaching notes</h3>
        <FeedbackList feedback={session.feedback} />
      </div>
    </div>
  );
}
