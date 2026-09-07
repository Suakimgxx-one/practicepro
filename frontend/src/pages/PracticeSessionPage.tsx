import { useState } from "react";
import { useUser } from "@/hooks/useUser";
import { EmailGate } from "@/components/EmailGate";
import { YoutubeReferenceInput } from "@/components/YoutubeReferenceInput";
import { RecordingUploader } from "@/components/RecordingUploader";

export function PracticeSessionPage() {
  const { user, loading, signIn } = useUser();
  const [referenceId, setReferenceId] = useState<string | null>(null);
  const [studentId, setStudentId] = useState<string | null>(null);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center">
        <p className="text-slate-500 text-sm">Loading…</p>
      </div>
    );
  }

  if (!user) {
    return <EmailGate onSubmit={signIn} />;
  }

  const bothReady = referenceId && studentId;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 px-4 py-10">
      <div className="max-w-2xl mx-auto">
        <header className="mb-8">
          <h1 className="text-2xl font-semibold">PracticePro</h1>
          <p className="text-slate-400 text-sm mt-1">Signed in as {user.email}</p>
        </header>

        <div className="space-y-4">
          <YoutubeReferenceInput userId={user.id} onReady={setReferenceId} />
          <RecordingUploader userId={user.id} onReady={setStudentId} />
        </div>

        {bothReady && (
          <div className="mt-6 bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-5">
            <p className="text-emerald-400 text-sm font-medium">Both recordings are ready.</p>
            <p className="text-slate-400 text-sm mt-1">
              The backend can now run the full comparison (alignment, pitch,
              rhythm, tempo, dynamics, feedback) via POST /analysis-sessions —
              chart visualization of that output lands next.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
