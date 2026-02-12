"use client";

import Link from "next/link";
import { useAuthStore } from "@/stores/authStore";

export function Header() {
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200/80 bg-white/80 backdrop-blur">
      <div className="container h-16 flex items-center justify-between">
        <Link href="/" className="font-semibold text-xl tracking-tight" style={{ fontFamily: "var(--font-display)" }}>
          DevForge
        </Link>
        <nav className="flex items-center gap-5 text-sm text-slate-700">
          <Link href="/dashboard">Dashboard</Link>
          <Link href="/editor">Editor</Link>
          <Link href="/analytics">Analytics</Link>
          {user ? (
            <button onClick={logout} className="rounded-full bg-slate-900 text-white px-3 py-1.5">
              Logout
            </button>
          ) : (
            <Link href="/" className="rounded-full bg-slate-900 text-white px-3 py-1.5">
              Sign in
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
