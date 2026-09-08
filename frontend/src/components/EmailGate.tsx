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
    <div className="min-h-screen bg-surface-950 text-ink-100 flex items-center justify-center px-6">
      <form onSubmit={handleSubmit} className="w-full max-w-sm">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-400 to-accent-600 shadow-glow mb-6" />
        <h1 className="text-2xl font-semibold tracking-tight mb-2">PracticePro</h1>
        <p className="text-ink-500 text-sm mb-6 leading-relaxed">
          A focused practice workspace for musicians. Enter your email to begin.
        </p>
        <input
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          className="w-full bg-surface-900 border border-border-subtle focus:border-accent-500 rounded-lg px-3.5 py-2.5 text-sm outline-none transition-colors mb-4"
        />
        {error && <p className="text-danger text-sm mb-4">{error}</p>}
        <button
          type="submit"
          disabled={submitting}
          className="w-full bg-accent-500 hover:bg-accent-400 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium py-2.5 rounded-lg shadow-glow transition-colors"
        >
          {submitting ? "Starting" : "Continue"}
        </button>
      </form>
    </div>
  );
}
