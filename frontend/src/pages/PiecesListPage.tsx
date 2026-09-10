import { useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useUser } from "@/hooks/useUser";
import { usePieces } from "@/hooks/usePieces";
import { useFolders } from "@/hooks/useFolders";
import { usePinnedPieces } from "@/hooks/usePinnedPieces";
import { createPiece, updatePiece } from "@/api/client";
import { AppShell } from "@/components/AppShell";
import { EmailGate } from "@/components/EmailGate";
import { NewPieceForm } from "@/components/NewPieceForm";
import { NewFolderForm } from "@/components/NewFolderForm";
import type { Piece } from "@/types/piece";

type SortMode = "recent" | "title";

const COLOR_DOT: Record<string, string> = {
  violet: "bg-accent-500",
  emerald: "bg-success",
  amber: "bg-warning",
  rose: "bg-danger",
  sky: "bg-sky-400",
};

function PieceRow({
  piece,
  pinned,
  onTogglePin,
}: {
  piece: Piece;
  pinned: boolean;
  onTogglePin: (id: string) => void;
}) {
  return (
    <div className="flex items-center justify-between py-3 flex-1 min-w-0 group">
      <Link to={`/pieces/${piece.id}`} className="flex-1 min-w-0">
        <p className="text-sm font-medium text-ink-100 group-hover:text-accent-400 transition-colors truncate">
          {piece.title}
        </p>
        {piece.composer && <p className="text-xs text-ink-500 mt-0.5">{piece.composer}</p>}
      </Link>
      <button
        onClick={() => onTogglePin(piece.id)}
        className={`text-xs px-2 transition-colors ${pinned ? "text-accent-400" : "text-ink-700 hover:text-ink-500"}`}
        aria-label={pinned ? "Unpin" : "Pin"}
      >
        ★
      </button>
    </div>
  );
}

export function PiecesListPage() {
  const { user, loading: userLoading, signIn } = useUser();
  const { pieces, loading: piecesLoading, refetch: refetchPieces } = usePieces(user?.id ?? null);
  const { folders, loading: foldersLoading, refetch: refetchFolders, create: createFolder, remove: removeFolder } =
    useFolders(user?.id ?? null);
  const { pinnedIds, toggle: togglePin } = usePinnedPieces();
  const [searchParams] = useSearchParams();
  const activeFolderId = searchParams.get("folder");

  const [search, setSearch] = useState("");
  const [sortMode, setSortMode] = useState<SortMode>("recent");
  const [showNewFolder, setShowNewFolder] = useState(false);
  const [confirmingDeleteId, setConfirmingDeleteId] = useState<string | null>(null);

  const filtered = useMemo(() => {
    let result = pieces;
    if (search.trim()) {
      const q = search.trim().toLowerCase();
      result = result.filter(
        (p) => p.title.toLowerCase().includes(q) || (p.composer ?? "").toLowerCase().includes(q)
      );
    }
    if (activeFolderId) {
      result = result.filter((p) => p.folder_id === activeFolderId);
    }
    const sorted = [...result].sort((a, b) => {
      if (sortMode === "title") return a.title.localeCompare(b.title);
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    });
    return sorted.sort((a, b) => Number(pinnedIds.has(b.id)) - Number(pinnedIds.has(a.id)));
  }, [pieces, search, sortMode, activeFolderId, pinnedIds]);

  if (userLoading) {
    return (
      <div className="min-h-screen bg-surface-950 flex items-center justify-center">
        <p className="text-ink-500 text-sm">Loading</p>
      </div>
    );
  }
  if (!user) return <EmailGate onSubmit={signIn} />;

  const handleCreatePiece = async (title: string) => {
    await createPiece({ user_id: user.id, title, folder_id: activeFolderId ?? undefined });
    await refetchPieces();
  };

  const handleMoveToFolder = async (pieceId: string, folderId: string | null) => {
    await updatePiece(pieceId, { folder_id: folderId });
    await refetchPieces();
    await refetchFolders();
  };

  const handleDeleteFolder = async (folderId: string) => {
    await removeFolder(folderId);
    setConfirmingDeleteId(null);
  };

  const unfiled = filtered.filter((p) => !p.folder_id);
  const activeFolder = folders.find((f) => f.id === activeFolderId);

  return (
    <AppShell user={user}>
      <div className="px-8 py-8 max-w-3xl">
        <header className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight mb-1">
              {activeFolder ? activeFolder.name : "My Pieces"}
            </h1>
            <p className="text-ink-500 text-sm">{user.email}</p>
          </div>
          {activeFolder && (
            <Link to="/pieces" className="text-sm text-ink-500 hover:text-ink-300 transition-colors">
              ← All pieces
            </Link>
          )}
        </header>

        <div className="mb-6">
          <NewPieceForm onCreate={handleCreatePiece} placeholder={activeFolder ? `Add a piece to ${activeFolder.name}` : undefined} />
        </div>

        <div className="flex items-center gap-3 mb-6">
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search pieces or composers"
            className="flex-1 bg-surface-900 border border-border-subtle focus:border-accent-500 rounded-lg px-3.5 py-2 text-sm outline-none transition-colors"
          />
          <select
            value={sortMode}
            onChange={(e) => setSortMode(e.target.value as SortMode)}
            className="bg-surface-900 border border-border-subtle rounded-lg px-3 py-2 text-sm text-ink-300 outline-none"
          >
            <option value="recent">Recently added</option>
            <option value="title">Title</option>
          </select>
        </div>

        {!activeFolderId && (
          <div className="mb-8">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-xs text-ink-500 uppercase tracking-wider">Folders</h2>
              <button onClick={() => setShowNewFolder((s) => !s)} className="text-xs text-accent-400 hover:text-accent-300 transition-colors">
                + New folder
              </button>
            </div>
            {showNewFolder && <NewFolderForm onCreate={createFolder} onCancel={() => setShowNewFolder(false)} />}
            {!foldersLoading && folders.length > 0 && (
              <ul className="space-y-0.5">
                {folders.map((f) => (
                  <li key={f.id} className="group flex items-center justify-between">
                    <Link to={`/pieces?folder=${f.id}`} className="flex items-center gap-2.5 py-2 text-sm text-ink-300 hover:text-ink-100 transition-colors">
                      <span className={`w-2 h-2 rounded-full ${COLOR_DOT[f.color] ?? "bg-accent-500"}`} />
                      {f.name}
                      <span className="text-ink-600 text-xs">{f.piece_count}</span>
                    </Link>
                    {confirmingDeleteId === f.id ? (
                      <div className="flex items-center gap-2 text-xs">
                        <span className="text-ink-500">Delete? Pieces stay, unfiled.</span>
                        <button onClick={() => handleDeleteFolder(f.id)} className="text-danger hover:text-red-400">Confirm</button>
                        <button onClick={() => setConfirmingDeleteId(null)} className="text-ink-500 hover:text-ink-300">Cancel</button>
                      </div>
                    ) : (
                      <button
                        onClick={() => setConfirmingDeleteId(f.id)}
                        className="opacity-0 group-hover:opacity-100 text-xs text-ink-600 hover:text-danger transition-opacity"
                      >
                        Delete
                      </button>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        <div>
          {!activeFolderId && <h2 className="text-xs text-ink-500 uppercase tracking-wider mb-2">All pieces</h2>}
          {(() => {
            const visible = activeFolderId ? filtered : unfiled;
            if (piecesLoading) {
              return <p className="text-sm text-ink-500">Loading</p>;
            }
            if (pieces.length === 0) {
              return <p className="text-sm text-ink-500">Nothing here yet — add the first piece you're working on above.</p>;
            }
            if (visible.length === 0 && search.trim()) {
              return <p className="text-sm text-ink-500">No pieces match "{search.trim()}".</p>;
            }
            if (visible.length === 0 && activeFolderId) {
              return <p className="text-sm text-ink-500">No pieces in this folder yet — add one above.</p>;
            }
            if (visible.length === 0) {
              return <p className="text-sm text-ink-500">Every piece is filed into a folder — browse folders above.</p>;
            }
            return (
              <ul className="divide-y divide-border-subtle">
                {visible.map((piece) => (
                  <li key={piece.id} className="flex items-center gap-2">
                    <PieceRow piece={piece} pinned={pinnedIds.has(piece.id)} onTogglePin={togglePin} />
                    {!activeFolderId && folders.length > 0 && (
                      <select
                        value=""
                        onChange={(e) => e.target.value && handleMoveToFolder(piece.id, e.target.value)}
                        className="text-xs bg-surface-900 border border-border-subtle rounded px-2 py-1 text-ink-500 outline-none"
                      >
                        <option value="">Move to…</option>
                        {folders.map((f) => (
                          <option key={f.id} value={f.id}>{f.name}</option>
                        ))}
                      </select>
                    )}
                  </li>
                ))}
              </ul>
            );
          })()}
        </div>
      </div>
    </AppShell>
  );
}
