import { useUser } from "@/hooks/useUser";
import { AppShell } from "@/components/AppShell";
import { EmailGate } from "@/components/EmailGate";

export function SettingsPage() {
  const { user, loading, signIn } = useUser();

  if (loading) {
    return (
      <div className="min-h-screen bg-surface-950 flex items-center justify-center">
        <p className="text-ink-500 text-sm">Loading</p>
      </div>
    );
  }
  if (!user) return <EmailGate onSubmit={signIn} />;

  return (
    <AppShell user={user}>
      <div className="px-8 py-8 max-w-lg">
        <h1 className="text-2xl font-semibold tracking-tight mb-6">Settings</h1>
        <div className="bg-surface-900/60 border border-border-subtle rounded-xl p-5 mb-4">
          <p className="text-xs text-ink-500 mb-1">Account</p>
          <p className="text-sm text-ink-100">{user.email}</p>
        </div>
        <p className="text-sm text-ink-500">
          More settings — practice reminders, notification preferences, and account management — are planned but not built yet.
        </p>
      </div>
    </AppShell>
  );
}
