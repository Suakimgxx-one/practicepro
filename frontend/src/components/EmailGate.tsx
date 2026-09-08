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
    <div className="min-h-screen bg-paper text-ink flex items-center justify-center px-6">
      <form onSubmit={handleSubmit} className="w-full max-w-sm">
        <h1 className="font-serif text-3xl mb-2">PracticePro</h1>
        <p className="text-ink-soft text-sm mb-6 leading-relaxed">
          A practice journal for the pieces you're working on. Enter your email to begin.
        </p>
        <input
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          className="w-full bg-transparent border-b border-line pb-2 text-sm outline-none focus:border-brass transition-colors mb-4"
        />
        {error && <p className="text-brick text-sm mb-4">{error}</p>}
        <button
          type="submit"
          disabled={submitting}
          className="text-sm font-medium text-paper bg-ink hover:bg-brass-dark disabled:opacity-50 disabled:cursor-not-allowed px-5 py-2.5 rounded transition-colors"
        >
          {submitting ? "Starting" : "Continue"}
        </button>
      </form>
    </div>
  );
}
