import { useState } from "react";

interface EmailGateProps {
  onSubmit: (email: string) => Promise<unknown>;
}

export function EmailGate({ onSubmit }: EmailGateProps) {
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await onSubmit(email);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center px-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm bg-slate-900 border border-slate-800 rounded-xl p-6"
      >
        <h1 className="text-xl font-semibold mb-1">PracticePro</h1>
        <p className="text-slate-400 text-sm mb-5">
          Enter your email to start a practice session.
        </p>
        <input
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          className="w-full rounded-lg bg-slate-800 border border-slate-700 px-3 py-2 text-sm mb-3 outline-none focus:border-slate-500"
        />
        {error && <p className="text-red-400 text-sm mb-3">{error}</p>}
        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed py-2 text-sm font-medium transition-colors"
        >
          {submitting ? "Starting…" : "Continue"}
        </button>
      </form>
    </div>
  );
}
