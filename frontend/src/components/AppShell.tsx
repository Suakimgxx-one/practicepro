import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import type { User } from "@/types/recording";

interface AppShellProps {
  user: User;
  children: React.ReactNode;
}

function NavIcon({ path }: { path: string }) {
  return (
    <svg viewBox="0 0 20 20" fill="none" className="w-[18px] h-[18px]" strokeWidth="1.6">
      <path d={path} stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

const ICONS = {
  home: "M3 10.5 10 4l7 6.5M5 9v7h10V9",
  pieces: "M4 4.5h9.5a2 2 0 0 1 2 2V16H6a2 2 0 0 1-2-2V4.5ZM4 4.5A2 2 0 0 1 6 3h.5M6 13.5h9.5",
  folders: "M3 6.5a1.5 1.5 0 0 1 1.5-1.5H8l1.5 2H15a1.5 1.5 0 0 1 1.5 1.5v6A1.5 1.5 0 0 1 15 16H4.5A1.5 1.5 0 0 1 3 14.5v-8Z",
  settings:
    "M10 12.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5ZM16.4 12.4a1.4 1.4 0 0 0 .28 1.54l.05.05a1.7 1.7 0 1 1-2.4 2.4l-.05-.05a1.4 1.4 0 0 0-1.54-.28 1.4 1.4 0 0 0-.85 1.28v.13a1.7 1.7 0 0 1-3.4 0v-.07a1.4 1.4 0 0 0-.92-1.28 1.4 1.4 0 0 0-1.54.28l-.05.05a1.7 1.7 0 1 1-2.4-2.4l.05-.05a1.4 1.4 0 0 0 .28-1.54 1.4 1.4 0 0 0-1.28-.85h-.13a1.7 1.7 0 0 1 0-3.4h.07a1.4 1.4 0 0 0 1.28-.92 1.4 1.4 0 0 0-.28-1.54l-.05-.05a1.7 1.7 0 1 1 2.4-2.4l.05.05a1.4 1.4 0 0 0 1.54.28h.07a1.4 1.4 0 0 0 .85-1.28v-.13a1.7 1.7 0 0 1 3.4 0v.07a1.4 1.4 0 0 0 .85 1.28 1.4 1.4 0 0 0 1.54-.28l.05-.05a1.7 1.7 0 1 1 2.4 2.4l-.05.05a1.4 1.4 0 0 0-.28 1.54v.07a1.4 1.4 0 0 0 1.28.85h.13a1.7 1.7 0 0 1 0 3.4h-.07a1.4 1.4 0 0 0-1.28.85Z",
};

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: ICONS.home },
  { to: "/pieces", label: "My Pieces", icon: ICONS.pieces },
  { to: "/settings", label: "Settings", icon: ICONS.settings },
];

export function AppShell({ user, children }: AppShellProps) {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  return (
    <div className="min-h-screen bg-surface-950 text-ink-100 flex">
      <aside
        className={`${collapsed ? "w-[68px]" : "w-64"} shrink-0 border-r border-border-subtle bg-surface-900/60 backdrop-blur-xl flex flex-col transition-all duration-200`}
      >
        <div className="h-16 flex items-center px-4 gap-2.5 border-b border-border-subtle">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-accent-400 to-accent-600 shrink-0 shadow-glow" />
          {!collapsed && <span className="font-semibold text-[15px] tracking-tight">PracticePro</span>}
        </div>

        <div className="px-3 pt-4">
          <Link
            to="/pieces"
            className="flex items-center justify-center gap-2 w-full bg-accent-500 hover:bg-accent-400 text-white text-sm font-medium rounded-lg py-2.5 shadow-glow transition-colors"
          >
            <svg viewBox="0 0 20 20" fill="none" className="w-4 h-4" strokeWidth="2">
              <path d="M10 4v12M4 10h12" stroke="currentColor" strokeLinecap="round" />
            </svg>
            {!collapsed && "Start Practice"}
          </Link>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-0.5">
          {NAV_ITEMS.map((item) => {
            const active = item.to === "/" ? location.pathname === "/" : location.pathname.startsWith(item.to);
            return (
              <Link
                key={item.to}
                to={item.to}
                className={`flex items-center gap-3 px-2.5 py-2 rounded-lg text-sm transition-colors ${
                  active
                    ? "bg-surface-800 text-ink-100"
                    : "text-ink-500 hover:text-ink-300 hover:bg-surface-800/60"
                }`}
              >
                <NavIcon path={item.icon} />
                {!collapsed && item.label}
              </Link>
            );
          })}
        </nav>

        <div className="p-3 border-t border-border-subtle">
          <button
            onClick={() => setCollapsed((c) => !c)}
            className="w-full flex items-center gap-3 px-2.5 py-2 rounded-lg text-sm text-ink-500 hover:text-ink-300 hover:bg-surface-800/60 transition-colors mb-1"
          >
            <svg viewBox="0 0 20 20" fill="none" className="w-[18px] h-[18px]" strokeWidth="1.6">
              <path
                d={collapsed ? "M7 4 13 10l-6 6" : "M13 4 7 10l6 6"}
                stroke="currentColor"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            {!collapsed && "Collapse"}
          </button>
          <div className="flex items-center gap-2.5 px-2.5 py-2">
            <div className="w-7 h-7 rounded-full bg-surface-700 flex items-center justify-center text-xs font-medium shrink-0">
              {user.email[0].toUpperCase()}
            </div>
            {!collapsed && <span className="text-sm text-ink-300 truncate">{user.email}</span>}
          </div>
        </div>
      </aside>

      <main className="flex-1 min-w-0">{children}</main>
    </div>
  );
}
