import { useState } from "react";

interface NewPieceFormProps {
  onCreate: (title: string) => Promise<unknown>;
  placeholder?: string;
}

export function NewPieceForm({ onCreate, placeholder }: NewPieceFormProps) {
  const [title, setTitle] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    setError(null);
    setSubmitting(true);
    try {
      await onCreate(title.trim());
      setTitle("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create piece");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-3 items-baseline">
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder={placeholder ?? "Add a piece — e.g. Mozart Flute Concerto No. 1"}
        className="flex-1 bg-surface-900 border border-border-subtle focus:border-accent-500 rounded-lg px-3.5 py-2.5 text-sm outline-none transition-colors"
      />
      <button
        type="submit"
        disabled={submitting || !title.trim()}
        className="bg-surface-800 hover:bg-surface-700 disabled:opacity-40 text-sm font-medium px-4 py-2.5 rounded-lg transition-colors whitespace-nowrap"
      >
        {submitting ? "Adding" : "Add"}
      </button>
      {error && <p className="text-danger text-sm">{error}</p>}
    </form>
  );
}
