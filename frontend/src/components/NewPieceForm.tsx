import { useState } from "react";

interface NewPieceFormProps {
  onCreate: (title: string) => Promise<unknown>;
}

export function NewPieceForm({ onCreate }: NewPieceFormProps) {
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
        placeholder="Add a piece — e.g. Mozart Flute Concerto No. 1"
        className="flex-1 bg-transparent border-b border-line pb-2 text-sm outline-none focus:border-brass transition-colors"
      />
      <button
        type="submit"
        disabled={submitting || !title.trim()}
        className="text-sm font-medium text-ink hover:text-brass-dark disabled:opacity-40 transition-colors whitespace-nowrap"
      >
        {submitting ? "Adding" : "Add"}
      </button>
      {error && <p className="text-brick text-sm">{error}</p>}
    </form>
  );
}
