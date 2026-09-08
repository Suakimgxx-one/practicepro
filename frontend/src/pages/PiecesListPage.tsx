import { Link } from "react-router-dom";
import { useUser } from "@/hooks/useUser";
import { usePieces } from "@/hooks/usePieces";
import { createPiece } from "@/api/client";
import { EmailGate } from "@/components/EmailGate";
import { NewPieceForm } from "@/components/NewPieceForm";

export function PiecesListPage() {
  const { user, loading: userLoading, signIn } = useUser();
  const { pieces, loading: piecesLoading, refetch } = usePieces(user?.id ?? null);

  if (userLoading) {
    return (
      <div className="min-h-screen bg-paper flex items-center justify-center">
        <p className="text-ink-faint text-sm">Loading</p>
      </div>
    );
  }

  if (!user) {
    return <EmailGate onSubmit={signIn} />;
  }

  const handleCreate = async (title: string) => {
    await createPiece({ user_id: user.id, title });
    await refetch();
  };

  return (
    <div className="min-h-screen bg-paper text-ink px-6 py-14">
      <div className="max-w-xl mx-auto">
        <header className="mb-10">
          <h1 className="font-serif text-3xl mb-1">Your pieces</h1>
          <p className="text-ink-soft text-sm">{user.email}</p>
        </header>

        <div className="mb-10">
          <NewPieceForm onCreate={handleCreate} />
        </div>

        {piecesLoading ? (
          <p className="text-sm text-ink-faint">Loading</p>
        ) : pieces.length === 0 ? (
          <p className="text-sm text-ink-faint">
            Nothing here yet — add the first piece you're working on above.
          </p>
        ) : (
          <ul className="divide-y divide-line">
            {pieces.map((piece) => (
              <li key={piece.id}>
                <Link
                  to={`/pieces/${piece.id}`}
                  className="flex items-center justify-between py-4 group"
                >
                  <span className="font-serif text-lg group-hover:text-brass-dark transition-colors">
                    {piece.title}
                  </span>
                  <span className="text-ink-faint text-sm">
                    {new Date(piece.created_at).toLocaleDateString(undefined, {
                      month: "short",
                      day: "numeric",
                    })}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
