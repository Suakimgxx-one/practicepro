import { Link } from "react-router-dom";
import { BarChart, Bar, XAxis, ResponsiveContainer, Tooltip } from "recharts";
import { useUser } from "@/hooks/useUser";
import { useDashboardData } from "@/hooks/useDashboardData";
import { useFolders } from "@/hooks/useFolders";
import { AppShell } from "@/components/AppShell";
import { EmailGate } from "@/components/EmailGate";

function formatMinutes(minutes: number): string {
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  const rest = minutes % 60;
  return rest > 0 ? `${hours}h ${rest}m` : `${hours}h`;
}

export function DashboardPage() {
  const { user, loading: userLoading, signIn } = useUser();
  const { data, loading } = useDashboardData(user?.id ?? null);
  const { folders } = useFolders(user?.id ?? null);

  if (userLoading) {
    return (
      <div className="min-h-screen bg-surface-950 flex items-center justify-center">
        <p className="text-ink-500 text-sm">Loading</p>
      </div>
    );
  }

  if (!user) return <EmailGate onSubmit={signIn} />;

  const pieceById = new Map((data?.pieces ?? []).map((p) => [p.id, p]));

  return (
    <AppShell user={user}>
      <div className="px-8 py-8 max-w-5xl">
        <header className="mb-8">
          <h1 className="text-2xl font-semibold tracking-tight mb-1">Welcome back</h1>
          <p className="text-ink-500 text-sm">{user.email}</p>
        </header>

        {loading || !data ? (
          <p className="text-ink-500 text-sm">Loading your practice data</p>
        ) : (
          <>
            {/* Stat row — all real, computed from actual practice sessions */}
            <div className="grid grid-cols-3 gap-4 mb-8">
              <div className="bg-surface-900/60 border border-border-subtle rounded-xl p-5">
                <p className="text-ink-500 text-xs mb-1.5">Practiced today</p>
                <p className="text-2xl font-semibold tabular-nums">{formatMinutes(data.minutesToday)}</p>
              </div>
              <div className="bg-surface-900/60 border border-border-subtle rounded-xl p-5">
                <p className="text-ink-500 text-xs mb-1.5">This week</p>
                <p className="text-2xl font-semibold tabular-nums">{formatMinutes(data.minutesThisWeek)}</p>
              </div>
              <div className="bg-surface-900/60 border border-border-subtle rounded-xl p-5">
                <p className="text-ink-500 text-xs mb-1.5">Current streak</p>
                <p className="text-2xl font-semibold tabular-nums">
                  {data.streakDays} day{data.streakDays === 1 ? "" : "s"}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-6">
              <div className="col-span-2 space-y-6">
                {/* Weekly activity */}
                <div className="bg-surface-900/60 border border-border-subtle rounded-xl p-5">
                  <h2 className="text-sm font-medium text-ink-300 mb-4">This week</h2>
                  <ResponsiveContainer width="100%" height={140}>
                    <BarChart data={data.weeklyActivity} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                      <XAxis dataKey="day" stroke="#5A5D6E" fontSize={11} tickLine={false} axisLine={false} />
                      <Tooltip
                        contentStyle={{
                          background: "#191B24",
                          border: "1px solid #2E313F",
                          borderRadius: 8,
                          fontSize: 12,
                          fontFamily: "Plus Jakarta Sans",
                        }}
                        formatter={(value: number) => [`${value}m`, "practiced"]}
                        cursor={{ fill: "#242631" }}
                      />
                      <Bar dataKey="minutes" fill="#7C6CF6" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Recent activity */}
                <div className="bg-surface-900/60 border border-border-subtle rounded-xl p-5">
                  <h2 className="text-sm font-medium text-ink-300 mb-4">Recent activity</h2>
                  {data.sessions.length === 0 ? (
                    <p className="text-sm text-ink-500">
                      No practice sessions yet — start one from a piece to see your activity here.
                    </p>
                  ) : (
                    <ul className="divide-y divide-border-subtle">
                      {data.sessions.slice(0, 6).map((s) => {
                        const piece = pieceById.get(s.piece_id);
                        return (
                          <li key={s.id} className="flex items-center justify-between py-2.5 text-sm">
                            <Link
                              to={`/pieces/${s.piece_id}`}
                              className="text-ink-100 hover:text-accent-400 transition-colors"
                            >
                              {piece?.title ?? "Untitled piece"}
                            </Link>
                            <span className="text-ink-500 tabular-nums">
                              {Math.round((s.duration_seconds ?? 0) / 60)}m ·{" "}
                              {new Date(s.started_at).toLocaleDateString(undefined, {
                                month: "short",
                                day: "numeric",
                              })}
                            </span>
                          </li>
                        );
                      })}
                    </ul>
                  )}
                </div>
              </div>

              <div className="space-y-6">
                {/* Folders quick access */}
                <div className="bg-surface-900/60 border border-border-subtle rounded-xl p-5">
                  <div className="flex items-center justify-between mb-3">
                    <h2 className="text-sm font-medium text-ink-300">Folders</h2>
                    <Link to="/pieces" className="text-xs text-accent-400 hover:text-accent-300 transition-colors">
                      View all
                    </Link>
                  </div>
                  {folders.length === 0 ? (
                    <p className="text-sm text-ink-500">No folders yet.</p>
                  ) : (
                    <ul className="space-y-2">
                      {folders.slice(0, 5).map((f) => (
                        <li key={f.id}>
                          <Link
                            to={`/pieces?folder=${f.id}`}
                            className="flex items-center justify-between text-sm text-ink-300 hover:text-ink-100 transition-colors"
                          >
                            <span>{f.name}</span>
                            <span className="text-ink-500 text-xs">{f.piece_count}</span>
                          </Link>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                {/* Pieces needing attention */}
                <div className="bg-surface-900/60 border border-border-subtle rounded-xl p-5">
                  <h2 className="text-sm font-medium text-ink-300 mb-3">Needs attention</h2>
                  {data.piecesNeedingAttention.length === 0 ? (
                    <p className="text-sm text-ink-500">Everything's been practiced recently.</p>
                  ) : (
                    <ul className="space-y-2">
                      {data.piecesNeedingAttention.slice(0, 5).map((p) => (
                        <li key={p.id}>
                          <Link
                            to={`/pieces/${p.id}`}
                            className="text-sm text-ink-300 hover:text-ink-100 transition-colors"
                          >
                            {p.title}
                          </Link>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </AppShell>
  );
}
