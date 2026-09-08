import { useState } from "react";
import { usePracticeTimer } from "@/hooks/usePracticeTimer";
import { formatDuration } from "@/lib/formatDuration";
import type { PracticeSession } from "@/types/practiceSession";

interface PracticeTimerWidgetProps {
  userId: string;
  pieceId: string;
  onSessionFinished?: (session: PracticeSession) => void;
}

function suggestNextStep(finished: PracticeSession): string {
  // A deterministic, data-derived note — not an AI-generated suggestion.
  // We don't claim any evaluation of the practice itself here, only
  // reflect back what was logged.
  if (finished.target_tempo_bpm) {
    return `Next time, try approaching this section a little closer to ${finished.target_tempo_bpm} bpm.`;
  }
  return "Log another attempt and compare it against your reference to track pitch accuracy over time.";
}

export function PracticeTimerWidget({ userId, pieceId, onSessionFinished }: PracticeTimerWidgetProps) {
  const { session, elapsedSeconds, starting, finishing, error, start, finish } = usePracticeTimer(userId, pieceId);

  const [showSetup, setShowSetup] = useState(false);
  const [focusSection, setFocusSection] = useState("");
  const [sessionGoal, setSessionGoal] = useState("");
  const [targetTempo, setTargetTempo] = useState("");

  const [showFinishModal, setShowFinishModal] = useState(false);
  const [reflection, setReflection] = useState("");
  const [rating, setRating] = useState<number | null>(null);
  const [summary, setSummary] = useState<PracticeSession | null>(null);

  const handleStart = async () => {
    await start({
      focus_section: focusSection || undefined,
      session_goal: sessionGoal || undefined,
      target_tempo_bpm: targetTempo ? Number(targetTempo) : undefined,
    });
    setShowSetup(false);
    setFocusSection("");
    setSessionGoal("");
    setTargetTempo("");
  };

  const handleFinish = async () => {
    const finished = await finish({
      reflection_notes: reflection || undefined,
      self_rating: rating ?? undefined,
    });
    setShowFinishModal(false);
    setReflection("");
    setRating(null);
    if (finished) {
      setSummary(finished);
      onSessionFinished?.(finished);
    }
  };

  // --- Completion summary screen ---
  if (summary) {
    return (
      <div className="bg-surface-900/60 border border-border-subtle rounded-xl p-6">
        <p className="text-xs text-success mb-1">Session saved</p>
        <p className="text-2xl font-semibold tabular-nums mb-4">{formatDuration(summary.duration_seconds ?? 0)}</p>
        <dl className="space-y-2 text-sm mb-4">
          {summary.session_goal && (
            <div className="flex justify-between"><dt className="text-ink-500">Goal</dt><dd className="text-ink-300">{summary.session_goal}</dd></div>
          )}
          {summary.focus_section && (
            <div className="flex justify-between"><dt className="text-ink-500">Section</dt><dd className="text-ink-300">{summary.focus_section}</dd></div>
          )}
          {summary.self_rating && (
            <div className="flex justify-between"><dt className="text-ink-500">Self-rating</dt><dd className="text-ink-300">{summary.self_rating}/5</dd></div>
          )}
        </dl>
        {summary.reflection_notes && <p className="text-sm text-ink-300 border-l-2 border-accent-500/30 pl-3 mb-4">{summary.reflection_notes}</p>}
        <p className="text-xs text-ink-500 mb-4">{suggestNextStep(summary)}</p>
        <button onClick={() => setSummary(null)} className="text-sm text-accent-400 hover:text-accent-300 transition-colors">
          Done
        </button>
      </div>
    );
  }

  // --- Active timer ---
  if (session) {
    return (
      <>
        <div className="bg-surface-900/60 border border-accent-500/30 rounded-xl p-6 shadow-glow">
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2 h-2 rounded-full bg-accent-400 animate-pulse" />
            <p className="text-xs text-ink-500">Practicing now</p>
          </div>
          <p className="text-4xl font-semibold tabular-nums mb-4">{formatDuration(elapsedSeconds)}</p>
          {session.session_goal && <p className="text-sm text-ink-300 mb-4">{session.session_goal}</p>}
          <button
            onClick={() => setShowFinishModal(true)}
            className="bg-surface-800 hover:bg-surface-700 text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            Finish session
          </button>
          {error && <p className="text-danger text-sm mt-2">{error}</p>}
        </div>

        {showFinishModal && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 px-4">
            <div className="bg-surface-900 border border-border-subtle rounded-xl p-6 w-full max-w-sm">
              <h3 className="text-base font-medium mb-4">How did it go?</h3>
              <div className="flex gap-1.5 mb-4">
                {[1, 2, 3, 4, 5].map((n) => (
                  <button
                    key={n}
                    onClick={() => setRating(n)}
                    className={`w-9 h-9 rounded-lg text-sm transition-colors ${
                      rating === n ? "bg-accent-500 text-white" : "bg-surface-800 text-ink-500 hover:text-ink-300"
                    }`}
                  >
                    {n}
                  </button>
                ))}
              </div>
              <textarea
                value={reflection}
                onChange={(e) => setReflection(e.target.value)}
                placeholder="Any notes on this session? (optional)"
                rows={3}
                className="w-full bg-surface-800 border border-border-subtle focus:border-accent-500 rounded-lg px-3 py-2 text-sm outline-none transition-colors resize-none mb-4"
              />
              <div className="flex gap-2">
                <button
                  onClick={handleFinish}
                  disabled={finishing}
                  className="flex-1 bg-accent-500 hover:bg-accent-400 disabled:opacity-50 text-white text-sm font-medium py-2.5 rounded-lg transition-colors"
                >
                  {finishing ? "Saving" : "Save session"}
                </button>
                <button
                  onClick={() => setShowFinishModal(false)}
                  className="px-4 py-2.5 text-sm text-ink-500 hover:text-ink-300 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </>
    );
  }

  // --- Idle / setup ---
  return (
    <div className="bg-surface-900/60 border border-border-subtle rounded-xl p-6">
      {!showSetup ? (
        <button
          onClick={() => setShowSetup(true)}
          className="flex items-center gap-2 bg-accent-500 hover:bg-accent-400 text-white text-sm font-medium px-5 py-2.5 rounded-lg shadow-glow transition-colors"
        >
          <svg viewBox="0 0 20 20" fill="none" className="w-4 h-4" strokeWidth="2">
            <path d="M6 4.5v11l9-5.5-9-5.5Z" fill="currentColor" />
          </svg>
          Start practice session
        </button>
      ) : (
        <div className="space-y-3">
          <input
            value={sessionGoal}
            onChange={(e) => setSessionGoal(e.target.value)}
            placeholder="Session goal (optional)"
            className="w-full bg-surface-800 border border-border-subtle focus:border-accent-500 rounded-lg px-3 py-2 text-sm outline-none transition-colors"
          />
          <div className="flex gap-3">
            <input
              value={focusSection}
              onChange={(e) => setFocusSection(e.target.value)}
              placeholder="Focus section, e.g. mm. 32-48"
              className="flex-1 bg-surface-800 border border-border-subtle focus:border-accent-500 rounded-lg px-3 py-2 text-sm outline-none transition-colors"
            />
            <input
              value={targetTempo}
              onChange={(e) => setTargetTempo(e.target.value)}
              type="number"
              placeholder="Target BPM"
              className="w-28 bg-surface-800 border border-border-subtle focus:border-accent-500 rounded-lg px-3 py-2 text-sm outline-none transition-colors"
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleStart}
              disabled={starting}
              className="bg-accent-500 hover:bg-accent-400 disabled:opacity-50 text-white text-sm font-medium px-5 py-2.5 rounded-lg shadow-glow transition-colors"
            >
              {starting ? "Starting" : "Start"}
            </button>
            <button onClick={() => setShowSetup(false)} className="px-4 py-2.5 text-sm text-ink-500 hover:text-ink-300 transition-colors">
              Cancel
            </button>
          </div>
        </div>
      )}
      {error && <p className="text-danger text-sm mt-2">{error}</p>}
    </div>
  );
}
