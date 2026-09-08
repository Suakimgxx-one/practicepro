import { useState } from "react";
import { FOLDER_COLORS } from "@/types/folder";

const COLOR_SWATCH: Record<string, string> = {
  violet: "bg-accent-500",
  emerald: "bg-success",
  amber: "bg-warning",
  rose: "bg-danger",
  sky: "bg-sky-400",
};

interface NewFolderFormProps {
  onCreate: (name: string, color: string) => Promise<unknown>;
  onCancel: () => void;
}

export function NewFolderForm({ onCreate, onCancel }: NewFolderFormProps) {
  const [name, setName] = useState("");
  const [color, setColor] = useState<string>("violet");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setSubmitting(true);
    try {
      await onCreate(name.trim(), color);
      setName("");
      onCancel();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-surface-900/60 border border-border-subtle rounded-lg p-4 mb-4">
      <input
        autoFocus
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Folder name"
        className="w-full bg-surface-800 border border-border-subtle focus:border-accent-500 rounded-lg px-3 py-2 text-sm outline-none transition-colors mb-3"
      />
      <div className="flex items-center gap-2 mb-3">
        {FOLDER_COLORS.map((c) => (
          <button
            key={c}
            type="button"
            onClick={() => setColor(c)}
            className={`w-6 h-6 rounded-full ${COLOR_SWATCH[c]} ${color === c ? "ring-2 ring-offset-2 ring-offset-surface-900 ring-ink-100" : ""}`}
            aria-label={c}
          />
        ))}
      </div>
      <div className="flex gap-2">
        <button type="submit" disabled={submitting || !name.trim()} className="bg-accent-500 hover:bg-accent-400 disabled:opacity-50 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors">
          Create
        </button>
        <button type="button" onClick={onCancel} className="px-3 py-2 text-sm text-ink-500 hover:text-ink-300 transition-colors">
          Cancel
        </button>
      </div>
    </form>
  );
}
