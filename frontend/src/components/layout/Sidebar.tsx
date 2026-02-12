"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const items = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/editor", label: "Portfolio Editor" },
  { href: "/analytics", label: "Analytics" },
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="glass rounded-2xl p-4">
      <ul className="space-y-2">
        {items.map((item) => {
          const active = pathname.startsWith(item.href);
          return (
            <li key={item.href}>
              <Link
                href={item.href}
                className={`block rounded-xl px-3 py-2 text-sm transition ${
                  active ? "bg-slate-900 text-white" : "hover:bg-slate-100 text-slate-700"
                }`}
              >
                {item.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </aside>
  );
}
